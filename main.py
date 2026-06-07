import sys
from src.etl.cleaner import DataCleaner
from src.etl.loader import DataLoader
from src.etl.analyzer import DataAnalyzer

def main():
    """
    Main entry point for the Bluestock Fintech Data Pipeline.
    Orchestrates the cleaning, loading, and analytical extraction processes.
    """
    print("=== Bluestock Fintech Data Pipeline Starting ===\n")

    try:
        # Step 1: Data Cleaning
        cleaner = DataCleaner()
        cleaner.run_all()

        print("\n" + "="*50 + "\n")

        # Step 2: Database Loading
        loader = DataLoader()
        loader.run_all()

        print("\n" + "="*50 + "\n")

        # Step 3: Analytical Extraction
        analyzer = DataAnalyzer()
        analyzer.run_all()

        print("\n=== Pipeline Execution Completed Successfully ===")

    except Exception as e:
        print(f"\n[ERROR] Pipeline failed: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
