from crewai import Agent, LLM
from tools.fileTool import WriteFileTool, ReadFileTool
from config.settings import(OPENROUTER_BASE_URL, OPENROUTER_API_KEY, LLM_MODEL, MAX_RPM, MAX_ITERATIONS, VERBOSE)
from utils.logger import get_logger

logger = get_logger(__name__)

def create_reviewer() -> Agent:
    """
    Factory function that creates and returns the Reviewer agent.
    The Reviewer is the quality gate - nothing gets published without passing its critique.
    """
    logger.info("Creating Reviewer agent...")

    #LLM configuration
    llm= LLM(
        model= LLM_MODEL,
        base_url= OPENROUTER_BASE_URL,
        api_key= OPENROUTER_API_KEY,
        temperature=0.1, #Very low = critical review needs consistency
    )

    #Agent definition
    agent = Agent(
        role = "Senior Quality Assurance Reviewer",
        goal = (
            "Critically review the research report for accuracy, completeness, clarity, and quality."
            "Identify any gaps, unsupported claims, or areas needing improvement."
            "Produce a final polished version of the report."
        ),
        backstory = (
            "You are a meticulous quality assurance reviewer with high standards and an eye for detail."
            "You have reviewed thousands of research reports and academic papers."
            "You check for: factual accuracy, logical consistency, unsupported claims, clarity of writing, proper structure, and completeness."
            "You are constructive but demanding - you do not pass substandard work."
            "When you find issues, you fix them directly rather than just flagging them."
        ),
        tools=[
            ReadFileTool(),
            WriteFileTool(),
        ],
        llm=llm,
        max_iter=MAX_ITERATIONS,
        max_rpm=MAX_RPM,
        verbose=VERBOSE,
        allow_delegation=False,
    )

    logger.info("Reviewer agent created successfully")
    return agent
