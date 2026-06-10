#Defining task need to perform by each agent
from crewai import Task
from agents.researcher import create_researcher
from agents.analyzer import create_analyzer
from agents.writer import create_writer
from agents.reviewer import create_reviewer
from utils.logger import get_logger

logger = get_logger(__name__)

def create_research_tasks(topic: str) -> tuple:
    """
    Creates all 4 tasks and their assigned agents for a research topic.
    Returns a tuple of (task, agents) ready for the Crew.

    Args:
    topic : The research topic provided by user.

    Returns:
    tuple: (list of tasks, list of agents)
    """
    logger.info(f"Creating research workflow for topic {topic}")

    #Create agents
    researcher = create_researcher()
    analyzer = create_analyzer()
    writer = create_writer()
    reviewer = create_reviewer()

    # task1 - research
    research_task = Task(
        description=(
            f"Conduct comprehensive research on the following topic:\n\n{topic}\n\n"
            f"TOPIC: {topic}\n\n"
            f"Your research MUST include:\n"
            f"1. Search for at least 3 different angles of this topics\n"
            f"2. Scrape and read at least 3 full articles\n"
            f"3. Gather key facts, statistics, and quotes with source URLs\n"
            f"4. Indentify any conflicting information or debates\n"
            f"5. Note the most credible and recent sources\n\n"
            f"IMPORTANT: You MUST call the 'Write File' tool to save your findings before finishing. "
            f"Use filename='raw_research.md' and 'subfolder='raw'. Do not give your final answer until the file is saved successfully."
        ),
        expected_output=(
            "Confirmation that 'raw_research.md' was saved to output/raw/, "
            "plus a brief summary of the key findings discovered."
        ),
        agent = researcher,
    )

    #task 2 - analysis
    analysis_task = Task(
        description = (
            f"Write a comprehensive, well-structured research report "
            f"about '{topic}' based on the analysis provided.\n\n"
            f"Your report MUST:\n"
            f"1. Start with an executive summary (150-200 words)\n"
            f"2. Include a proper introduction with context\n"
            f"3. Cover all major themes identified in the analysis\n"
            f"4. Include relevant statistics and cite sources\n"
            f"5. End with a conclusion and key takeaways\n"
            f"6. Be formatted in clean, professional Markdown\n"
            f"7. Be between 800-1200 words\n\n"
            f"IMPORTANT: You MUST call the 'Write File' tool to save your "
            f"report before finishing. Use filename='final_report.md' and "
            f"subfolder='reports'. Do not give your final answer until "
            f"the file is saved successfully."
        ),
        expected_output = (
            "Confirmation that 'analysis.md' was saved to output/raw/, "
            "plus a brief summary of the top themes identified."
        ),
        agent = analyzer,
        context = [research_task], #analyzer see researcher output
    )

    #task 3 - writing
    writing_task = Task(
        description = (
            f"Write a comprehensive, well-structured research report "
            f"about '{topic}' based on the analysis provided.\n\n"
            f"Your report MUST:\n"
            f"1. Start with an executive summary (150-200 words)\n"
            f"2. Include a proper introduction with context\n"
            f"3. Cover all major themes identified in the analysis\n"
            f"4. Include relevant statistics and cite sources\n"
            f"5. End with a conclusion and key takeaway\n"
            f"6. Be formatted in clean, professional Markdown\n"
            f"7. Be between 800-1200 words\n\n"
            f"Save the reports as 'final_report.md' in the 'reports' subfolder."
        ),
        expected_output = (
            "Confirmation that 'final_report.md' was saved to output/reports/, "
            "plus the full report content in Markdown format."
        ),
        agent = writer,
        context = [research_task, analysis_task], #writer see both analyzer and researcher output
    )

    #task 4 - review
    review_task = Task(
        description=(
            f"Review and improve the research report about '{topic}'.\n\n"
            f"You MUST check for:\n"
            f"1. Factual accuracy — are all claims supported by research?\n"
            f"2. Completeness — are all major themes covered?\n"
            f"3. Clarity — is the writing clear and professional?\n"
            f"4. Structure — does the report flow logically?\n"
            f"5. Citations — are sources properly referenced?\n\n"
            f"Fix any issues you find directly in the report. "
            f"Save the final reviewed version as 'reviewed_report.md' "
            f"in the 'reports' subfolder. "
            f"Also provide a brief review summary of what you changed."
        ),
        expected_output=(
            "Confirmation that 'reviewed_report.md' was saved to output/reports/, "
            "plus a summary of improvements made to the report."
        ),
        agent = reviewer,
        context = [research_task, analysis_task, writing_task],
    )

    tasks = [research_task, analysis_task, writing_task, review_task]
    agents = [researcher, analyzer, writer, reviewer]

    logger.info(f"Created {len(tasks)} tasks for workflow")
    return tasks, agents