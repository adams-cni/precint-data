import streamlit as st
import pandas as pd

# Load the input CSV files with low_memory=False to handle mixed data types properly
precincts_file = 'unique_precincts_by_office.csv'
results_file = 'results_combined.csv'

# Load data into pandas DataFrames
precincts_df = pd.read_csv(precincts_file, low_memory=False)
results_df = pd.read_csv(results_file, low_memory=False)

# Streamlit app title
st.title("Election Contest Finder")

# Dropdown for district selection
selected_district = st.selectbox("Select District:", options=precincts_df.columns)

# Dropdown for year selection
selected_year = st.selectbox("Select Year:", options=['2022GE', '2022GP', '2024GP'])

# Button to fetch contests
if st.button("Find Contests"):
    if selected_district and selected_year:
        # Get the precincts for the selected district
        precincts = precincts_df[selected_district].dropna().unique()

        # Filter the results_combined.csv based on selected year and matching precincts
        matching_contests = results_df[
            (results_df['PrecinctID'].isin(precincts)) &
            (results_df['ContestName'].notna()) &
            (results_df['ElectionType'] == selected_year)
        ]['ContestName'].unique()

        # Display the unique ContestNames as a selectbox
        selected_contest = st.selectbox("Select Contest Name:", options=matching_contests)

        if selected_contest:
            # Filter vote counts based on the selected ContestName and ElectionType
            vote_data = results_df[
                (results_df['ContestName'] == selected_contest) &
                (results_df['PrecinctID'].isin(precincts)) &
                (results_df['ElectionType'] == selected_year)
            ].groupby('CandidateName')['VoteCount'].sum().reset_index()

            # Remove rows where VoteCount is zero
            vote_data = vote_data[vote_data['VoteCount'] > 0]

            # Display the vote count results as a table
            st.write("Vote Counts for Selected Contest:")
            st.table(vote_data)
    else:
        st.warning("Please select both district and year.")
