import pandas as pd

# --- 1. GLOBAL SCOPE (Runs immediately on import) ---
# These lines must be at the far left (no indentation) so the variable exists for import.

flat_file_df = pd.read_csv("layoffs.csv")

# Filter for USA
flat_file_usa = flat_file_df[flat_file_df['country'] == 'United States']

# Filter for Public Companies
flat_file_public = flat_file_usa[flat_file_usa['stage'] == 'Post-IPO'].copy()

# Date Formatting
flat_file_public['date'] = pd.to_datetime(flat_file_public['date'], errors='coerce')
flat_file_public['date_added'] = pd.to_datetime(flat_file_public['date_added'], errors='coerce')

# Filter Nulls & Types
flat_file_public = flat_file_public[flat_file_public['total_laid_off'].notnull()]
flat_file_public = flat_file_public.convert_dtypes()

# Clean Whitespace (THIS IS THE VARIABLE YOU WANT)
flat_file_cleaned = flat_file_public.copy()
flat_file_cleaned['company'] = flat_file_cleaned['company'].str.strip().str.title()


# --- 2. LOCAL SCOPE (Runs only when you run this file directly) ---
# Use this for print statements so they don't spam you when you import.
if __name__ == "__main__":
    print("This file is being run directly.")
    print(flat_file_cleaned.head())