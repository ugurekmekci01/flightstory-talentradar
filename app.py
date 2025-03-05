import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import json

# Function to load survey data from JSON file
def load_survey_data(file_path):
    with open(file_path, "r") as f:
        return json.load(f)

# Define a dictionary to map each question to an attribute
question_attributes = {
    0: 'Leadership',
    1: 'Decision-Making',
    2: 'Problem Solving',
    3: 'Technical Skills',
    4: 'Leadership',
    5: 'Decision-Making',
    6: 'Communication',
    7: 'Decision-Making',
    8: 'Problem Solving',
    9: 'Leadership',
    10: 'Technical Skills',
    11: 'Problem Solving',
    12: 'Creativity',
    13: 'Leadership',
    14: 'Technical Skills',
    15: 'Problem Solving',
    16: 'Teamwork',
    17: 'Communication',
    18: 'Problem Solving',
    19: 'Leadership',
    20: 'Creativity',
    21: 'Technical Skills',
    22: 'Problem Solving',
    23: 'Leadership',
    24: 'Problem Solving',
    25: 'Leadership',
    26: 'Communication',
    27: 'Teamwork',
    28: 'Leadership',
    29: 'Teamwork',
    30: 'Technical Skills',
    31: 'Problem Solving',
    32: 'Creativity',
    33: 'Communication'
}

# Function to calculate score from answers
def calculate_score(selected_answer, question_index, survey_data):
    # Get the index of the selected answer in the options list
    answer_index = selected_answer
    # Return the corresponding score for that answer
    score = survey_data["questions"][question_index]["scores"][answer_index]
    return score if isinstance(score, int) else 0  # Return 0 if the score is not an integer

# Create a spider chart from the scores
def create_spider_chart(scores, labels):
    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=scores,
        theta=labels,
        fill='toself',
        name='User Strengths'
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[-10, 10])  # Adjusted range based on scores
        ),
        showlegend=False,
        title="User Strengths Spider Chart"
    )
    return fig

# Streamlit app
def app():
    # Load the survey data from JSON file
    survey_data = load_survey_data("output2.json")

    st.title("Survey Data Collection and Scoring")

    # Initialize session state
    if "responses" not in st.session_state:
        st.session_state.responses = []

    # Create a form to collect user responses
    with st.form("survey_form"):
        st.subheader("Survey Questions")
        user_responses = []
        
        for index, data in enumerate(survey_data["questions"]):  # Adjusted to access "questions"
            question = data["question"]
            answers = data["answers"]
            answer_scores = data["scores"]
            
            # Radio buttons to choose answer
            user_answer = st.radio(question, options=range(len(answers)), format_func=lambda x: answers[x])
            
            # Store the selected answer
            score = answer_scores[user_answer]
            # Handle non-integer scores (e.g., strings like "Score")
            if isinstance(score, str):
                score = 0  # or you could handle it differently, like displaying a warning
            user_responses.append((index, user_answer, score))

        submit_button = st.form_submit_button("Submit Answers")

        # Calculate and display the score if the user submits the form
        if submit_button:
            st.session_state.responses.append(user_responses)

            # Initialize a dictionary to store total scores for each attribute
            attribute_scores = {
                'Leadership': 0,
                'Communication': 0,
                'Technical Skills': 0,
                'Problem Solving': 0,
                'Creativity': 0,
                'Teamwork': 0,
                'Decision-Making': 0
            }

            # Aggregate scores by attribute
            for index, answer, score in user_responses:
                attribute = question_attributes.get(index, None)
                if attribute:
                    attribute_scores[attribute] += score

            # Display the scores by attribute in a table
            result_df = pd.DataFrame(
                list(attribute_scores.items()),
                columns=["Attribute", "Score"]
            )
            st.dataframe(result_df)

            # Create a spider chart based on the attribute scores
            scores = list(attribute_scores.values())
            labels = list(attribute_scores.keys())
            fig = create_spider_chart(scores, labels)
            st.plotly_chart(fig)

if __name__ == "__main__":
    app()
