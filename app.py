from flask import Flask, request, jsonify
from flask_cors import CORS

from video_search import get_timestamp_list


app = Flask(__name__)
CORS(app)


@app.route('/get-timestamps', methods=['POST'])
def get_timestamps():
    data = request.json
    video_url = data['video_url']
    prompt = data['prompt']
    
    # Example logic to return dummy timestamps
    timestamps = get_timestamp_list(video_url, prompt)

    return jsonify({'timestamps': timestamps})

if __name__ == '__main__':
    app.run(debug=True)
