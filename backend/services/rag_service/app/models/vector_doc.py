from sqlalchemy import Column, Integer, JSON, Text
from pgvector.sqlalchemy import Vector

from .base import Base, SchemaMixin

class DocumentChunk(Base, SchemaMixin):
    __tablename__ = "document_chunks"

    id = Column(Integer, primary_key=True)
    content = Column(Text, nullable=False)
    # Kích thước embedding của Gemini (text-embedding-004) là 768
    embedding = Column(Vector(768)) 
    chunk_metadata = Column(JSON) # Lưu thông tin meta như source_url, program_id, university_name...
