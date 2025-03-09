import streamlit as st
import pandas as pd
import json
import random
import plotly.graph_objects as go
import os
from PIL import Image, ImageDraw, ImageFont
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

def show_gauge_chart(score, full_name, in_office_status=None, top_skills=None, save_as_image=False):
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
        img_width, img_height = image.size

        # Increase the height to accommodate bars
        new_height = img_height + 200  # Adjust this value as needed
        new_image = Image.new("RGB", (img_width, new_height), "white")
        new_image.paste(image, (0, 0))

        # Draw on the new image
        draw = ImageDraw.Draw(new_image)

        # Define font (fallback to default if not found)
        font_path = "/Users/ugurekmekci/VSCodeProjects/flightstory-talentradar/Arial.ttf"
        try:
            font = ImageFont.truetype(font_path, 24)  # Adjust size if needed
        except IOError:
            font = ImageFont.load_default()
            print("Font not found, using default.")


        # Add top skills as horizontal bars
        if top_skills:
            skill_bar_height = 20  # Height of each bar
            skill_bar_spacing = 40  # Spacing between bars
            skill_bar_start_y = img_height + 20  # Start drawing bars closer to the gauge chart

            # Calculate maximum skill name width for alignment
            max_skill_width = max([draw.textlength(skill, font=font) for skill in top_skills.keys()])
            bar_start_x = 50 + max_skill_width + 20  # Bars start after skill names with padding
            bar_end_x = img_width - 50  # Bars stretch to the right edge with padding

            # Ensure there's enough space for all bars
            total_bars_height = len(top_skills) * skill_bar_spacing
            if skill_bar_start_y + total_bars_height > new_height:
                new_height = skill_bar_start_y + total_bars_height + 20  # Add extra padding
                new_image = Image.new("RGB", (img_width, new_height), "white")
                new_image.paste(image, (0, 0))
                image = new_image
                draw = ImageDraw.Draw(image)

            for i, (skill, score) in enumerate(top_skills.items()):
                skill_bar_y = skill_bar_start_y + i * skill_bar_spacing
                rounded_score = round(score, 1)
                
                # Draw the skill name
                draw.text(
                    (50, skill_bar_y),  # Skill names start at x=50
                    f"{skill}", 
                    font=font, 
                    fill="black"
                )
                
                # Draw the bar
                bar_width = (bar_end_x - bar_start_x) * (rounded_score / 10)  # Stretch bar based on score
                draw.rectangle(
                    [(bar_start_x, skill_bar_y), 
                    (bar_start_x + bar_width, skill_bar_y + skill_bar_height)], 
                    fill="lightblue"
                )
                
                # Draw the score at the end of the bar
                draw.text(
                    (bar_end_x + 10, skill_bar_y),  # Scores are placed to the right of the bars
                    f"{rounded_score}", 
                    font=font, 
                    fill="black"
                )

        # Add alignment description
        text_position = (img_width // 2, img_height - 50)  # Position near bottom
        text_color = "lightblue"
        draw.text(text_position, alignment_description, font=font, fill="black", anchor="mm")

        # Add in-office status
        status_text = f"{'In-Office' if in_office_status else 'Remote'}"
        status_position = (img_width // 2, img_height - 20)
        status_color = "green" if in_office_status else "orange"  # Green for In-Office, Yellow for Remote
        draw.text(status_position, status_text, font=font, fill=status_color, anchor="mm")
                
        # Save updated image
        new_image.save(image_path)
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
        status = random.choice([True, False])
        top_skills = {
            "Skill 1": max(score_input / 10, 0.1),
            "Skill 2": max(score_input / 10, 0.1),
            "Skill 3": max(score_input / 9, 0.1),
            "Skill 4": max(score_input / 10, 0.1),
            "Skill 5": max(score_input / 9, 0.1),
            "Skill 6": max(score_input / 10, 0.1)
        }
        show_gauge_chart(score_input, "Isa May")
        image_path = show_gauge_chart(score_input, "Isa May", in_office_status=status, top_skills=top_skills, save_as_image=True)
        #st.image(image_path, use_container_width=True)

        st.markdown(f"<h3 style='text-align: center;'>{'✅ In-Office' if status else '🏠 Remote'}</h3>", unsafe_allow_html=True)

        show_top_skills(top_skills)

        if score_input >= 55:
            send_telegram.send_to_telegram(message, image_path)
        # #os.remove(image_path)
        
        
if __name__ == "__main__":
    main()