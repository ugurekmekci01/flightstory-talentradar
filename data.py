import pandas as pd
import json

# Load the Excel file
file_path = 'Scoring system.xlsx'  # Replace with your file path
df = pd.read_excel(file_path, header=None)  # Assuming no header in the Excel file

# Initialize variables
questions = []
current_question = None
current_answers = []
current_scores = []

# Iterate through the rows
for index, row in df.iterrows():
    if pd.notna(row[0]) and row[0].startswith(("Question", "Would you like")):  # Skip metadata rows
        continue
    if pd.notna(row[0]):  # Check if the question column has data
        if current_question:  # Save the previous question and its answers/scores
            questions.append({
                "question": current_question,
                "answers": current_answers,
                "scores": current_scores
            })
        current_question = row[0]  # New question
        current_answers = []  # Reset answers
        current_scores = []  # Reset scores
        # Add the first answer and score (from the same row as the question)
        if pd.notna(row[1]):  # Check if the answer column has data
            current_answers.append(row[1])  # Add first answer
            current_scores.append(row[2])  # Add corresponding score
    elif pd.notna(row[1]):  # Check if the answer choices column has data
        current_answers.append(row[1])  # Add subsequent answer
        current_scores.append(row[2])  # Add corresponding score

# Add the last question and its answers/scores
if current_question:
    questions.append({
        "question": current_question,
        "answers": current_answers,
        "scores": current_scores
    })

# Convert to JSON-like structure
json_data = {"questions": questions}

# Print the JSON-like structure
print(json.dumps(json_data, indent=4))

# Optionally, save to a JSON file
with open('output2.json', 'w') as f:
    json.dump(json_data, f, indent=4)