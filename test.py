import streamlit as st
import pandas as pd
import json
from datetime import datetime
import uuid
import matplotlib.pyplot as plt
import seaborn as sns


#create visualisation
def plot_category_scores(df):
    # Sort by score in descending order
    df = df.sort_values(by="Score", ascending=False)
    
    # Create the figure and axis
    plt.figure(figsize=(10, 8))
    sns.barplot(x=df["Score"], y=df["Category"], palette="coolwarm")
    plt.xlabel("Score")
    plt.ylabel("Category")
    plt.title("Category Scores (Descending Order)")
    plt.axvline(0, color='black', linewidth=1)  # Vertical line at 0 for reference
    
    return plt

# Load survey questions
with open("scorechart.json", "r") as file:
    data = json.load(file)

# Personal Information Fields
st.title("Survey Form")
full_name = st.text_input("Full Name")
email = st.text_input("Email")
position = st.text_input("Position")

# Survey Form
responses = {}
st.subheader("Answer the questions below:")
for idx, q in enumerate(data["questions"]):
    response = st.radio(q["question"], q["answers"], key=f"q{idx}")
    responses[q["question"]] = {
        "score": q["scores"][q["answers"].index(response)],
        "categories": q["categories"]
    }

# Aggregate Results
if st.button("Submit"):
    # Initialize results dictionary with default scores for all categories
    categories = set()
    for q in data["questions"]:
        categories.update(q["categories"])
    results = {category: 0 for category in categories}

    # Calculate scores for each category
    total_score = 0
    for q in data["questions"]:
        score = responses[q["question"]]["score"]
        for category in responses[q["question"]]["categories"]:
            results[category] += score
        total_score += score

    # Add metadata (ID, DateTime, and TotalScore)
    results["ID"] = str(uuid.uuid4())  # Generate a unique ID
    results["DateTime"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Add current timestamp
    results["FullName"] = full_name
    results["Email"] = email
    results["Position"] = position
    results["TotalScore"] = total_score  # Add total score

    # Convert results to DataFrame
    df_results = pd.DataFrame([results])

    # Reorder columns to have metadata first, followed by categories
    columns = ["ID", "DateTime", "FullName", "Email", "Position", "TotalScore"] + sorted(categories)
    df_results = df_results[columns]

    # Display the results dataframe
    st.dataframe(df_results)

    # Save results to a session-state DataFrame (optional, for persistence across submissions)
    if 'all_results' not in st.session_state:
        st.session_state.all_results = pd.DataFrame(columns=columns)
    st.session_state.all_results = pd.concat([st.session_state.all_results, df_results], ignore_index=True)

    # Display all submitted results (optional)
    st.subheader("All Submitted Results:")
    st.dataframe(st.session_state.all_results)