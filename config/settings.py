import os
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
SERPER_API_KEY = os.getenv("SERPER_API_KEY")
LLM_MODEL = os.getenv("LLM_MODEL", "openrouter/nvidia/nemotron-3-super-120b-a12b:free")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

#Project Configurations
PROJECT_NAME = "Personal Research and Report Generations Crew"
VERSION = "1.0.0"

#Output Configurations
OUTPUT_DIR = "output"
REPORTS_DIR = f"{OUTPUT_DIR}/reports"
RAW_DATA_DIR = f"{OUTPUT_DIR}/raw"

#Agent Configurations
MAX_ITERATIONS = 10 #max reasoning steps for each agents
MAX_RPM = 10 #mas requests/minutes
VERBOSE = True #show agent reasoning in terminal

#Memoory Configurations
CHROMA_DB_PATH = "./memory/chroma_db"
COLLECTION_NAME = "research_memory"

#Validations
def validate_settings() -> None:
    """
    Checks that all required API keys are present.
    Raises an error early so you know immediately if something is missing,
    rather than failing halfway through crew run.
    """
    missing = []

    if not OPENROUTER_API_KEY:
        missing.append("OPENROUTER_API_KEY")
    if not SERPER_API_KEY:
        missing.append("SERPER_API_KEY")

    if missing:
        raise ValueError(f"Missing required environment variables: {', '.join(missing)}\n"
                         f"Please check your .env file."
                         )

if __name__ == "__main__":
    validate_settings()
    print("-- Setting Loaded Successfully --")
    print(f" Model: {LLM_MODEL}")
    print(f" Project: {PROJECT_NAME}")
    print(f" Version: {VERSION}")

