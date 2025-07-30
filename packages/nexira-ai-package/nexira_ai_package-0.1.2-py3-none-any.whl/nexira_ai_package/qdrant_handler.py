from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.models import Distance, VectorParams, Filter, FieldCondition, MatchText, MatchValue
from typing import List, Optional, Dict, Any
import logging
import os
import markdown
from bs4 import BeautifulSoup
import hashlib
from .app_config import app_config
from sentence_transformers import SentenceTransformer
from flashrank import Ranker, RerankRequest
import pandas as pd
import re
import threading

class QdrantHandler:
    def __init__(self, collection_name: str):
        """Initialize Qdrant client."""
        self.client = None
        self.collection_name = collection_name
        self.vector_size = 768
        self.llm_model = SentenceTransformer("nomic-ai/nomic-embed-text-v1.5", trust_remote_code=True)
        self.reranker = Ranker(max_length=128)
        self.lock = threading.Lock()

    def get_embedding(self, text: str) -> List[float]:
        with self.lock:
            return self.llm_model.encode(text).tolist()

    def clear_collection(self, collection_name: Optional[str] = None):
        if not self.client:
            logging.error("❌ No Qdrant connection")
            return False

        try:
            collection = collection_name or self.collection_name
            self.client.delete_collection(collection_name=collection)
            logging.info(f"✅ Collection '{collection}' cleared successfully")
            return True
        except Exception as e:
            logging.error(f"❌ Error clearing collection: {e}")
            return False


    def connect_to_database(self):
        try:
            self.client = QdrantClient(
                url=app_config.QDRANT_URL,
                #api_key=app_config.QDRANT_API_KEY,
                prefer_grpc=False
            )
            logging.info("✅ Qdrant connection established")
            return True
        except Exception as e:
            logging.error(f"❌ Qdrant connection error: {e}")
            self.client = None
            return False

    def create_collection(self, collection_name: Optional[str] = None):
        print("create_collection")
        """Create a new collection in Qdrant."""
        if not self.client:
            logging.error("❌ No Qdrant connection")
            return False

        try:
            collection = collection_name or self.collection_name
            self.client.create_collection(
                collection_name=collection,
                vectors_config=VectorParams(
                    size=self.vector_size,
                    distance=Distance.COSINE
                )
            )
            logging.info(f"✅ Collection '{collection}' created successfully")
            return True
        except Exception as e:
            logging.error(f"❌ Error creating collection: {e}")
            return False

    def read_markdown_file(self, file_path: str) -> dict:
        """Read and parse markdown file content."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                images = re.findall(r'!\[[^\]]*\]\(.*\)', content)
                # Convert markdown to HTML
                html = markdown.markdown(content)
                # Extract text from HTML
                soup = BeautifulSoup(html, 'html.parser')
                text = soup.get_text()
                return {"text": text, "images": images}
        except Exception as e:
            logging.error(f"❌ Error reading file {file_path}: {e}")
            return {"text": "", "images": []}


    def generate_doc_id(self, filename: str, row_index: Optional[int] = None) -> int:
        """Generate a document ID from filename hash, optionally including a row index for uniqueness within a file."""
        identifier = filename
        if row_index is not None:
            identifier += f"_row_{row_index}"
        hash_object = hashlib.md5(identifier.encode())
        return int(hash_object.hexdigest(), 16) % 1000000  # Keep a consistent modulo

    def process_markdown_directory(self, directory_path: str, collection_name: Optional[str] = None) -> List[Dict]:
        points = []        
        for filename in os.listdir(directory_path):
            if filename.endswith('.md'):
                file_path = os.path.join(directory_path, filename)
                content = self.read_markdown_file(file_path)
                if content.get("text"):
                    doc_id = self.generate_doc_id(filename)
                    points.append({
                        "id": doc_id,
                        "vector": None,
                        "payload": {
                            "text": content.get("text"),
                            "images": content.get("images"),
                            "filename": filename,
                            "file_path": file_path,
                            "source_type": "markdown"
                        }
                    })
        return points

    def insert_markdown_directory(self, directory_path: str, collection_name: Optional[str] = None, topic: str = "") -> bool:
        if not self.client:
            logging.error("❌ No Qdrant connection")
            return False

        if not os.path.exists(directory_path):
            logging.error(f"❌ Directory {directory_path} does not exist")
            return False

        try:
            points = self.process_markdown_directory(directory_path, collection_name)
            logging.info(f"✅ Found {len(points)} markdown files to process")
            success = True
            for point in points:
                if self.does_point_exist(point["payload"]["file_path"], collection_name):
                    logging.info(f"✅ Document already exists: {point['payload']['filename']}")
                    continue

                if not self.save_text_to_qdrant(
                    id=point["id"],
                    text=point["payload"]["text"],
                    metadata={
                        "filename": point["payload"]["filename"],
                        "file_path": point["payload"]["file_path"],
                        "source_type": "markdown",
                        "tags": topic,
                        "images": point["payload"]["images"]
                    },
                    collection_name=collection_name
                ):
                    success = False
                    logging.error(f"❌ Failed to insert document: {point['payload']['filename']}")
                else:
                    logging.info(f"✅ Successfully inserted document: {point['payload']['filename']}")

            return success
        except Exception as e:
            logging.error(f"❌ Error processing markdown directory: {e}")
            return False

    def read_csv_file(self, file_path: str) -> Optional[pd.DataFrame]:
        try:
            df = pd.read_csv(file_path)
            logging.info(f"✅ Successfully read CSV file: {file_path}")
            return df
        except FileNotFoundError:
            logging.error(f"❌ CSV file not found: {file_path}")
            return None
        except pd.errors.EmptyDataError:
            logging.error(f"❌ CSV file is empty: {file_path}")
            return None
        except Exception as e:
            logging.error(f"❌ Error reading CSV file {file_path}: {e}")
            return None

    def process_csv_directory(self, directory_path: str, collection_name: Optional[str] = None) -> List[Dict]:
        points = []
        if not os.path.exists(directory_path):
            logging.error(f"❌ CSV directory not found: {directory_path}")
            return points

        expected_columns = ['text', 'title', 'description', 'ingredients', 'directions', 'price', 'image', 'url']
        
        for filename in os.listdir(directory_path):
            if filename.lower().endswith('.csv'):
                file_path = os.path.join(directory_path, filename)
                df = self.read_csv_file(file_path)
                
                if df is not None:
                    # Normalize column names (e.g., lowercase and replace spaces with underscores)
                    df.columns = [col.lower().replace(' ', '_') for col in df.columns]
                    
                    if 'text' not in df.columns:
                        logging.warning(f"⚠️ Skipping CSV file {filename}: 'text' column not found.")
                        continue

                    for index, row in df.iterrows():
                        main_text = row.get('text')
                        if not main_text or (isinstance(main_text, float) and pd.isna(main_text)): # Check for NaN in text
                            logging.warning(f"⚠️ Skipping row {index} in {filename}: 'text' column is empty or NaN.")
                            continue

                        doc_id = self.generate_doc_id(filename, index) # Pass filename and row_index
                        
                        payload_metadata = {"filename": filename, "row_index": index, "source_type": "csv"}
                        for col in expected_columns:
                            if col != 'text': # 'text' is primary content, not metadata in this context
                                payload_metadata[col] = row.get(col) if col in df.columns else None
                        
                        points.append({
                            "id": doc_id,
                            "vector": None,  # Will be set by save_text_to_qdrant
                            "payload": {
                                "text": str(main_text), # Ensure text is string
                                **payload_metadata 
                            }
                        })
        return points

    def insert_csv_directory(self, directory_path: str, collection_name: Optional[str] = None) -> bool:
        if not self.client:
            logging.error("❌ No Qdrant connection for CSV insertion")
            return False

        if not os.path.exists(directory_path):
            logging.error(f"❌ CSV directory {directory_path} does not exist")
            return False

        try:
            points_to_insert = self.process_csv_directory(directory_path, collection_name)
            if not points_to_insert:
                logging.info("ℹ️ No CSV data found or processed.")
                return True # No data to insert can be considered a success in some contexts

            logging.info(f"✅ Found {len(points_to_insert)} data points from CSV files to process")
            
            all_successful = True
            for point_data in points_to_insert:
                doc_id = point_data["id"]
                text_content = point_data["payload"]["text"]
                # Prepare metadata by excluding 'text' if it was inadvertently included
                metadata = {k: v for k, v in point_data["payload"].items() if k != 'text'}

                if not self.save_text_to_qdrant(
                    id=doc_id,
                    text=text_content,
                    metadata=metadata,
                    collection_name=collection_name
                ):
                    all_successful = False
                    logging.error(f"❌ Failed to insert document ID {doc_id} from CSV: {metadata.get('filename', '')} (Row {metadata.get('row_index', '')})")
                else:
                    logging.info(f"✅ Successfully inserted document ID {doc_id} from CSV: {metadata.get('filename', '')} (Row {metadata.get('row_index', '')})")
            
            if all_successful:
                logging.info("✅ All CSV data processed and inserted successfully.")
            else:
                logging.warning("⚠️ Some CSV data points failed to insert. Check logs for details.")
            return all_successful
            
        except Exception as e:
            logging.error(f"❌ Error processing CSV directory for Qdrant: {e}")
            return False

    def does_point_exist(self, file_path: str, collection_name: Optional[str] = None) -> bool:
        if not self.client:
            logging.error("❌ No Qdrant connection")
            return False

        try:
            collection = collection_name or self.collection_name
            results, _ = self.client.scroll(
                collection_name=collection,
                scroll_filter=Filter(
                    must=[
                        FieldCondition(
                            key="file_path",
                            match=MatchValue(value=file_path)
                        )
                    ]
                ),
                limit=1
            )
            return len(results) > 0
        except Exception as e:
            logging.error(f"❌ Error checking if point exists for file_path {file_path}: {e}")
            return False

    def insert_vectors(self, points: List[Dict[str, Any]], collection_name: Optional[str] = None) -> bool:
        if not self.client:
            logging.error("❌ No Qdrant connection")
            return False

        try:
            collection = collection_name or self.collection_name
            self.client.upsert(
                collection_name=collection,
                points=points
            )
            logging.info(f"✅ Successfully inserted {len(points)} vectors")
            return True
        except Exception as e:
            logging.error(f"❌ Error inserting vectors: {e}")
            return False

    def search_vectors(self, query_vector: List[float], limit: int = 10, search_filter: str = "",
                       collection_name: Optional[str] = None,
                       score_threshold: Optional[float] = None) -> List[Dict[str, Any]]:
        if not self.client:
            logging.error("❌ No Qdrant connection")
            return []

        try:
            collection = collection_name or self.collection_name
            search_params = {}
            if score_threshold is not None:
                search_params["score_threshold"] = score_threshold

            query_filter = None
            if search_filter:
                query_filter = Filter(
                    must=[
                        FieldCondition(
                            key="tags",
                            match=MatchText(text=search_filter)
                        )
                    ]
                )
            results = self.client.search(
                collection_name=collection,
                query_vector=query_vector,
                limit=limit,
                query_filter=query_filter,
                **search_params
            )

            return [{
                "id": result.id,
                "score": result.score,
                "payload": result.payload
            } for result in results]

        except Exception as e:
            logging.error(f"❌ Error searching vectors: {e}")
            return []

    def delete_vectors(self, point_ids: List[int], collection_name: Optional[str] = None) -> bool:
        if not self.client:
            logging.error("❌ No Qdrant connection")
            return False

        try:
            collection = collection_name or self.collection_name
            self.client.delete(
                collection_name=collection,
                points_selector=models.PointIdsList(points=point_ids)
            )
            logging.info(f"✅ Successfully deleted {len(point_ids)} vectors")
            return True
        except Exception as e:
            logging.error(f"❌ Error deleting vectors: {e}")
            return False

    def get_collection_info(self, collection_name: Optional[str] = None) -> Dict[str, Any]:
        if not self.client:
            logging.error("❌ No Qdrant connection")
            return {}

        try:
            collection = collection_name or self.collection_name
            info = self.client.get_collection(collection_name=collection)
            return {
                "name": info.name,
                "vector_size": info.vectors_config.size,
                "distance": info.vectors_config.distance,
                "points_count": info.points_count
            }
        except Exception as e:
            logging.error(f"❌ Error getting collection info: {e}")
            return {}

    def save_text_to_qdrant(self, id: int, text: str, metadata: dict = {}, collection_name: Optional[str] = None) -> bool:
        vector = self.get_embedding(text)
        return self.insert_vectors([{
            "id": id,
            "vector": vector,
            "payload": {
                "text": text,
                **metadata
            }
        }], collection_name)

    def search_similar_texts(self, query: str, limit: int = 7, search_filter: str = "") -> List[Dict[str, Any]]:
        """
        Search Qdrant for texts similar to the input query and rerank them using a reranker.

        Args:
            query (str): The user query for similarity search.
            limit (int): Number of initial candidates to retrieve. Default is 7.

        Returns:
            List[Dict[str, Any]]: Reranked list of documents with score, id, payload, and text.
        """
        # Step 1: Embed the query
        query_vector = self.get_embedding(query)

        # Step 2: Search vector DB
        results = self.search_vectors(query_vector=query_vector, limit=limit, search_filter=search_filter)
        if not results:
            return []

        # Step 3: Format results into reranker-friendly format
        passages = [
            {
                "id": str(doc["id"]),
                "text": doc["payload"]["text"],
                "meta": {k: v for k, v in doc["payload"].items() if k != "text"}
            }
            for doc in results
        ]

        # Step 4: Run reranking
        rerank_request = RerankRequest(query=query, passages=passages)
        reranked = self.reranker.rerank(rerank_request)
        reranked = reranked[0:5]
        # Step 5: Format output
        final_results = [
            {
                "score": item.get("score"),
                "id": item.get("id"),
                "text": item.get("text"),
                "payload": item.get("meta", {})
            }
            for item in reranked
        ]
        return final_results


    def close_connection(self):
        if self.client:
            self.client.close()
            self.client = None
            logging.info("🔒 Qdrant connection closed")
        else:
            logging.info("ℹ️ No active Qdrant connection to close")

    def __del__(self):
        self.close_connection()
