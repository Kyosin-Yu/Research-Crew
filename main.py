from crew import run_research_crew
from utils.logger import get_logger

logger = get_logger(__name__)

def main():
    print("\n" + "="*60)
    print(" Personal Research & Report Generation Crew ")
    print("="*60)

    #get topic from user
    topic = input("\nEnter research topic: ").strip()

    if not topic:
        print("ERROR: Please provide a research topic.")
        return

    print(f"\nStarting research on: '{topic}'")
    print("This may take a few minutes...\n")

    try:
        result = run_research_crew(topic)
        print("\n" + "=" * 60)
        print(" RESEARCH COMPLETE ")
        print("=" * 60 + "\n")
        print(result)
        print("\n\nCheck the output/reports/ folder for saved files.")

    except KeyboardInterrupt:
        print("\n\nresearch cancelled by user.")

    except Exception as e:
        logger.error(f"unexpected error: {e}")
        print(f"ERROR: Something went wrong - {e}")

if __name__ == "__main__":
    main()