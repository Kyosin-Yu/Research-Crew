import json
import requests
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from config.settings import SERPER_API_KEY
from utils.logger import get_logger

logger = get_logger(__name__)

#Input Scheme
class SearchInput(BaseModel):
    """Defines what inputs the search tool accepts"""
    query: str = Field(description = "The search query to look up on Google")
    num_results: int= Field(default = 5, description = "Number of search results to return (maximum 10)")

#Tool Definition
class WebSearchTool(BaseTool):
    name: str = "Web Search"
    description: str = (
        "Searches Google for current information on any topic."
        "Return titles, URLs, and snippets of the top results."
        "Use this when you need to find recent or factual information."
    )
    args_schema: type[BaseModel] = SearchInput

    def _run(self, query: str, num_results: int = 5) -> str:
        """
        Executes a Google search via Serper API.
        Returns formatted search results as a string.
        """
        logger.info(f"Web search called with query: {query}")

        #call API
        try:
            response = requests.post(
                url="https://google.serper.dev/search",
                headers={
                    "X-Api-Key": SERPER_API_KEY,
                    "Content-Type": "application/json"
                },
                data = json.dumps({
                    "q": query,
                    "num": num_results
                }),
                timeout = 10
            )
            response.raise_for_status()

        except requests.exceptions.Timeout:
            logger.error("Search request timed out")
            return "ERROR: Search request timed out. Please try again."

        except requests.exceptions.RequestException as e:
            logger.error(f"Search request failed: {e}")
            return f"ERROR: Search failed - {str(e)}"

        #Parse results
        try:
            data = response.json()
            results = data.get("organic", [])

            if not results:
                logger.warning(f"No results found for query: '{query}'")
                return f"No results found for '{query}'. Try a different search query."

            #Format results into readable string for agent
            formatted = f"Search Results For: '{query}'\n"
            formatted += "=" * 30 + "\n\n"

            for i, result in enumerate(results[:num_results], 1):
                formatted += f"{i}. {result.get('title', 'No title')}\n"
                formatted += f"URL: {result.get('link', 'No URL')}\n"
                formatted += f"{result.get('snippet', 'No snippet')}\n\n"

            logger.info(f"Search returned {len(results)} results")
            return formatted

        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Failed to parse search response: {e}")
            return f"ERROR: Could not parse search response - {str(e)}"

if __name__ == "__main__":
    tool = WebSearchTool()
    result = tool._run("artificial intelligence in healthcare 2024")
    print(result)





