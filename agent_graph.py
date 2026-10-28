import yaml
import operator
from typing import Annotated, List, TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.types import Send
from ingestion_router import DocumentIngestor
from llm_config import extract_chunk_with_retry, structured_reduce_llm
from persistence import get_checkpointer

# Load Prompts
with open("prompts.yaml", "r") as file:
    prompts = yaml.safe_load(file)

# Define Graph States
class OverallState(TypedDict):
    metadata: dict
    raw_text: str
    chunks: List[str]
    # operator.add ensures that parallel map nodes append to the list rather than overwrite
    extracted_data: Annotated[List[dict], operator.add]
    final_markdown: str

class MapState(TypedDict):
    chunk: str

# Node 1: Fan-out Logic (Send API)
def continue_to_map(state: OverallState):
    """Dynamically creates a parallel Map node for every chunk."""
    return [Send("extract_node", {"chunk": chunk}) for chunk in state["chunks"]]

# Node 2: Map / Extract
def extract_node(state: MapState):
    prompt = prompts["map_prompt"].format(chunk=state["chunk"])
    structured_json = extract_chunk_with_retry(prompt)
    # Return as list to satisfy the Annotated operator.add reducer
    return {"extracted_data": [structured_json.model_dump()]}

# Node 3: Reduce / Synthesize & Format MD
def synthesis_node(state: OverallState):
    prompt = prompts["reduce_prompt"].format(extracted_data=state["extracted_data"])
    final_json = structured_reduce_llm.invoke(prompt)
    
    # Format into the final Markdown string
    md_content = f"""# Document Compression Report
**Central Idea:** {final_json.central_idea}

## Metadata
* **UUID:** {state['metadata']['uuid']}
* **User ID:** {state['metadata']['user_id']}
* **Created:** {state['metadata']['created_date']} ({state['metadata']['created_day']}) at {state['metadata']['created_time']}

---

## Entities
"""
    for ent in final_json.deduplicated_entities:
        md_content += f"* **{ent.name}** ({ent.type}): {ent.description}\n"

    md_content += "\n## Relationships\n"
    for rel in final_json.merged_relationships:
        md_content += f"* **{rel.source_entity}** → **{rel.target_entity}**: {rel.description}\n"

    md_content += "\n## Major Details\n"
    for detail in final_json.synthesized_major_details:
        md_content += f"* {detail}\n"

    md_content += "\n## Minor Details\n"
    for detail in final_json.synthesized_minor_details:
        md_content += f"* {detail}\n"

    # Save to disk
    filename = f"{state['metadata']['uuid']}.md"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(md_content)
        
    return {"final_markdown": md_content}

# Compile Graph
workflow = StateGraph(OverallState)
workflow.add_node("extract_node", extract_node)
workflow.add_node("synthesis_node", synthesis_node)

workflow.add_conditional_edges(START, continue_to_map)
workflow.add_edge("extract_node", "synthesis_node")
workflow.add_edge("synthesis_node", END)

checkpointer = get_checkpointer()
app = workflow.compile(checkpointer=checkpointer)

if __name__ == "__main__":
    # Example Execution
    ingestor = DocumentIngestor("complex_test_file.txt", user_id="admin_01")
    doc_data = ingestor.process()
    
    # Provide the thread ID for Supabase Checkpointer to track state
    config = {"configurable": {"thread_id": doc_data["metadata"]["uuid"]}}
    
    print(f"Processing {len(doc_data['chunks'])} chunks in parallel...")
    final_state = app.invoke(
        {
            "metadata": doc_data["metadata"],
            "raw_text": doc_data["raw_text"],
            "chunks": doc_data["chunks"]
        },
        config=config
    )
    
    print(f"Successfully compiled markdown: {doc_data['metadata']['uuid']}.md")