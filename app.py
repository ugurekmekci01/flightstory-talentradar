import streamlit as st
import pandas as pd
import json
import plotly.express as px
import random

# Load the survey questions from the JSON file
def load_survey_data(json_file="scorechart.json"):
    with open(json_file, "r") as file:
        return json.load(file)

# Calculate the total score and category scores for the respondent
def calculate_scores(data, responses):
    category_scores = {}
    total_score = 0
    for q in data["questions"]:
        score = responses[q["question"]]
        for category in q["categories"]:
            category_scores[category] = category_scores.get(category, 0) + score
            total_score += score
    return total_score, category_scores

def plot_category_scores(df, width=800, height=600):
    # Ensure the column exists
    if "CategoryScores" not in df.columns:
        raise ValueError("DataFrame must contain a 'CategoryScores' column")
    
    # Convert dictionary column to a DataFrame
    scores_df = pd.DataFrame(df["CategoryScores"].iloc[0].items(), columns=["Category", "Score"])
    
    # Sort by score in descending order
    scores_df = scores_df.sort_values(by="Score", ascending=False)
    
    # Create interactive bar chart using Plotly
    fig = px.bar(scores_df, x="Score", y="Category", orientation='h',
                 color="Score", color_continuous_scale="RdBu_r",
                 title="Category Scores (Descending Order)")
    fig.update_layout(xaxis_title="Score", yaxis_title="Category", template="plotly_white",
                      width=width, height=height)
    
    return fig


# Enrich the data with additional information like best/worst categories
def enrich_data(total_score, category_scores):
    best_category = max(category_scores, key=category_scores.get)
    worst_category = min(category_scores, key=category_scores.get)
    best_score = category_scores[best_category]
    worst_score = category_scores[worst_category]
    return [total_score, category_scores, best_category, worst_category, best_score, worst_score]

# Visualization functions
def plot_position_among_candidates(df_all_results, current_respondent_score, width=800, height=600):
    # Sort by TotalScore
    df_all_results_sorted = df_all_results.sort_values(by="TotalScore", ascending=False)
    
    # Find the rank of the current respondent
    rank = df_all_results_sorted[df_all_results_sorted["FullName"] == current_respondent_score["FullName"]].index[0] + 1
    total_respondents = len(df_all_results_sorted)

    # Rank chart
    fig = px.bar(df_all_results_sorted.head(10), x="FullName", y="TotalScore", 
                 color="TotalScore", title=f"Ranking of Current Respondent: {rank}/{total_respondents}")
    fig.update_layout(xaxis_title="Respondent", yaxis_title="Total Score", template="plotly_white",
                      width=width, height=height)
    
    return fig

def plot_top_performers(df_all_results, width=800, height=600):
    # Sort by TotalScore
    df_all_results_sorted = df_all_results.sort_values(by="TotalScore", ascending=False)
    df_top_5 = df_all_results_sorted.head(5)

    # Top performers chart
    fig = px.bar(df_top_5, x="FullName", y="TotalScore", 
                 color="TotalScore", title="Top 5 Performers")
    fig.update_layout(xaxis_title="Respondent", yaxis_title="Total Score", template="plotly_white",
                      width=width, height=height)
    
    return fig

def plot_category_comparison(df_all_results, current_respondent, width=800, height=600):
    # Find current respondent's category scores
    top_scores = pd.DataFrame(current_respondent["CategoryScores"].items(), columns=["Category", "Score"])
    
    # Aggregate category scores for historical data (average)
    category_means = df_all_results["CategoryScores"].apply(pd.Series).mean()
    category_means_df = category_means.reset_index(name="AvgScore")
    
    # Merge top respondent scores with historical data
    comparison_df = pd.merge(top_scores, category_means_df, left_on="Category", right_on="index", how="left")
    comparison_df = comparison_df.rename(columns={"Score": "Respondent Score", "AvgScore": "Average Score"})
    
    # Plot comparison
    fig = px.bar(comparison_df, x="Category", y=["Respondent Score", "Average Score"], barmode="group",
                 title="Respondent vs Historical Data (Category Scores)")
    fig.update_layout(xaxis_title="Category", yaxis_title="Score", template="plotly_white",
                      width=width, height=height)
    
    return fig

