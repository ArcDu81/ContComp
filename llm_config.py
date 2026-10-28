import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from tenacity import retry, wait_exponential, stop_after_attempt
from schema import ChunkExtraction, FinalSummary

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# 1. Map Model: Gemini 3.8 Flash
map_llm = ChatGoogleGenerativeAI(
    model="gemini-3.8-pro",
    temperature=0.0,
    api_key=GOOGLE_API_KEY
)
structured_map_llm = map_llm.with_structured_output(ChunkExtraction)

# 2. Reduce Model: Gemini 3.8 Flash
reduce_llm = ChatGoogleGenerativeAI(
    model="gemini-3.8-pro",
    temperature=0.2,
    api_key=GOOGLE_API_KEY
)
structured_reduce_llm = reduce_llm.with_structured_output(FinalSummary)

# Bulletproof Retry Logic: 
# If Google throws a rate limit, this pauses the script for 10 seconds, then 20s, up to 5 times.
@retry(
    wait=wait_exponential(multiplier=5, min=10, max=60), 
    stop=stop_after_attempt(5)
)
def extract_chunk_with_retry(prompt_messages):
    return structured_map_llm.invoke(prompt_messages)