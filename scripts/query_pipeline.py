import logging
from pathlib import Path
from system_prompt import system_prompt
from local_generate import local_generate
from query_chunks import get_top_k_similar_chunks


logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger()


def run_query(question, k=5):
    try:
        top_chunks_df = get_top_k_similar_chunks(question, k=k)
        top_chunks = top_chunks_df.to_dict(orient="records")
        prompt = system_prompt(top_chunks, question)
        response = local_generate(prompt)
        logger.info("Response generated.")
        return response
    except Exception as e:
        logger.exception(f"Query failed: {str(e)}")
        raise

if __name__ == "__main__":
    question = "Give me insights about the Education Loan, is the demand for such loans increasing every year? Whats the general trend happening?"
    answer = run_query(question)
    print("Answer:\n")
    print(answer)
