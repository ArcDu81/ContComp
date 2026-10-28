import streamlit as st
import os
import tempfile
from ingestion_router import DocumentIngestor
from agent_graph import app as agent_app

# Set up the page
st.set_page_config(page_title="CntCmp : Agentic Context Compressor", page_icon="🗜️", layout="wide")

st.title("ContComp : Agentic Context Compressor")
st.markdown("Upload large text files or PDFs to extract a dense, highly structured Markdown context using a LangGraph Map-Reduce pipeline.")

# File uploader
uploaded_file = st.file_uploader("Upload a document (.txt or .pdf)", type=["txt", "pdf"])

if uploaded_file is not None:
    if st.button("Run Compression Pipeline"):
        # UI Spinner during execution
        with st.spinner("Processing document... This may take a few minutes for large files depending on API rate limits."):
            
            # 1. Save the uploaded file locally so the Ingestor can read it
            file_extension = uploaded_file.name.split('.')[-1]
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_extension}") as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                temp_filepath = tmp_file.name
            
            try:
                # 2. Ingest and Chunk
                ingestor = DocumentIngestor(temp_filepath, user_id="streamlit_user")
                doc_data = ingestor.process()
                
                st.info(f"Document ingested and split into {len(doc_data['chunks'])} massive chunks. Starting Agent graph...")
                
                # 3. Execute LangGraph Pipeline
                config = {"configurable": {"thread_id": doc_data["metadata"]["uuid"]}}
                
                final_state = agent_app.invoke(
                    {
                        "metadata": doc_data["metadata"],
                        "raw_text": doc_data["raw_text"],
                        "chunks": doc_data["chunks"]
                    },
                    config=config
                )
                
                # 4. Display Results
                md_filename = f"{doc_data['metadata']['uuid']}.md"
                st.success("Compression Complete!")
                
                # Read the generated markdown
                with open(md_filename, "r", encoding="utf-8") as f:
                    md_content = f.read()
                    
                # Download Button
                st.download_button(
                    label="⬇️ Download Markdown Report",
                    data=md_content,
                    file_name=md_filename,
                    mime="text/markdown"
                )
                
                # Visual Preview
                st.markdown("---")
                st.markdown("### Report Preview")
                st.markdown(md_content)
                
            except Exception as e:
                st.error(f"Pipeline Failed: {e}")
                
            finally:
                # Cleanup the temporary uploaded file from the system
                if os.path.exists(temp_filepath):
                    os.remove(temp_filepath)