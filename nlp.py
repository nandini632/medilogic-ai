import spacy

# Load NLP model
nlp = spacy.load("en_core_web_sm")

# Simple symptom list
SYMPTOMS = [
    "fever",
    "cough",
    "chest pain",
    "fatigue",
    "headache",
    "back pain"
]

def extract_symptoms(text):
    text = text.lower()
    found = []

    for symptom in SYMPTOMS:
        if symptom in text:
            found.append(symptom)

    return found