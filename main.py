from flask import Flask, render_template, request, redirect, url_for, flash
import json, os

app = Flask(__name__)
app.secret_key = "secret123"

# Load prescriptions.json from same directory as this script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "prescriptions.json")

# Ensure prescriptions.json exists
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump([], f)


def load_prescriptions():
    with open(DATA_FILE, "r") as f:
        data = json.load(f)
    print(f"[DEBUG] Loaded {len(data)} prescriptions")
    for p in data:
        print(f"[DEBUG] Prescription: {p}")
    return data


def save_prescriptions(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/search", methods=["GET", "POST"])
def search_prescriptions():
    results = []
    if request.method == "POST":
        try:
            age = int(request.form["age"])
            weight = float(request.form["weight"])
            input_symptoms = [s.strip().lower() for s in request.form["symptoms"].split(",")]

            prescriptions = load_prescriptions()
            for p in prescriptions:
                age_min = int(p["age_min"])
                age_max = int(p["age_max"])
                weight_min = float(p["weight_min"])
                weight_max = float(p["weight_max"])
                pres_symptoms = [s.lower() for s in p["symptoms"]]

                if (age_min <= age <= age_max and
                    weight_min <= weight <= weight_max and
                    any(sym in pres_symptoms for sym in input_symptoms)):
                    results.append({
                        "medicine": p["medicine"],
                        "dosage": p["dosage"],
                        "age_min": age_min,
                        "age_max": age_max,
                        "weight_min": weight_min,
                        "weight_max": weight_max,
                        "symptoms": p["symptoms"]
                    })

            if not results:
                print("[DEBUG] No matching prescription found.")
                flash("No matching prescription found.", "warning")

        except ValueError as ve:
            flash(f"Input Error: {ve}", "danger")
            print(f"[DEBUG] Value Error: {ve}")
        except Exception as e:
            flash(f"Unexpected Error: {e}", "danger")
            print(f"[DEBUG] Exception during search: {e}")

    print(f"[DEBUG] Search results: {results}")
    return render_template("search.html", results=results)


@app.route("/upload", methods=["GET", "POST"])
def upload_prescriptions():
    if request.method == "POST":
        try:
            # Get and validate inputs
            medicine = request.form["medicine"].strip()
            dosage = request.form["dosage"].strip()
            if not medicine or not dosage:
                raise ValueError("Medicine and dosage cannot be empty.")

            # Convert age and weight safely
            age_min = int(request.form["age_min"])
            age_max = int(request.form["age_max"])
            weight_min = float(request.form["weight_min"])
            weight_max = float(request.form["weight_max"])

            if age_min > age_max:
                raise ValueError("Minimum age cannot be greater than maximum age.")
            if weight_min > weight_max:
                raise ValueError("Minimum weight cannot be greater than maximum weight.")

            # Process symptoms into a clean list
            symptoms = [s.strip() for s in request.form["symptoms"].split(",") if s.strip()]
            if not symptoms:
                raise ValueError("At least one symptom must be provided.")

            # Load existing prescriptions
            prescriptions = load_prescriptions()

            # Append new prescription in proper format
            prescriptions.append({
                "medicine": medicine,
                "dosage": dosage,
                "age_min": age_min,
                "age_max": age_max,
                "weight_min": weight_min,
                "weight_max": weight_max,
                "symptoms": symptoms
            })

            # Save back to JSON
            save_prescriptions(prescriptions)
            flash("Prescription uploaded successfully!", "success")
            print(f"[DEBUG] Uploaded prescription: {prescriptions[-1]}")
            return redirect(url_for("upload_prescriptions"))

        except ValueError as ve:
            flash(f"Input Error: {ve}", "danger")
            print(f"[DEBUG] Value Error: {ve}")
        except Exception as e:
            flash(f"Unexpected Error: {e}", "danger")
            print(f"[DEBUG] Exception during upload: {e}")

    return render_template("upload.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
