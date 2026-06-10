from crewai import Crew, Process
from oauthlib.oauth2.rfc6749.parameters import parse_token_response
from pandas.io.clipboard import paste

from memory.vectorStore import ResearchMemory
from workflows.researchWorkflow import create_research_tasks
from config.settings import validate_settings, VERBOSE
from utils.logger import get_logger
from utils.helpers import ensure_directories

logger = get_logger(__name__)

def run_research_crew(topic: str) -> str:
    """
    Main entry point for running the research crew.
    Takes a topic string and returns the final report as a string.

    Now includes memory - check past research before starting
    Args:
        topic: The research topic ton investigate.

    returns:
        str: The final reviewed report content.
    """

    logger.info(f"{'=' * 50}")
    logger.info(f"Staring Research Crew for topic: '{topic}'")
    logger.info(f"{'=' * 50}")

    #pre-flight checks
    validate_settings() #ensures API key present
    ensure_directories() #create output folders if missing

    #check memory for related past research
    memory = ResearchMemory()
    past_research = memory.get_related_research(topic)

    if past_research:
        logger.info("> Found related past research in memory <")
        print(f"\nFound related past research -agent will use this context")
    else:
        logger.info("> No related past research in memory - starting fresh <")
        print("\nNo past research found — conducting fresh research")


    #assemble crew
    tasks, agents = create_research_tasks(
        topic = topic,
        past_context = past_research #pass memory context to workflow
    )

    crew = Crew(
        agents=agents,
        tasks=tasks,
        process=Process.sequential, #run task in sequence order: research -> analyze -> write -> review
        verbose=VERBOSE,
        memory=False, #will enable ChromaDB after testing the module
    )

    #run crew
    logger.info("Crew assembled. Starting execution...")

    try:
        result = crew.kickoff() #start entire workflow

        #store result in memory
        memory.store_research(
            topic = topic,
            content = str(result),
            doc_type = "report"
        )
        logger.info(f"Results stored in memory.")
        logger.info("Crew execution completed successfully.")
        return str(result)

    except Exception as e:
        logger.error(f"Crew execution failed with error: {e}")
        raise

#test module
if __name__ == "__main__":
    topic = "The impact of artificial intelligence on healthcare in 2025"
    result = run_research_crew(topic)
    print("\n" + "="*50)
    print(" FINAL OUTPUT ")
    print("="*50 + "\n")
    print(result)