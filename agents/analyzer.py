from crewai import Agent, LLM
from tools.fileTool import WriteFileTool, ReadFileTool
from config.settings import (OPENROUTER_API_KEY, OPENROUTER_BASE_URL, LLM_MODEL, MAX_ITERATIONS, MAX_RPM, VERBOSE)
from utils.logger import get_logger

logger = get_logger(__name__)

def create_analyzer() -> Agent:
    """
    Factory function that creates and returns the Analyzer agent.
    The Analyzer receives raw research and turn it into structured, reasoned insights.
    """
    logger.info("Creating Analyzer agent...")

    #LLM configuration
    llm = LLM(
        model=LLM_MODEL,
        base_url=OPENROUTER_BASE_URL,
        api_key=OPENROUTER_API_KEY,
        temperature=0.2, #Very low = precise and logical analysis
    )

    #Agent definition
    agent = Agent(
        role="Senior Research Analyst",
        goal=(
            "Analyze and synthesize raw research findings into clear, structured insights."
            "Identify key theme, patterns, and contradictions"
            "Organize findings into a logical structure ready for reports writing."
        ),
        backstory=(
            "You are an expert research analyst with a background in data synthesis and critical thinking."
            "You excel at taking large volume of arw information and distilling them into clear, actionable insights."
            "You always look for patterns, evaluate source credibility, flag contradictions, and structure information logically."
            "You separate facts from opinions and always maintain objectivity in your analysis."
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

    logger.info("Analyzer agent created successfully")
    return agent
