import streamlit as st
import pandas as pd
import json
import plotly.express as px
import plotly.graph_objects as go
import random, glob, os
from send_telegram import send_to_telegram


# Load survey questions from JSON file
def load_survey_data(json_file="scorechart.json"):
    with open(json_file, "r") as file:
        return json.load(file)


# Calculate total score and category scores
def calculate_scores(data, responses):
    category_scores = {}
    total_score = 0
    for q in data["questions"]:
        score = responses[q["question"]]
        for category in q["categories"]:
            category_scores[category] = category_scores.get(category, 0) + score
            total_score += score
    return total_score, category_scores


# Display best performers' personal info in a table
def display_top_performers_table(df_all_results, top_n=5):
    df_sorted = df_all_results.sort_values(by="TotalScore", ascending=False).head(top_n)
    return df_sorted[["FullName", "Email", "TotalScore"]]


# Gauge chart showing respondent's top X% ranking
def plot_top_percentage_chart(df_all_results, current_respondent_score):
    df_all_results_sorted = df_all_results.sort_values(by="TotalScore", ascending=False)
    rank = df_all_results_sorted[df_all_results_sorted["FullName"] == current_respondent_score["FullName"]].index[0] + 1
    total_respondents = len(df_all_results_sorted)
    percentile = (1 - (rank / total_respondents)) * 100

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=percentile,
        title={"text": f"Respondent is in the Top {round(percentile, 2)}% of Participants"},
        gauge={"axis": {"range": [0, 100]}},
    ))

    return fig


# Rotate category comparison chart to horizontal
def plot_category_comparison_horizontal(df_all_results, current_respondent):
    top_scores = pd.DataFrame(current_respondent["CategoryScores"].items(), columns=["Category", "Score"])
    category_means = df_all_results["CategoryScores"].apply(pd.Series).mean()
    category_means_df = category_means.reset_index(name="AvgScore")

    comparison_df = pd.merge(top_scores, category_means_df, left_on="Category", right_on="index", how="left")
    comparison_df = comparison_df.rename(columns={"Score": "Respondent Score", "AvgScore": "Average Score"})

    fig = px.bar(comparison_df, y="Category", x=["Respondent Score", "Average Score"], orientation="h",
                 title="Comparison of Respondent’s Scores Against Historical Averages",
                 barmode="group")

    return fig

def display_respondent_rank(df_all_results, current_respondent_score):
    # Sort the dataset by TotalScore in descending order (higher scores rank higher)
    df_sorted = df_all_results.sort_values(by="TotalScore", ascending=False).reset_index(drop=True)

    # Find the respondent's rank (index + 1 because index starts at 0)
    rank = df_sorted[df_sorted["FullName"] == current_respondent_score["FullName"]].index[0] + 1

    # Get total respondents
    total_respondents = len(df_sorted)

    # Get the respondent's total score
    total_score = current_respondent_score["TotalScore"]

    # Generate the two-line ranking statement
    score_statement = f"🏆 **Total Score: {total_score}**"
    rank_statement = f"📊 **Ranking: {rank}{get_ordinal_suffix(rank)} out of {total_respondents} candidates**"

    return score_statement, rank_statement


def get_ordinal_suffix(n):
    """Returns the ordinal suffix for a given number (e.g., 1 -> '1st', 2 -> '2nd', 3 -> '3rd')"""
    if 11 <= (n % 100) <= 13:
        return "th"
    else:
        return {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")



def get_ordinal_suffix(n):
    """Returns the ordinal suffix for a given number (e.g., 1 -> '1st', 2 -> '2nd', 3 -> '3rd')"""
    if 11 <= (n % 100) <= 13:
        return "th"
    else:
        return {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")



# **NEW** Pie Chart for Respondent’s Strengths (With Labels)
def plot_top_6_strengths_pie(df):
    if "CategoryScores" not in df.columns:
        raise ValueError("DataFrame must contain a 'CategoryScores' column")

    # Convert category scores dictionary to DataFrame
    scores_df = pd.DataFrame(df["CategoryScores"].iloc[0].items(), columns=["Category", "Score"])

    # Sort by descending order and take the top 6 categories
    scores_df = scores_df.sort_values(by="Score", ascending=False).head(6)

    # Create a Pie Chart with labels inside the slices
    fig = px.pie(scores_df, names="Category", values="Score",
                 title="Respondent’s Top 6 Strengths",
                 hole=0.4,
                 color_discrete_sequence=px.colors.qualitative.Set3)

    # Ensure category labels are displayed inside the slices
    fig.update_traces(textinfo="label+percent", insidetextorientation="radial")

    return fig



def plot_top_6_weaknesses_pie(df):
    if "CategoryScores" not in df.columns:
        raise ValueError("DataFrame must contain a 'CategoryScores' column")
    
    # Convert category scores dictionary to DataFrame
    scores_df = pd.DataFrame(df["CategoryScores"].iloc[0].items(), columns=["Category", "Score"])

    # Sort by ascending order and take the lowest 6 categories
    scores_df = scores_df.sort_values(by="Score", ascending=True).head(6)

    # Convert negative scores to positive values for visualization
    scores_df["Score"] = scores_df["Score"].abs()

    # Create a Pie Chart with labels inside the slices
    fig = px.pie(scores_df, names="Category",
                 title="Respondent’s 6 Areas for Improvement",
                 hole=0.4,
                 color_discrete_sequence=px.colors.qualitative.Pastel)

    # Ensure category labels are displayed inside the slices
    fig.update_traces(textinfo="label+percent", insidetextorientation="radial")

    return fig

import plotly.graph_objects as go
import streamlit as st

def plot_gauge_chart(name, score, max_score=100):
    """
    Creates a gauge chart to visualize the respondent's score dynamically.
    
    :param name: Respondent's name from the form
    :param score: Respondent's total score from the form
    :param max_score: Maximum possible score (default 100)
    :return: Plotly figure
    """
    # Define gauge sections
    sections = [
        {"range": [0, 40], "color": "red", "label": "Poor"},
        {"range": [40, 60], "color": "orange", "label": "Fair"},
        {"range": [60, 80], "color": "yellow", "label": "Good"},
        {"range": [80, 100], "color": "green", "label": "Excellent"},
    ]

    # Create gauge chart
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        title={"text": f"<b>{name}</b>", "font": {"size": 24}},
        gauge={
            "axis": {"range": [0, max_score], "tickvals": [-50,-10, 0, 40, 60, 80, 100]},
            "bar": {"color": "black"},  # The needle
            "steps": [{"range": sec["range"], "color": sec["color"]} for sec in sections],
            "threshold": {"line": {"color": "black", "width": 4}, "thickness": 0.75, "value": score},
        }
    ))

    return fig



