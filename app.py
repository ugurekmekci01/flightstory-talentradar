import streamlit as st
import pandas as pd
import json
import random
import plotly.graph_objects as go

# Load survey template
def load_survey():
    with open("scorechart.json", "r") as file:
        return json.load(file)

survey_data = load_survey()

# Sample data for ranking and percentiles
def get_sample_ranking():
    total_participants = 150
    user_rank = random.randint(1, total_participants)
    percentile = round((1 - (user_rank / total_participants)) * 100, 1)
    return user_rank, total_participants, percentile

def compute_scores(responses):
    category_scores = {}
    total_score = 0
    
    for question, answer in responses.items():
        for q in survey_data['questions']:
            if q['question'] == question:
                idx = q['answers'].index(answer)
                score = q['scores'][idx]
                total_score += score
                
                for category in q['categories']:
                    if category not in category_scores:
                        category_scores[category] = 0
                    category_scores[category] += score
    
    return total_score, category_scores

def show_gauge_chart(score, full_name):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        title={'text': full_name, 'font': {'size': 24}},
        gauge={
            'axis': {'range': [-50, 250]},
            'steps': [
                {'range': [-50, 50], 'color': "red"},
                {'range': [50, 100], 'color': "orange"},
                {'range': [100, 175], 'color': "yellow"},
                {'range': [175, 250], 'color': "green"}
            ],
        }
    ))
    st.markdown("<div style='display: flex; justify-content: center;'>", unsafe_allow_html=True)
    st.plotly_chart(fig)
    st.markdown("</div>", unsafe_allow_html=True)

def show_top_skills(category_scores):
    top_skills = sorted(category_scores.items(), key=lambda x: x[1], reverse=True)[:6]
    for skill, score in top_skills:
        st.markdown(f"<h4 style='text-align: center;'>{skill}: {score}</h4>", unsafe_allow_html=True)
        st.progress(min(max(score / 10, 0), 1))

def main():
    st.title("📋 Survey App with Scoring & Analysis")
    
    with st.form("survey_form"):
        first_name = st.text_input("First Name")
        last_name = st.text_input("Last Name")
        email = st.text_input("Email")
        in_office = st.toggle("🏢 In-Office?")
        
        responses = {}
        for q in survey_data['questions']:
            responses[q['question']] = st.radio(q['question'], q['answers'])
        
        submitted = st.form_submit_button("Submit Survey")
    
    if submitted:
        full_name = f"{first_name} {last_name}".strip()
        total_score, category_scores = compute_scores(responses)    
        user_rank, total_participants, percentile = get_sample_ranking()
        
        #st.subheader("🏆 Total Score & Ranking")
        st.markdown(f"<h2 style='text-align: center;'>Total Score: {total_score}</h2>", unsafe_allow_html=True)
        st.markdown(f"<h3 style='text-align: center;'>Ranking: {user_rank} out of {total_participants} participants</h3>", unsafe_allow_html=True)
        st.markdown(f"<h3 style='text-align: center;'>You are in the top {percentile}% of participants!</h3>", unsafe_allow_html=True)
        
        #st.subheader("🎯 Performance Score Gauge")
        show_gauge_chart(total_score, full_name)
        
        #st.subheader("🏢 Work Status")
        st.markdown(f"<h3 style='text-align: center;'>{'✅ In-Office' if in_office else '🏠 Remote'}</h3>", unsafe_allow_html=True)
        
        #st.subheader("🏅 Top 6 Skills")
        show_top_skills(category_scores)
        
        st.subheader("📝 Survey Responses")
        df = pd.DataFrame({
            "Question": list(responses.keys()),
            "Selected Answer": list(responses.values()),
        })
        st.markdown("<div style='display: flex; justify-content: center;'>", unsafe_allow_html=True)
        st.dataframe(df)
        st.markdown("</div>", unsafe_allow_html=True)
        
if __name__ == "__main__":
    main()
