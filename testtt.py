import plotly.express as px
import pandas as pd

def create_dummy_chart(output_path="dummy_chart.png"):
    # Create dummy data
    df = pd.DataFrame({
        "Category": ["A", "B", "C", "D", "E"],
        "Value": [10, 20, 15, 25, 30]
    })
    
    # Create a bar chart
    fig = px.bar(df, x="Category", y="Value", title="Dummy Chart")
    
    # Save the chart as a PNG image
    fig.write_image(output_path)

    return output_path

# Generate and save the dummy chart
dummy_chart_path = create_dummy_chart()
print(f"Dummy chart saved at: {dummy_chart_path}")
