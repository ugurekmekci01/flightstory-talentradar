import streamlit as st
import pandas as pd
import json
from datetime import datetime
import uuid

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
    responses[q["question"]] = q["scores"][q["answers"].index(response)]

# Aggregate Results
if st.button("Submit"):
    # Initialize results dictionary with default scores for all categories
    categories = set()
    for q in data["questions"]:
        categories.update(q["categories"])
    results = {category: 0 for category in categories}

    # Calculate scores for each category
    total_score = 0  # Initialize total score
    for q in data["questions"]:
        score = responses[q["question"]]
        for category in q["categories"]:
            results[category] += score
            total_score += score  # Add to total score

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


    # fig = px.bar(df_results, x="Category", y="Score", title="Category Scores")
    # st.plotly_chart(fig)
    
    # # Dummy Data for Statistical Visualization
    # dummy_data = []
    # for i in range(20):
    #     dummy_data.append({category: random.randint(-10, 10) for category in results.keys()})
    # df_dummy = pd.DataFrame(dummy_data)
    # st.subheader("Statistical Overview")
    # st.dataframe(df_dummy.describe())
    
    # # Best & Worst Performers
    # best = df_dummy.mean().idxmax()
    # worst = df_dummy.mean().idxmin()
    # st.write(f"Best Performing Category: {best}")
    # st.write(f"Worst Performing Category: {worst}")