def plot_top_6_categories(df, width=800, height=600):
    # Ensure the column exists
    if "CategoryScores" not in df.columns:
        raise ValueError("DataFrame must contain a 'CategoryScores' column")
    
    # Convert dictionary column to a DataFrame
    scores_df = pd.DataFrame(df["CategoryScores"].iloc[0].items(), columns=["Category", "Score"])
    
    # Sort by score in descending order and take the top 6 categories
    scores_df = scores_df.sort_values(by="Score", ascending=False).head(6)
    
    # Create interactive bar chart using Plotly
    fig = px.bar(scores_df, x="Score", y="Category", orientation='h',
                 color="Score", color_continuous_scale="RdBu_r",
                 title="Top 6 Categories of the Respondent")
    fig.update_layout(xaxis_title="Score", yaxis_title="Category", template="plotly_white",
                      width=width, height=height)
    
    return fig

def plot_category_distribution(df_all_results, width=800, height=600):
    # Box plot showing the distribution of category scores
    category_scores = df_all_results["CategoryScores"].apply(pd.Series)
    fig = px.box(category_scores, points="all", title="Category Score Distribution Across All Respondents")
    fig.update_layout(xaxis_title="Category", yaxis_title="Score", template="plotly_white", 
                      width=width, height=height)
    
    return fig


def generate_fake_data(num_records=10):
    fake_data = []
    categories = ["Patience", "Leadership", "Decision-Making", "Risk-Taking", "Ambition", "Teamwork", "Work Ethic"]
    
    for i in range(num_records):
        full_name = f"User {i+1}"
        email = f"user{i+1}@example.com"
        total_score = random.randint(20, 100)
        category_scores = {category: random.randint(1, 10) for category in categories}
        best_category = max(category_scores, key=category_scores.get)
        worst_category = min(category_scores, key=category_scores.get)
        best_score = category_scores[best_category]
        worst_score = category_scores[worst_category]
        
        fake_data.append([full_name, email, total_score, category_scores, best_category, worst_category, best_score, worst_score])
    
    return pd.DataFrame(fake_data, columns=["FullName", "Email", "TotalScore", "CategoryScores", "BestCategory", "WorstCategory", "BestCategoryScore", "WorstCategoryScore"])

# Main Streamlit app logic
def main():
    # Load survey data
    data = load_survey_data()
    
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

    # Generate fake historical data
    if 'df_all_results' not in st.session_state:
        st.session_state.df_all_results = generate_fake_data(10)  # Generate 10 fake records for testing purposes

    # Aggregate Results
    if st.button("Submit"):
        # Calculate scores and enrich data
        total_score, category_scores = calculate_scores(data, responses)
        enriched_data = enrich_data(total_score, category_scores)
        
        # Create the DataFrame for the current submission
        df_new_respondant_result = pd.DataFrame(
            [[full_name, email, total_score, category_scores, enriched_data[2], enriched_data[3], enriched_data[4], enriched_data[5]]],
            columns=["FullName", "Email", "TotalScore", "CategoryScores", "BestCategory", "WorstCategory", "BestCategoryScore", "WorstCategoryScore"]
        )
        
        # Store in session state for historical tracking
        st.session_state.df_all_results = pd.concat([st.session_state.df_all_results, df_new_respondant_result], ignore_index=True)

        # Display the results
        st.dataframe(df_new_respondant_result)
        
        # Display Business Stakeholder Charts
        st.title("Top 6 Categories of the Respondent")
        st.plotly_chart(plot_top_6_categories(df_new_respondant_result))

        st.title("Ranking of Current Respondent Among All Candidates")
        st.plotly_chart(plot_position_among_candidates(st.session_state.df_all_results, df_new_respondant_result.iloc[0]))

        st.title("Top 5 Performers")
        st.plotly_chart(plot_top_performers(st.session_state.df_all_results))

        st.title("Category Comparison: Current Submission vs Historical Data")
        st.plotly_chart(plot_category_comparison(st.session_state.df_all_results, df_new_respondant_result.iloc[0]))

        st.title("Category Score Distribution Across All Respondents")
        st.plotly_chart(plot_category_distribution(st.session_state.df_all_results))


# Run the app
if __name__ == "__main__":
    main()