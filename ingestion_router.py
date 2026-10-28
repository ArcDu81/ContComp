import uuid
import datetime
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

class DocumentIngestor:
    def __init__(self, file_path: str, user_id: str = "default_user"):
        self.file_path = file_path
        self.user_id = user_id
        # Splitter targets ~3000 tokens to stay well within Groq limits
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=80000, # Approx 3000 tokens
            chunk_overlap=4000 # Approx 300 tokens overlap to preserve context edges
        )
    
    def process(self):
        # Generate Metadata
        now = datetime.datetime.now()
        metadata = {
            "uuid": str(uuid.uuid4()),
            "user_id": self.user_id,
            "created_date": now.strftime("%Y-%m-%d"),
            "created_day": now.strftime("%A"),
            "created_time": now.strftime("%H:%M:%S")
        }
        
        # Load File
        if self.file_path.endswith(".pdf"):
            loader = PyPDFLoader(self.file_path)
            docs = loader.load()
            raw_text = "\n".join([doc.page_content for doc in docs])
        else:
            with open(self.file_path, "r", encoding="utf-8") as f:
                raw_text = f.read()
                
        # Chunk Text
        chunks = self.text_splitter.split_text(raw_text)
        
        return {
            "metadata": metadata,
            "raw_text": raw_text,
            "chunks": chunks
        }