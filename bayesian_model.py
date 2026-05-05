from pgmpy.models import DiscreteBayesianNetwork as BayesianNetwork
from pgmpy.factors.discrete import TabularCPD
from pgmpy.inference import VariableElimination


def create_model():
    model = BayesianNetwork([
        ("Fever", "Flu"),
        ("Cough", "Flu"),
        ("Fatigue", "Flu"),

        ("Cough", "Cold"),

        ("ChestPain", "Pneumonia"),
        ("Cough", "Pneumonia"),

        ("Headache", "Migraine"),

        ("BackPain", "Injury")
    ])

    # ---------------- SYMPTOM PROBABILITIES ----------------
    cpd_fever = TabularCPD("Fever", 2, [[0.7], [0.3]])
    cpd_cough = TabularCPD("Cough", 2, [[0.6], [0.4]])
    cpd_chest = TabularCPD("ChestPain", 2, [[0.8], [0.2]])
    cpd_fatigue = TabularCPD("Fatigue", 2, [[0.6], [0.4]])
    cpd_headache = TabularCPD("Headache", 2, [[0.7], [0.3]])
    cpd_back = TabularCPD("BackPain", 2, [[0.8], [0.2]])

    # ---------------- DISEASE PROBABILITIES ----------------

    # Flu (depends on Fever, Cough, Fatigue)
    cpd_flu = TabularCPD(
        "Flu", 2,
        [
            [0.9, 0.7, 0.6, 0.4, 0.5, 0.3, 0.2, 0.1],
            [0.1, 0.3, 0.4, 0.6, 0.5, 0.7, 0.8, 0.9]
        ],
        evidence=["Fever", "Cough", "Fatigue"],
        evidence_card=[2, 2, 2]
    )

    # Pneumonia (ChestPain + Cough)
    cpd_pneumonia = TabularCPD(
        "Pneumonia", 2,
        [
            [0.95, 0.5, 0.4, 0.1],
            [0.05, 0.5, 0.6, 0.9]
        ],
        evidence=["ChestPain", "Cough"],
        evidence_card=[2, 2]
    )

    # Cold (Cough only)
    cpd_cold = TabularCPD(
        "Cold", 2,
        [
            [0.8, 0.3],
            [0.2, 0.7]
        ],
        evidence=["Cough"],
        evidence_card=[2]
    )

    # Migraine (Headache)
    cpd_migraine = TabularCPD(
        "Migraine", 2,
        [
            [0.9, 0.2],
            [0.1, 0.8]
        ],
        evidence=["Headache"],
        evidence_card=[2]
    )

    # Injury (BackPain)
    cpd_injury = TabularCPD(
        "Injury", 2,
        [
            [0.9, 0.2],
            [0.1, 0.8]
        ],
        evidence=["BackPain"],
        evidence_card=[2]
    )

    # ---------------- ADD CPDs ----------------
    model.add_cpds(
        cpd_fever, cpd_cough, cpd_chest,
        cpd_fatigue, cpd_headache, cpd_back,
        cpd_flu, cpd_pneumonia,
        cpd_cold, cpd_migraine, cpd_injury
    )

    model.check_model()
    return model


def infer_disease(symptoms):
    model = create_model()
    infer = VariableElimination(model)

    evidence = {
        "Fever": 1 if "fever" in symptoms else 0,
        "Cough": 1 if "cough" in symptoms else 0,
        "ChestPain": 1 if "chest pain" in symptoms else 0,
        "Fatigue": 1 if "fatigue" in symptoms else 0,
        "Headache": 1 if "headache" in symptoms else 0,
        "BackPain": 1 if "back pain" in symptoms else 0
    }

    return {
        "Flu": round(float(infer.query(["Flu"], evidence=evidence).values[1]), 3),
        "Pneumonia": round(float(infer.query(["Pneumonia"], evidence=evidence).values[1]), 3),
        "Cold": round(float(infer.query(["Cold"], evidence=evidence).values[1]), 3),
        "Migraine": round(float(infer.query(["Migraine"], evidence=evidence).values[1]), 3),
        "Injury": round(float(infer.query(["Injury"], evidence=evidence).values[1]), 3)
    }