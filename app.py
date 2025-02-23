from flask import Flask, request, jsonify
from openai import OpenAI, RateLimitError
from flask_cors import CORS  # Import Flask-CORS

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

@app.route("/extrapolate", methods=["POST"])
def extrapolate_route():
    data = request.get_json(force=True)
    text = data.get("text", "").strip()
    if not text:
        return jsonify({"error": "No text provided"}), 400

    try:
        extrapolated_content = Extrapolator().extrapolate(text)
        return jsonify({"extrapolated": extrapolated_content}), 200

    except RateLimitError as e:
        # Optional: Return a specific message if quota is exceeded.
        return jsonify({"error": "Rate limit exceeded. " + str(e)}), 429

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)