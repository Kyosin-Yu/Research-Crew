from crewai import Agent, LLM
from tools.searchTool import WebSearchTool
from tools.scrapeTool import WebScrapeTool
from tools.fileTool import WriteFileTool
from config.settings import (OPENROUTER_API_KEY, OPENROUTER_BASE_URL, LLM_MODEL, MAX_ITERATIONS, MAX_RPM, VERBOSE)
from utils.logger import get_logger

logger = get_logger(__name__)

def create_researcher() -> Agent:
    """
    Factory function that creates and returns the Researcher agent.
    Using a factory function (instead of a global object) means we create a fresh agent each time - no stale state between runs.
    """
    logger.info("Creating Researcher Agent...")

    #LLM configuration
    llm=LLM(
        model=LLM_MODEL,
        base_url=OPENROUTER_BASE_URL,
        api_key=OPENROUTER_API_KEY,
        temperature=0.3 #lower = less creative
    )

    #Agent definitions
    agent = Agent(
        role="Senior Research Specialists",
        goal=(
            "Conduct thorough and comprehensive research on the given topic."
            "Gather accurate, relevant, and up-to-date information from"
            "multiple credible sources. Always cite your sources with URLs."
            ""
        ),
        backstory=(
            "You are a seasoned research specialist with over 10 years of experience in academic and investigative research. You have a talent for finding credible information quickly,"
            "cross-referencing multiple sources, and identifying both supporting evidence and contractions."
            "You are methodical, thorough, and always prioritize accuracy over speed."
            "You never make up information - if you can't find something, you say so clearly."
        ),
        tools=[
            WebSearchTool(),
            WebScrapeTool(),
            WriteFileTool()
        ],
        llm=llm,
        max_itr=MAX_ITERATIONS,
        max_rpm=MAX_RPM,
        verbose=VERBOSE,
        allow_delegation=False, #researcher do it own work
    )

    logger.info("Researcher agent created successfully")
    return agent
