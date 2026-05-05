from flask import Flask, request, jsonify, render_template
from nlp import extract_symptoms
from bayesian_model import infer_disease

# PDF imports
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

from datetime import datetime

app = Flask(__name__)

#  CASE STORAGE
case_history = []


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.json
    text = data.get("text", "")

    symptoms = extract_symptoms(text)

    # ✅ FIX: Handle unknown / no symptoms
    if not symptoms:
        return jsonify({
            "symptoms": [],
            "prediction": {},
            "logic": [],
            "summary": "No relevant symptoms detected. Unable to provide diagnosis."
        })

    prediction = infer_disease(symptoms)

    # ---------------- LOGIC EXPLANATION ----------------
    logic = []

    if "fever" in symptoms:
        logic.append("Fever → Flu")

    if "cough" in symptoms:
        logic.append("Cough → Flu / Cold")

    if "fatigue" in symptoms:
        logic.append("Fatigue → Flu")

    if "chest pain" in symptoms:
        logic.append("Chest Pain → Pneumonia")

    if "headache" in symptoms:
        logic.append("Headache → Migraine")

    if "back pain" in symptoms:
        logic.append("Back Pain → Injury")

    # ---------------- FILTER LOW VALUES ----------------
    filtered_prediction = {
        d: p for d, p in prediction.items() if p > 0.05
    }

    # ---------------- DIAGNOSIS SUMMARY ----------------
    if filtered_prediction:
        top_disease = max(filtered_prediction, key=filtered_prediction.get)
        top_prob = filtered_prediction[top_disease]

        if top_prob > 0.7:
            confidence = "high"
        elif top_prob > 0.4:
            confidence = "moderate"
        else:
            confidence = "low"

        summary = f"Based on the symptoms, the most likely condition is {top_disease} with {confidence} confidence."
    else:
        summary = "Symptoms detected, but no strong disease prediction."

    # ---------------- SAVE CASE ----------------
    case = {
        "symptoms": symptoms,
        "prediction": filtered_prediction,
        "summary": summary,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    case_history.append(case)

    # ---------------- RESPONSE ----------------
    return jsonify({
        "symptoms": symptoms,
        "prediction": filtered_prediction,
        "logic": logic,
        "summary": summary
    })


# ---------------- GET CASE HISTORY ----------------
@app.route("/cases", methods=["GET"])
def get_cases():
    return jsonify(case_history)


# ---------------- PDF REPORT ROUTE ----------------
@app.route("/report", methods=["POST"])
def generate_report():
    data = request.json

    symptoms = data.get("symptoms", [])
    prediction = data.get("prediction", {})
    summary = data.get("summary", "")
    logic = data.get("logic", [])

    doc = SimpleDocTemplate("report.pdf")
    styles = getSampleStyleSheet()

    elements = []

    elements.append(Paragraph("MediLogic AI Report", styles["Title"]))
    elements.append(Spacer(1, 10))

    elements.append(Paragraph("Symptoms: " + ", ".join(symptoms), styles["Normal"]))
    elements.append(Spacer(1, 10))

    elements.append(Paragraph("Predictions:", styles["Heading2"]))
    for d, p in prediction.items():
        elements.append(Paragraph(f"{d}: {p}", styles["Normal"]))

    elements.append(Spacer(1, 10))

    elements.append(Paragraph("Summary:", styles["Heading2"]))
    elements.append(Paragraph(summary, styles["Normal"]))

    elements.append(Spacer(1, 10))

    elements.append(Paragraph("Reasoning:", styles["Heading2"]))
    for l in logic:
        elements.append(Paragraph(l, styles["Normal"]))

    doc.build(elements)

    return jsonify({"message": "Report generated successfully"})


if __name__ == "__main__":
    app.run(debug=True)