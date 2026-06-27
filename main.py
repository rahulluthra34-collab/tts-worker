import os
import tempfile
from flask import Flask, request, jsonify, send_file
from openai import OpenAI

app = Flask(__name__)

client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY")
)

@app.route("/", methods=["GET"])
def health():
    return {"status": "ok"}

@app.route("/tts", methods=["POST"])
def tts():
    try:
        data = request.get_json()

        text = data.get("text", "")
        voice = data.get("voice", "alloy")
        model = data.get("model", "gpt-4o-mini-tts")

        if not text:
            return jsonify({"error": "text required"}), 400

        temp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        temp.close()

        with client.audio.speech.with_streaming_response.create(
            model=model,
            voice=voice,
            input=text
        ) as response:
            response.stream_to_file(temp.name)

        return send_file(
            temp.name,
            mimetype="audio/mpeg",
            as_attachment=True,
            download_name="audio.mp3"
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
