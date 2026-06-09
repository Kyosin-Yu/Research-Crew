from crewai import Agent, LLM
from tools.fileTool import WriteFileTool, ReadFileTool
from config.settings import(OPENROUTER_BASE_URL, OPENROUTER_API_KEY, LLM_MODEL, MAX_RPM, MAX_ITERATIONS, VERBOSE)
from utils.logger import get_logger

logger = get_logger(__name__)

def create_writer() -> Agent:
    """
    Factory functions that creates and returns the Writer agent.
    The Writer transforms analyzed insights into a polished report.
    """
    logger.info("Creating Writer agent...")

    #LLM configurations
    llm = LLM(
        model = LLM_MODEL,
        base_url = OPENROUTER_BASE_URL,
        api_key = OPENROUTER_API_KEY,
        temperature = 0.7, #Higher = more creative, better writing style
    )

    #Agent definition
    agent = Agent(
        role = "Senior Technical Writer",
        goal = (
            "Transform research analysis into a well-structured, comprehensive, and engaging Markdown report."
            "The report must be clear, professional, and accessible to a general educated audience."
        ),
        backstory=(
            "You are an accomplished technical writer with expertise in transforming complex research into clear, engaging reports."
            "You have written hundreds of research reports, white papers, and technical documents."
            "You excel in structuring information logically, writing compelling introductions and conclusions, and making complex topics accessible without sacrificing accuracy."
            "you always format reports in clean Markdown with proper headings, bullet points, and sections."
        ),
        tools = [
            ReadFileTool(),
            WriteFileTool(),
        ],
        llm=llm,
        max_iter=MAX_ITERATIONS,
        max_rpm=MAX_RPM,
        verbose=VERBOSE,
        allow_delegation=False,
    )

    logger.info("Writer agent created successfully")
    return agent
