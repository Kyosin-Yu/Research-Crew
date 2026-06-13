# Research-Crew
A multi-agent AI system that autonomously researches any topic, analyzes findings, writes a report, and reviews it for quality — built with CrewAI.

## Architecture 

## Tech Stack
- **Framework:** CrewAI (multi-agent orchestration)
- **LLM:** NVIDIA Nemotron 3 Super (free, via OpenRouter)
- **Search:** Serper API (Google search)
- **Scraping:** BeautifulSoup4
- **Memory:** ChromaDB (local vector database)
- **UI:** Streamlit
- **Testing:** pytest

# Setup Instructions
### 1. Clone and create virtual environment
```bash
git clone https://github.com/Kyosin-Yu/Research-Crew.git
cd Research-Crew
py -3.12 -m venv venv
venv\Scripts\activate

```
### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure API keys
Create a `.env` file in the project root:

## Running the Project

### Terminal version
```bash
python main.py
```
Enter your research topic when prompted.

### Web UI (Streamlit)
```bash
streamlit run app.py
```

### Run tests
```bash
python -m pytest tests/ -v
```

## Project Structure
Research-Crew/
├── agents/          # Agent definitions (Researcher, Analyzer, Writer, Reviewer)
├── tools/           # Custom tools (search, scrape, file I/O)
├── workflows/       # Task definitions & sequencing
├── memory/          # ChromaDB long-term memory
├── config/          # Settings & environment config
├── utils/           # Logger & helper functions
├── tests/           # Unit tests
├── output/
│   ├── raw/         # Researcher & Analyzer outputs
│   └── reports/     # Final reports
├── crew.py          # Crew orchestration
├── main.py          # CLI entry point
└── app.py           # Streamlit UI

## Example Workflow

1. User enters: *"The impact of AI on healthcare"*
2. **Researcher** searches Google (Serper), scrapes top articles, saves `raw_research.md`
3. **Analyzer** identifies key themes & evaluates sources, saves `analysis.md`
4. **Writer** drafts an 800-1200 word Markdown report, saves `final_report.md`
5. **Reviewer** checks accuracy/clarity, polishes, saves `reviewed_report.md`
6. Result is stored in ChromaDB for future related research

## Limitations

- Free OpenRouter models have a **50 requests/day** rate limit
- Web scraping is capped at 4,000 characters per page to manage context size
- Some websites block scraping (anti-bot protection)
- ChromaDB memory is local — not shared across machines

## Future Improvements

- [ ] Hierarchical process (manager agent dynamically delegates)
- [ ] PDF export of final reports
- [ ] Human-in-the-loop approval between agent stages
- [ ] Support for multiple LLM providers with automatic fallback
- [ ] Deploy to Hugging Face Spaces

