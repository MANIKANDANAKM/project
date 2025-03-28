from flask import Flask, render_template, request, jsonify
import pandas as pd
import os
import google.generativeai as genai  

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Configure Google Generative AI (Gemini)
genai.configure(api_key="AIzaSyCN3kjQunheAjIEfGlFGFjrshGXC3C8I1s")  # Replace with your valid API key

generation_config = {
    "temperature": 0.9,
    "top_p": 1,
    "top_k": 1,
    "max_output_tokens": 2048,
}

safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_ONLY_HIGH"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_ONLY_HIGH"},
]

# Use correct model name (Check with list_models())
modelai = genai.GenerativeModel(
    model_name="gemini-1.5-pro",  # Change based on available models
    generation_config=generation_config,
    safety_settings=safety_settings,
)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/try-now')
def try_now():
    return render_template('trynow.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if not file.filename.endswith('.csv'):  # Ensure only CSV files are processed
        return jsonify({'error': 'Only CSV files are supported'}), 400

    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)
    
    try:
        insights = generate_ai_insights(filepath)
        return jsonify(insights)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def generate_ai_insights(filepath):
    """Reads medical records and generates AI-driven recommendations using Gemini AI."""
    df = pd.read_csv(filepath)

    if df.empty:
        return {"error": "Uploaded file is empty."}

    # Extract key medical indicators (ignoring non-numeric columns)
    relevant_data = df.mean(numeric_only=True).to_dict()

    # Calculate Parkinson's likelihood (simple threshold-based classification)
    risk_factors = [
        relevant_data.get("Tremor Intensity (1-10)", 0),
        relevant_data.get("Muscle Rigidity (1-10)", 0),
        relevant_data.get("Walking Difficulty (1-10)", 0),
        relevant_data.get("Handwriting Changes (1-10)", 0),
        relevant_data.get("Memory Issues (1-10)", 0),
    ]
    
    average_severity = sum(risk_factors) / len(risk_factors)
    
    if average_severity > 6:
        parkinsons_diagnosis = "Diagnosis: The person has Parkinson's disease"
    else:
        parkinsons_diagnosis = "Diagnosis: The person does not have Parkinson's disease"

    # Convert data to text format for AI processing
    medical_summary = "\n".join([f"{k}: {v:.2f}" for k, v in relevant_data.items()])

    # Call Gemini AI for lifestyle recommendations
    prompt = f"""
    A patient uploaded medical records with these key indicators:
    {medical_summary}
    
    {parkinsons_diagnosis}
    
    Based on this, generate personalized lifestyle recommendations, including:
    - Diet suggestions
    - Exercise routines
    - Stress management techniques
    - Potential health risks
    
    Format the response as a friendly, readable text.
    """

    response = modelai.generate_content(prompt)  # Fixed generate_content() usage
    
    insights = response.text if response else "No recommendations available."
    
    return {
        "message": "AI-generated personalized lifestyle recommendations!",
        "diagnosis": parkinsons_diagnosis,
        "insights": insights
    }

if __name__ == '__main__':
    app.run(debug=True)
