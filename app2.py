import streamlit as st
import pandas as pd
import json

def enrich_data(data):
    # Extract the dictionary containing the category scores
    category_scores = data[3]  # Access the category_scores directly from the inner list
    
    # Find the best and worst performed categories
    best_category = max(category_scores, key=category_scores.get)
    worst_category = min(category_scores, key=category_scores.get)
    
    # Get the scores for the best and worst categories
    best_score = category_scores[best_category]
    worst_score = category_scores[worst_category]
    
    # Return the enriched data as a list
    return data + [best_category, worst_category, best_score, worst_score]

# Load survey questions from JSON file
with open("scorechart.json", "r") as file:
    data = json.load(file)

# Personal Information Fields
st.title("Survey Form")
full_name = st.text_input("Full Name")
email = st.text_input("Email")

# Survey Form
responses = {}
st.subheader("Answer the questions below:")
for idx, q in enumerate(data["questions"]):
    response = st.radio(q["question"], q["answers"], key=f"q{idx}")
    responses[q["question"]] = q["scores"][q["answers"].index(response)]

# Aggregate Results
if st.button("Submit"):
    results = []
    # Store the survey responses and calculate total score
    category_scores = {}
    total_score = 0
    for q in data["questions"]:
        score = responses[q["question"]]
        for category in q["categories"]:
            category_scores[category] = category_scores.get(category, 0) + score
            total_score += score
    
    # Append full_name, email, total_score, and category_scores to the results
    results.append([full_name, email, total_score, category_scores])
    
    # Enrich the data for the current respondent
    enriched_data = enrich_data(results[0])  # Pass the first (and only) row to enrich_data
    
    # Create the DataFrame
    df_results = pd.DataFrame([enriched_data], columns=["FullName", "Email", "TotalScore", "CategoryScores", "BestCategory", "WorstCategory", "BestCategoryScore", "WorstCategoryScore"])
    
    # Display the results dataframe
    st.dataframe(df_results)
       
    # Append the current submission to the session-state DataFrame
    if 'df_all_results' not in st.session_state:
        st.session_state.df_all_results = pd.DataFrame(columns=["FullName", "Email", "TotalScore", "CategoryScores", "BestCategory", "WorstCategory", "BestCategoryScore", "WorstCategoryScore"])
    st.session_state.df_all_results = pd.concat([st.session_state.df_all_results, df_results], ignore_index=True)
    # Display all submitted results
    st.write("All Submitted Results:")
    st.dataframe(st.session_state.df_all_results)
