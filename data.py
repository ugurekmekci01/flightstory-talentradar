import json
import pandas as pd

def excel_to_json(excel_file, json_file):
    # Load the Excel file
    df = pd.read_excel(excel_file, engine='openpyxl')
    
    # Ensure questions appear in the same order as in Excel
    df["Order"] = df.index  # Add an index column to track original order
    
    # Group by question and category, but **disable sorting**
    questions = []
    for (question, category), group in df.groupby(["Question", "Category"], sort=False):  
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
json_file = "scorechart2.json"  # Desired output JSON file name
excel_to_json(excel_file, json_file)



excel_file = "/Users/ugurekmekci/VSCodeProjects/flightstory-talentradar/surway_scorechart.xlsx"  # Replace with actual Excel file
json_file = "scorechart2.json"  # Desired output JSON file name
excel_to_json(excel_file, json_file)