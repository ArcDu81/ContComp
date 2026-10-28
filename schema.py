from pydantic import BaseModel, Field
from typing import List

class Entity(BaseModel):
    name: str = Field(description="The normalized name of the entity.")
    type: str = Field(description="The type of entity (e.g., Person, Organization, Concept).")
    description: str = Field(description="A brief description of the entity.")

class Relationship(BaseModel):
    source_entity: str = Field(description="The name of the origin entity.")
    target_entity: str = Field(description="The name of the destination entity.")
    description: str = Field(description="How the source and target entities are connected.")

class ChunkExtraction(BaseModel):
    """The expected output from Groq for a single text chunk."""
    entities: List[Entity] = Field(default_factory=list, description="All entities found in the chunk.")
    relationships: List[Relationship] = Field(default_factory=list, description="All relationships between entities found in the chunk.")
    major_details: List[str] = Field(default_factory=list, description="Critical facts, plot points, or core arguments.")
    minor_details: List[str] = Field(default_factory=list, description="Nuances, dates, specific metrics, or supporting facts.")

class FinalSummary(BaseModel):
    """The final structured JSON from Gemini before Markdown formatting."""
    central_idea: str = Field(description="Strictly a 1-line overarching summary of the entire document.")
    deduplicated_entities: List[Entity] = Field(description="A clean, deduplicated list of all entities.")
    merged_relationships: List[Relationship] = Field(description="A clean, deduplicated list of relationships.")
    synthesized_major_details: List[str] = Field(description="Synthesized major details from across all chunks.")
    synthesized_minor_details: List[str] = Field(description="Synthesized minor details from across all chunks.")