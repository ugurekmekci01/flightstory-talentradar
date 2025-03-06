import pandas as pd
import json

def excel_to_json(excel_file, json_file):
    # Load the Excel file
    df = pd.read_excel(excel_file, engine='openpyxl')
    
    # Group by question and category to maintain structure
    questions = []
    for (question, category), group in df.groupby(["Question", "Category"]):
        questions.append({
            "question": question,
            "categories": category.split(", "),  # Convert category back to list
            "answers": group["Answer"].tolist(),
            "scores": group["Score"].tolist()
        })
    
    # Create JSON structure
    data = {"questions": questions}
    
    # Save to JSON file
    with open(json_file, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)
    
    print(f"JSON file saved as {json_file}")

# Example usage
excel_file = "/Users/ugurekmekci/VSCodeProjects/flightstory-talentradar/surway_scorechart.xlsx"  # Replace with actual Excel file
json_file = "scorechart.json"  # Desired output JSON file name
excel_to_json(excel_file, json_file)
