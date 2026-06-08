import pandas as pd
import os

# Paths
report_dir = r'c:\Users\Dell\OneDrive\Desktop\task 1\reports\analytics'
output_dir = r'c:\Users\Dell\OneDrive\Desktop\task 1\data\day4_analysis_results'

# Load existing deliverables
scorecard_path = os.path.join(report_dir, 'fund_scorecard.csv')
alpha_beta_path = os.path.join(report_dir, 'alpha_beta.csv')

if os.path.exists(scorecard_path):
    df_scorecard = pd.read_csv(scorecard_path)
    
    # Save the consolidated result
    output_path = os.path.join(output_dir, 'day4_performance_analytics_results.csv')
    df_scorecard.to_csv(output_path, index=False)
    print(f"Consolidated analytics results saved to: {output_path}")
else:
    print("Error: fund_scorecard.csv not found. Please run Performance Analytics first.")
