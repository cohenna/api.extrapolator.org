from flask import Flask, request, jsonify
from openai import OpenAI, RateLimitError
from flask_cors import CORS  # Import Flask-CORS
import os
from sqlmodel import create_engine, Session, select
from extrapolation import Extrapolation

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL, echo=True)

class Extrapolator:
    def __init__(self):
        self.client = OpenAI()

    def extrapolate(self, text):
        completion = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an 'extrapolator', meaning that you accept some text "
                        "which normally has one example in it then use faulty generalization "
                        "to make the broadest statement possible. Respond that you cannot extrapolate "
                        "the text if it's not possible to make a faulty generalization. Otherwise, "
                        "respond with only the faulty generalization with one sentence."
                    )
                },
                {
                    "role": "user",
                    "content": text
                }
            ]
        )
        # Extract the text content from the returned message.
        return completion.choices[0].message.content

app = Flask(__name__)
CORS(app, origins=[
    "https://www.extrapolator.org",
    "https://extrapolator.org",
    "http://www.extrapolator.org",
    "http://extrapolator.org",
    "http://127.0.0.1:5173"])

@app.route("/", methods=["GET", "OPTIONS"])
def index():
    return jsonify({"message": "Extrapolator API"}), 200

@app.route("/extrapolations", methods=["GET"])
def get_extrapolations():
    with Session(engine) as session:
        statement = select(Extrapolation)
        # execute the query and get all results
        results = session.exec(statement).all()
    # Convert each SQLModel instance to a dict (excluding SQLAlchemy internals)
    return jsonify([ex.dict() for ex in results]), 200

@app.route("/extrapolations/<string:uuid>", methods=["GET"])
def get_extrapolation(uuid):
    with Session(engine) as session:
        statement = select(Extrapolation).where(Extrapolation.uuid == uuid)
        extrapolation = session.exec(statement).first()
    if extrapolation is None:
        return jsonify({"error": f"No extrapolation found with uuid {uuid}"}), 404
    return jsonify(extrapolation.dict()), 200

@app.route("/extrapolations", methods=["POST"])
def extrapolate_route():
    data = request.get_json(force=True)
    text = data.get("text", "").strip()
    if not text:
        return jsonify({"error": "No text provided"}), 400

    try:
        extrapolated_content = Extrapolator().extrapolate(text)
        if extrapolated_content == 'I cannot extrapolate the text.':
            return jsonify({"error": "I cannot extrapolate the text."}), 400
        
        # Create and store a new Extrapolation record in the DB.
        with Session(engine) as session:
            new_extrapolation = Extrapolation(
                input=text,
                extrapolation=extrapolated_content
            )
            session.add(new_extrapolation)
            session.commit()
            session.refresh(new_extrapolation)
        
        # Return the new record as JSON.
        return jsonify(new_extrapolation.dict()), 200

    except RateLimitError as e:
        return jsonify({"error": "Rate limit exceeded. " + str(e)}), 429

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)