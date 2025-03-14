import re
import json
from typing import List, Dict
from google.generativeai import GenerativeModel, configure


def load_model(api_key):
    configure(api_key=api_key)
    model = GenerativeModel('gemini-2.0-flash-001')
    return model


def find_initial_timestamps(transcript: List[Dict], prompt: str, api_key: str) -> List[Dict]:
    """Initial timestamp search using Gemini."""
    model = load_model(api_key)

    # Format transcript for AI processing
    formatted_transcript = "\n".join([
        f"{entry['start']:.1f}s: {entry['text']}"
        for entry in transcript
    ])

    system_prompt = """
    You are an expert at finding relevant timestamps in video transcripts. 
    Analyze the following transcript and find ALL timestamps that match the user's query.
    Return ONLY the response in this exact JSON format: 
    {"timestamps": [{"time": number, "text": "string"}]}
    Include ALL relevant timestamps, do not limit the number of results.
    """

    user_prompt = f"Transcript:\n{formatted_transcript}\n\nFind timestamps for: {prompt}"

    try:
        response = model.generate_content([system_prompt, user_prompt])
        result = response.text

        # Extract JSON from response
        json_match = re.search(r'\{[\s\S]*\}', result)
        if not json_match:
            raise ValueError("Invalid response format from AI")

        parsed_response = json.loads(json_match.group())
        return parsed_response['timestamps']

    except Exception as e:
        raise Exception(f"Failed to process initial search: {str(e)}")


def refine_timestamps(timestamps: List[Dict], prompt: str, api_key: str) -> List[Dict]:
    """Refine timestamps using a second Gemini call."""
    model = load_model(api_key)

    system_prompt = """
    You are an expert at refining and validating video timestamp results.
    Review these timestamps and:
    1. Ensure each timestamp is highly relevant to the query
    2. Remove any duplicates or very similar content
    3. Sort by relevance to the query
    4. Maintain only the most impactful and relevant timestamps
    Return ONLY the response in this exact JSON format:
    {"timestamps": [{"time": number, "text": "string"}]}
    """

    user_prompt = f"""
    Original query: {prompt}
    Timestamps to refine: {json.dumps(timestamps)}

    Please analyze these timestamps and return only the most relevant and unique moments.
    Merge timestamps that are within 5 seconds of each other and keep the more relevant one.
    """

    try:
        response = model.generate_content([system_prompt, user_prompt])
        result = response.text

        # Extract JSON from response
        json_match = re.search(r'\{[\s\S]*\}', result)
        if not json_match:
            raise ValueError("Invalid refinement format from AI")

        parsed_response = json.loads(json_match.group())
        return parsed_response['timestamps']

    except Exception as e:
        raise Exception(f"Failed to refine timestamps: {str(e)}")