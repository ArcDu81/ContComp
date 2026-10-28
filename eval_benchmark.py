import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

eval_llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    temperature=0.0,
    api_key=GOOGLE_API_KEY
)

def run_benchmark(raw_file_path: str, md_file_path: str):
    with open(raw_file_path, "r", encoding="utf-8") as f:
        raw_text = f.read()
    with open(md_file_path, "r", encoding="utf-8") as f:
        md_text = f.read()

    # Step 1: Generate questions from the RAW text
    question_prompt = f"""Based on the following text, generate 10 highly specific factual questions. 
    5 about entity relationships, 5 about minor supporting details. Output ONLY the questions, one per line.
    Text: {raw_text[:50000]}...""" # Truncated for prompt safety in baseline generation
    
    questions = eval_llm.invoke(question_prompt).content
    
    # Step 2: Answer using RAW text (Baseline)
    baseline_prompt = f"Answer these questions strictly based on the provided text.\nQuestions:\n{questions}\nText:\n{raw_text}"
    baseline_answers = eval_llm.invoke(baseline_prompt).content
    
    # Step 3: Answer using COMPRESSED text (Agent)
    agent_prompt = f"Answer these questions strictly based on the provided text.\nQuestions:\n{questions}\nText:\n{md_text}"
    agent_answers = eval_llm.invoke(agent_prompt).content
    
    # Step 4: Grade
    grade_prompt = f"""You are a grader. Compare the Agent's Answers to the Baseline Answers. 
    Calculate the percentage of questions the Agent answered correctly with the same factual accuracy as the Baseline.
    
    Baseline Answers:
    {baseline_answers}
    
    Agent Answers:
    {agent_answers}
    
    Output a short scorecard ending with: 'Context Retention: X%'"""
    
    scorecard = eval_llm.invoke(grade_prompt).content
    print("\n--- BENCHMARK SCORECARD ---")
    print(scorecard)

if __name__ == "__main__":
    # Ensure you replace these with your actual output file names
    # run_benchmark("sample_large_text.txt", "your-generated-uuid.md")
    pass