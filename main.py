from flask import Flask, request, jsonify
from utils.llm import find_initial_timestamps, refine_timestamps
from utils.video import extract_video_id, get_transcript, format_time

app = Flask(__name__)

@app.route('/find_timestamps', methods=['POST'])
def find_timestamps():
    try:
        # Parse JSON request
        data = request.get_json()
        youtube_url = data.get('youtube_url')
        query = data.get('query')
        api_key = data.get("api_key")

        # Validate input
        if not youtube_url or not query:
            return jsonify({"error": "Missing youtube_url or query"}), 400

        # Extract video ID
        video_id = extract_video_id(youtube_url)

        # Get transcript
        transcript = get_transcript(video_id)

        # Find initial timestamps
        initial_timestamps = find_initial_timestamps(transcript, query, api_key)

        # Refine timestamps
        refined_timestamps = refine_timestamps(initial_timestamps, query, api_key)

        # Format output
        output = [format_time(ts['time']) for ts in refined_timestamps]

        return jsonify({"timestamps": output})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)