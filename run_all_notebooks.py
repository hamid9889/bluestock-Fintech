import os
import subprocess
import glob

def run_notebook(notebook_path):
    """Executes a Jupyter notebook using nbconvert."""
    print(f"Executing: {notebook_path}")
    try:
        subprocess.run([
            "jupyter", "nbconvert", "--to", "notebook", "--execute", 
            "--inplace", notebook_path
        ], check=True)
        print(f"Successfully finished: {notebook_path}")
    except subprocess.CalledProcessError as e:
        print(f"Error executing {notebook_path}: {e}")

def main():
    # 1. Day 2: Cleaning Notebooks
    print("\n--- Phase 1: Running Day 2 Cleaning Notebooks ---")
    day2_cleaning_dir = r"notebooks/day2_cleaning"
    cleaning_files = sorted(glob.glob(os.path.join(day2_cleaning_dir, "*_cleaning.ipynb")))
    for nb in cleaning_files:
        run_notebook(nb)

    # 2. Day 2: Master Loading & SQL Analysis
    print("\n--- Phase 2: Running Database Loading & SQL Analysis ---")
    run_notebook(os.path.join(day2_cleaning_dir, "99_master_loading.ipynb"))
    run_notebook(os.path.join(day2_cleaning_dir, "100_sql_analysis.ipynb"))

    # 3. Day 3: EDA Analysis
    print("\n--- Phase 3: Running Day 3 EDA Analysis ---")
    run_notebook(r"notebooks/day3_eda/EDA_Analysis.ipynb")

    # 4. Day 4: Performance Analytics
    print("\n--- Phase 4: Running Day 4 Performance Analytics ---")
    run_notebook(r"notebooks/day4_analytics/Performance_Analytics.ipynb")

    print("\nAll notebooks have been executed and outputs are updated!")

if __name__ == "__main__":
    main()
