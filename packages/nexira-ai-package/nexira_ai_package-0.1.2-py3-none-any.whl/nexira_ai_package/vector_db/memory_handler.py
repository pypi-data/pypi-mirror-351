from nexira_ai_package.qdrant_handler import QdrantHandler
import logging
import markdown
from bs4 import BeautifulSoup
import io
from PyPDF2 import PdfReader
import docx
from nexira_ai_package.vector_db.data_parser import DataParser
from langgraph.prebuilt import create_react_agent
from langchain_core.tools import tool
from nexira_ai_package.llm_model import Model
from importlib.resources import files

class MemoryHandler(QdrantHandler):
    def __init__(self, collection_name: str):
        super().__init__(collection_name)
    
    def initialise_collection(self):
        self.create_collection(self.collection_name)
        self.agent_mini_mavia = self.create_llm_agent(0)
        self.agent_block_clans = self.create_llm_agent(1)
        max_iterations = 3
        recursion_limit = 1 * max_iterations + 1
        self.recursion = {"recursion_limit": recursion_limit}

    def get_qdrant_search_tool(self):        
        @tool("mini_mavia_search_tool", parse_docstring=True)
        def mini_mavia_search_tool(query: str, limit: int = 5) -> list[str]:
            """Search Qdrant for relevant document chunks for Mini Mavia.

            Args:
                query: The search query string.
                limit: Number of results to return (default: 5).

            Returns:
                A list of relevant information for the query on Mini Mavia.
            """
            results = self.search_similar_texts(query, limit, "Mini Mavia")
            tool_results = []
            for doc in results:
                text = doc["text"]
                images = doc["payload"]["images"] if "images" in doc["payload"] else []
                text += "\n\n" + "\n".join(images)
                tool_results.append(text)
            return tool_results

        @tool("block_clans_search_tool", parse_docstring=True)
        def block_clans_search_tool(query: str, limit: int = 5) -> list[str]:
            """Search Qdrant for relevant document chunks for Block Clans.

            Args:
                query: The search query string.
                limit: Number of results to return (default: 5).

            Returns:
                A list of relevant information for the query on Block Clans.
            """
            results = self.search_similar_texts(query, limit, "Block Clans")
            tool_results = []
            for doc in results:
                text = doc["text"]
                images = doc["payload"]["images"] if "images" in doc["payload"] else []
                text += "\n\n" + "\n".join(images)
                tool_results.append(text)
            return tool_results
        return [mini_mavia_search_tool, block_clans_search_tool]

    def insert_nexira_document(self):
        pdf_folder = files("nexira_ai_package.vector_db") / "nexira_docs"
        output_folder = pdf_folder / "dataset"
        output_folder.mkdir(exist_ok=True)
        parser = DataParser()
        md_paths = parser.process_folder(pdf_folder, output_folder)

        for path, topic in md_paths:
            print(f"Inserting {path} with topic {topic}")
            self.insert_markdown_directory(path, self.collection_name, topic)

    # Agent type 0: Mini Mavia
    # Agent type 1: Block Clans
    def create_llm_agent(self, agent_type: int):
        if agent_type == 0:
            tools = [self.get_qdrant_search_tool()[0]]
        elif agent_type == 1:
            tools = [self.get_qdrant_search_tool()[1]]
        else:
            tools = self.get_qdrant_search_tool()

        tool_names = "and".join([tool.name for tool in tools])
        system_prompt =f"""
        You are a helpful assistant who answers questions using relevant document content retrieved via tools.
        Use the {tool_names} to retrieve document chunks related to the query.
        Base your answer on the retrieved content, citing specific details where relevant.
        """

        llm_model = Model(system_prompt)
        agent = create_react_agent(
            llm_model.llm_model,
            tools=tools,
            prompt=system_prompt
        )
        return agent

    def call_llm_streaming(self, query: str, agent_type: int) -> list[str]:
        messages = {"messages": [{"role": "user", "content": query}]}
        agent = self.agent_mini_mavia if agent_type == 0 else self.agent_block_clans
        chunks = []
        for chunk in agent.stream(messages, self.recursion, stream_mode="updates"):
            chunks.append(chunk)
        return chunks
        
    def call_llm(self, query: str, agent_type: int) -> str:
        agent = self.agent_mini_mavia if agent_type == 0 else self.agent_block_clans
        messages = {"messages": [{"role": "user", "content": query}]}
        response = agent.invoke(messages, self.recursion)
        return response["messages"][-1].content

    def call_tool(self, query: str, agent_type: int):
        tools = self.get_qdrant_search_tool()[agent_type]
        return tools(query)

    def insert_document(self, file_bytes: bytes, file_name: str, metadata: dict):
        file_name = file_name.lower()

        handlers = {
            ".md": self.insert_markdown,
            ".txt": self.insert_text,
            ".pdf": self.insert_pdf,
            ".docx": self.insert_docx,
            ".csv": self.insert_csv,
            ".xlsx": self.insert_xlsx
        }

        for ext, handler in handlers.items():
            if file_name.endswith(ext):
                return handler(file_bytes, file_name, metadata)


    def insert_text(self, file_bytes: bytes, file_name: str, metadata: dict):
        try:
            text = file_bytes.decode("utf-8")
            self.save_text_to_qdrant(
                id=self.generate_doc_id(file_name),
                text=text,
                metadata=metadata
            )
            return True
        except Exception as e:
            logging.error(f"❌ Error processing plain text file: {e}")
            return False

    def insert_markdown(self, file_bytes: bytes, file_name: str, metadata: dict):
        try:
            content = file_bytes.decode("utf-8")
            html = markdown.markdown(content)
            text = BeautifulSoup(html, "html.parser").get_text()

            self.save_text_to_qdrant(
                id=self.generate_doc_id(file_name),
                text=text,
                metadata=metadata
            )
            return True
        except Exception as e:
            logging.error(f"❌ Error processing markdown file: {e}")
            return False

    def insert_pdf(self, file_bytes: bytes, file_name: str, metadata: dict):
        try:
            pdf_reader = PdfReader(io.BytesIO(file_bytes))
            full_text = "\n".join(page.extract_text() for page in pdf_reader.pages if page.extract_text())

            self.save_text_to_qdrant(
                id=self.generate_doc_id(file_name),
                text=full_text,
                metadata=metadata
            )
            return True
        except Exception as e:
            logging.error(f"❌ Error processing PDF file: {e}")
            return False

    def insert_docx(self, file_bytes: bytes, file_name: str, metadata: dict):
        try:
            doc = docx.Document(io.BytesIO(file_bytes))
            full_text = "\n".join([p.text for p in doc.paragraphs if p.text.strip()])

            self.save_text_to_qdrant(
                id=self.generate_doc_id(file_name),
                text=full_text,
                metadata=metadata
            )
            return True
        except Exception as e:
            logging.error(f"❌ Error processing DOCX file: {e}")
            return False
