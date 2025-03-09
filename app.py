import streamlit as st
import pandas as pd
import json
import random
import plotly.graph_objects as go
import os

from PIL import Image
import io

import send_telegram

# Load survey template
def load_survey():
    with open("scorechart.json", "r") as file:
        return json.load(file)

survey_data = load_survey()

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

def get_alignment_description(score):
    if score >= 55:
        return "Very Strong Alignment"
    elif 45 <= score < 55:
        return "Strong Alignment"
    elif 35 <= score < 45:
        return "Aligned"
    elif 25 <= score < 35:
        return "Low Alignment"
    elif 15 <= score < 25:
        return "Poor Alignment"
    else:
        return "Unaligned"

import plotly.io as pio
from PIL import Image, ImageDraw, ImageFont

def show_gauge_chart(score, full_name, save_as_image=False):
    alignment_description = get_alignment_description(score)
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        title={'text': full_name, 'font': {'size': 24}},
        number={'suffix': f"/100"},
        gauge={
            'axis': {'range': [0, 100]},
            'steps': [
                {'range': [0, 15], 'color': "red"},
                {'range': [15, 50], 'color': "orange"},
                {'range': [45, 55], 'color': "yellow"},
                {'range': [55, 100], 'color': "lightgreen"},
            ],
            'bar': {'color': "white", 'thickness': 0.3}
        }
    ))
    
    if save_as_image:
        # Save Plotly chart as image
        image_path = "gauge_chart.png"
        fig.write_image(image_path)

        # Open the image using PIL
        image = Image.open(image_path)
        draw = ImageDraw.Draw(image)

        # Define font (fallback to default if not found)
        font_path = "/Users/ugurekmekci/VSCodeProjects/flightstory-talentradar/Arial.ttf"
        try:
            font = ImageFont.truetype(font_path, 24)  # Adjust size if needed
        except IOError:
            font = ImageFont.load_default()
            print("Font not found, using default.")


        # Get image dimensions
        img_width, img_height = image.size
        text_position = (img_width // 2, img_height - 50)  # Position near bottom

        # Add text overlay
        text_color = "black"
        draw.text(text_position, alignment_description, font=font, fill=text_color, anchor="mm", stroke_width=2, stroke_fill="white")


        # Save updated image
        image.save(image_path)
        return image_path

    # Show in Streamlit if not saving
    st.markdown("<div style='display: flex; justify-content: center;'>", unsafe_allow_html=True)
    st.plotly_chart(fig)
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown(f"<h4 style='text-align: center; color: #888;'>{alignment_description}</h4>", unsafe_allow_html=True)


def show_top_skills(category_scores):
    top_skills = sorted(category_scores.items(), key=lambda x: x[1], reverse=True)[:6]
    for skill, score in top_skills:
        col1, col2 = st.columns([1.5, 4])
        with col1:
            st.markdown(f"<p style='text-align: left; font-weight: bold; font-size: 18px; margin: 5px 0;'>{skill}</p>", unsafe_allow_html=True)
        with col2:
            st.progress(min(max(score / 10, 0), 1))

def main():
    st.title("📋 Talent Radar PoC")
    
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
        
        show_gauge_chart(total_score, full_name)
        st.markdown(f"<h2 style='text-align: center;'>Total Score: {total_score}/100</h2>", unsafe_allow_html=True)
        st.markdown(f"<h3 style='text-align: center;'>{'✅ In-Office' if in_office else '🏠 Remote'}</h3>", unsafe_allow_html=True)
        show_top_skills(category_scores)
        
        st.subheader("📝 Survey Responses")
        df = pd.DataFrame({
            "Question": list(responses.keys()),
            "Selected Answer": list(responses.values()),
        })
        st.dataframe(df)
    
    st.subheader("🎯 Simulate Score")
    score_input = st.number_input("Enter a score (0-100):", min_value=0, max_value=100, value=50)
    
    if st.button("Simulate"):
        alignment_description = get_alignment_description(score_input)
        message = f"Simulation complete! Score: {score_input}/100\nAlignment: {alignment_description}"
        image_path = show_gauge_chart(score_input, "Isa May", save_as_image=True)
        st.image(image_path, use_container_width=True)

        status = random.choice(["✅ In-Office", "🏠 Remote"])
        st.markdown(f"<h3 style='text-align: center;'>{status}</h3>", unsafe_allow_html=True)

        show_top_skills({
            "Simulated Skill 1": max(score_input / 10, 0.1),
            "Simulated Skill 2": max(score_input / 10, 0.1),
            "Simulated Skill 3": max(score_input / 9, 0.1),
            "Simulated Skill 4": max(score_input / 10, 0.1),
            "Simulated Skill 5": max(score_input / 9, 0.1),
            "Simulated Skill 6": max(score_input / 10, 0.1)
        })

        if score_input >= 55:
            send_telegram.send_to_telegram(message, image_path)
        #os.remove(image_path)
        
        
if __name__ == "__main__":
    main()
