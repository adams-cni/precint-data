import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd

# Load the input CSV files with low_memory=False to handle mixed data types properly
precincts_file = 'unique_precincts_by_office.csv'
results_file = 'results_combined.csv'

# Load data into pandas DataFrames
precincts_df = pd.read_csv(precincts_file, low_memory=False)
results_df = pd.read_csv(results_file, low_memory=False)

# Create the main application window
root = tk.Tk()
root.title("Election Contest Finder")

# Function to fetch and display unique ContestNames based on user selection
def fetch_contest_names():
    selected_district = district_var.get()
    selected_year = year_var.get()

    if not selected_district or not selected_year:
        messagebox.showwarning("Input Error", "Please select both district and year.")
        return

    # Get the precincts for the selected district
    precincts = precincts_df[selected_district].dropna().unique()

    # Check if 'ElectionType' exists in the DataFrame columns
    if 'ElectionType' not in results_df.columns:
        messagebox.showerror("Data Error", "'ElectionType' column not found in results_combined.csv.")
        return

    # Filter the results_combined.csv based on selected year and matching precincts from the selected district
    matching_contests = results_df[
        (results_df['PrecinctID'].isin(precincts)) &  # Only consider precincts in the selected district
        (results_df['ContestName'].notna()) &  # Ensure ContestName is not null
        (results_df['ElectionType'] == selected_year)  # Match the selected ElectionType
    ]['ContestName'].unique()

    # Clear and populate the ContestName listbox with the matching contests
    contest_listbox.delete(0, tk.END)
    for contest in matching_contests:
        contest_listbox.insert(tk.END, contest)

# Function to display vote counts for selected ContestName
def display_vote_counts():
    try:
        selected_contest = contest_listbox.get(contest_listbox.curselection())
        selected_year = year_var.get()

        # Get the precincts for the selected district again to ensure filtering is accurate
        selected_district = district_var.get()
        precincts = precincts_df[selected_district].dropna().unique()

        # Filter results_combined.csv based on the selected ContestName, ElectionType, and precincts in the district
        vote_data = results_df[
            (results_df['ContestName'] == selected_contest) &  # Filter by the selected ContestName
            (results_df['PrecinctID'].isin(precincts)) &  # Only include precincts in the selected district
            (results_df['ElectionType'] == selected_year)  # Match the selected ElectionType
        ].groupby('CandidateName')['VoteCount'].sum().reset_index()

        # Remove rows where VoteCount is zero
        vote_data = vote_data[vote_data['VoteCount'] > 0]

        # Clear the table frame before populating new data
        for widget in table_frame.winfo_children():
            widget.destroy()

        # Create table headers
        header_label_1 = tk.Label(table_frame, text="CandidateName", font=('Arial', 10, 'bold'))
        header_label_1.grid(row=0, column=0, padx=10, pady=5)
        header_label_2 = tk.Label(table_frame, text="VoteCount", font=('Arial', 10, 'bold'))
        header_label_2.grid(row=0, column=1, padx=10, pady=5)

        # Populate the table with vote counts
        for i, (candidate, vote_count) in enumerate(vote_data.itertuples(index=False), start=1):
            candidate_label = tk.Label(table_frame, text=candidate)
            candidate_label.grid(row=i, column=0, padx=10, pady=2)
            vote_count_label = tk.Label(table_frame, text=vote_count)
            vote_count_label.grid(row=i, column=1, padx=10, pady=2)
    except tk.TclError:
        messagebox.showwarning("Selection Error", "Please select a contest name from the list.")

# Variables for storing user input
district_var = tk.StringVar()
year_var = tk.StringVar()

# Create the dropdown for district selection
district_label = tk.Label(root, text="Select District:")
district_label.pack()

district_dropdown = ttk.Combobox(root, textvariable=district_var)
district_dropdown['values'] = list(precincts_df.columns)
district_dropdown.pack()

# Create the dropdown for year selection
year_label = tk.Label(root, text="Select Year:")
year_label.pack()

year_dropdown = ttk.Combobox(root, textvariable=year_var)
year_dropdown['values'] = ['2022GE', '2022GP', '2024GP']
year_dropdown.pack()

# Create a button to trigger fetching the contest names
fetch_button = tk.Button(root, text="Find Contests", command=fetch_contest_names)
fetch_button.pack()

# Create a label and a frame for the ContestName listbox with a scrollbar
contest_label = tk.Label(root, text="Select Contest Name:")
contest_label.pack()

contest_frame = tk.Frame(root)
contest_frame.pack()

scrollbar = tk.Scrollbar(contest_frame, orient=tk.VERTICAL)
contest_listbox = tk.Listbox(contest_frame, width=50, height=10, yscrollcommand=scrollbar.set, selectmode=tk.SINGLE)
scrollbar.config(command=contest_listbox.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
contest_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Button to display vote counts for the selected ContestName
vote_count_button = tk.Button(root, text="Show Vote Counts", command=display_vote_counts)
vote_count_button.pack()

# Frame to display the vote count table
table_frame = tk.Frame(root)
table_frame.pack()

# Start the main event loop
root.mainloop()
