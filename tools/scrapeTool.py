import requests
from bs4 import BeautifulSoup
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from utils.logger import get_logger

logger = get_logger(__name__)


#Input schema
class ScrapeInput(BaseModel):
    """Defines what inputs the scrape tool accepts."""
    url: str = Field(
        description="The full URL of the webpage to scrape and read"
    )


#Tool definition
class WebScrapeTool(BaseTool):
    name: str = "Web Scraper"
    description: str = (
        "Reads and extracts the full text content from a webpage URL. "
        "Use this after web search to read the full article or page content. "
        "Input must be a valid URL starting with http:// or https://"
    )
    args_schema: type[BaseModel] = ScrapeInput

    def _run(self, url: str) -> str:
        """
        Fetches a webpage and extracts clean readable text.
        Strips all HTML tags, scripts, and styling.
        """
        logger.info(f"Scraping URL: {url}")

        #Validate URL
        if not url.startswith(("http://", "https://")):
            return "ERROR: Invalid URL. Must start with http:// or https://"

        #Fetch page
        try:
            response = requests.get(
                url=url,
                headers={
                    #Pretend to be a browser so websites don't block us
                    "User-Agent": (
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/120.0.0.0 Safari/537.36"
                    )
                },
                timeout=15
            )
            response.raise_for_status()

        except requests.exceptions.Timeout:
            logger.error(f"Scrape timed out: {url}")
            return f"ERROR: Page took too long to load - {url}"

        except requests.exceptions.RequestException as e:
            logger.error(f"Scrape failed: {url} | {e}")
            return f"ERROR: Could not access page - {str(e)}"

        #Parse and clean HTML (remove the <div> <b>....</b> </div> etc)
        try:
            soup = BeautifulSoup(response.content, "html.parser")

            #Remove noise elements that aren't actual content
            for tag in soup(["script", "style", "nav", "footer",
                             "header", "aside", "advertisement"]):
                tag.decompose()

            #Extract clean text
            text = soup.get_text(separator="\n", strip=True)

            #Remove excessive blank lines
            lines = [line for line in text.splitlines() if line.strip()]
            clean_text = "\n".join(lines)

            #Limit output size (avoid overflowing model context window)
            MAX_CHARS = 4000
            if len(clean_text) > MAX_CHARS:
                clean_text = clean_text[:MAX_CHARS]
                clean_text += f"\n\n[Content truncated at {MAX_CHARS} chars]"

            logger.info(f"Scraped {len(clean_text)} characters from {url}")
            return f"Content from {url}:\n\n{clean_text}"

        except Exception as e:
            logger.error(f"Failed to parse page content: {e}")
            return f"ERROR: Could not parse page content - {str(e)}"


#test module
if __name__ == "__main__":
    tool = WebScrapeTool()
    result = tool._run("https://en.wikipedia.org/wiki/Artificial_intelligence")
    print(result)
    print(f"\nTotal characters: {len(result)}")