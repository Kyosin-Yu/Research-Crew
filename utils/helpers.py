import os
import json
from datetime import datetime
from utils.logger import get_logger

logger = get_logger(__name__)

def ensure_directories() -> None:
    """Creates all required output directories if they do not exist."""
    dirs = ["output", "output/reports", "output/raw", "logs"]
    for dir_path in dirs:
        os.makedirs(dir_path, exist_ok=True)
        logger.debug(f"Directory ensures: {dir_path}")

def save_json(data: dict, filename: str) -> str:
    """
    Saves a dictionary to a JSON file in output/raw/.
    Returns the full file path.
    """
    ensure_directories()
    filepath = f"output/raw/{filename}"
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    logger.info(f"JSON saved: {filepath}")
    return filepath

def save_raport(content:str, topic:str) -> str:
    """
    Save the final report as a Markdown file.
    Filename is auto-generated from topic + timestamp.
    Returns the full file path.
    """
    ensure_directories()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_topic = topic.lower().replace(" ","_")[:30]
    filename = f"output/reports/{safe_topic}_{timestamp}.md"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
    logger.info(f"Report saved: {filename}")
    return filename

def load_json(file_path: str) -> dict:
    """Loads a JSON file and returns it as a dictionary."""
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)