# Generate fake data for testing
def generate_fake_data(num_records=10):
    fake_data = []
    categories = ["Patience", "Leadership", "Decision-Making", "Risk-Taking", "Ambition", "Teamwork", "Work Ethic"]

    for i in range(num_records):
        full_name = f"User {i+1}"
        email = f"user{i+1}@example.com"
        total_score = random.randint(20, 100)
        category_scores = {category: random.randint(1, 10) for category in categories}

        fake_data.append([full_name, email, total_score, category_scores])

    return pd.DataFrame(fake_data, columns=["FullName", "Email", "TotalScore", "CategoryScores"])


# Streamlit App
def main():
    data = load_survey_data()
    st.title("Survey Form")

    full_name = st.text_input("Full Name")
    email = st.text_input("Email")

    responses = {}
    st.subheader("Answer the questions below:")
    for idx, q in enumerate(data["questions"]):
        response = st.radio(q["question"], q["answers"], key=f"q{idx}")
        responses[q["question"]] = q["scores"][q["answers"].index(response)]

    if 'df_all_results' not in st.session_state:
        st.session_state.df_all_results = generate_fake_data(10)

    if st.button("Submit"):
        for file in glob.glob("charts/*"):
            os.remove(file)
        st.balloons()

        total_score, category_scores = calculate_scores(data, responses)

        df_new_respondent = pd.DataFrame([[full_name, email, total_score, category_scores]],
                                         columns=["FullName", "Email", "TotalScore", "CategoryScores"])
        
        st.session_state.df_all_results = pd.concat([st.session_state.df_all_results, df_new_respondent], ignore_index=True)

        score_statement, rank_statement = display_respondent_rank(st.session_state.df_all_results, df_new_respondent.iloc[0])
        st.markdown(f"### {score_statement}")  # Display total score first
        st.markdown(f"### {rank_statement}")  # Display ranking second

        # 🎯 Display Score Gauge Chart
        st.title("Performance Gauge")
        gauge_chart = plot_gauge_chart(full_name, total_score)
        st.plotly_chart(gauge_chart)

        # Save and send images
        #st.title("Respondent’s Top 6 Strengths")
        fig1 = plot_top_6_strengths_pie(df_new_respondent)
        st.plotly_chart(fig1)
        fig1.write_image("charts/top_6_strengths.png")
        send_to_telegram("🟢 Respondent’s Top 6 Strengths", "charts/top_6_strengths.png")

        #st.title("Respondent’s Weakest 6 Categories")
        fig2 = plot_top_6_weaknesses_pie(df_new_respondent)
        st.plotly_chart(fig2)
        fig2.write_image("charts/weakest_6_categories.png")
        send_to_telegram("🔴 Respondent’s Weakest 6 Categories", "charts/weakest_6_categories.png")

        #st.title("Respondent’s Ranking Among All Participants")
        st.plotly_chart(plot_top_percentage_chart(st.session_state.df_all_results, df_new_respondent.iloc[0]))

        # st.title("Comparison of Respondent’s Scores Against Historical Averages")
        st.plotly_chart(plot_category_comparison_horizontal(st.session_state.df_all_results, df_new_respondent.iloc[0]))

        st.title("Top Performers' Information")
        st.dataframe(display_top_performers_table(st.session_state.df_all_results))


# Run the app
if __name__ == "__main__":
    main()
