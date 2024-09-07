import re
import ast
from urllib.parse import urlparse, parse_qs
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi
from langchain import PromptTemplate

from api import api_key

# video_url = "https://www.youtube.com/watch?v=v3jGLV-vgJE"
# prompt = "Find the most exciting move in this game"
# chunk_size = 15

genai.configure(api_key=api_key)


# def extract_youtube_id(url):
#     # Parse the URL
#     parsed_url = urlparse(url)
#     # Parse the query parameters
#     query_params = parse_qs(parsed_url.query)
#     # Extract the 'v' parameter which is the video ID
#     video_id = query_params.get('v', [None])[0]
#     return video_id

def extract_youtube_id(url):
    # Regular expression to match YouTube video IDs
    pattern = r"(?:v=|\/)([0-9A-Za-z_-]{11})(?:&|$)"
    match = re.search(pattern, url)
    if match:
        return match.group(1)
    return None

def combine_chunks(data, chunk_size=30):    
    combined_chunks = []
    current_chunk = {"start": int(data[0]['start']), "text": ""}
    current_start = data[0]['start']
    
    for item in data:
        if item['start'] - current_start < chunk_size:
            # Add text to the current chunk
            current_chunk["text"] += " " + item['text']
        else:
            # Save the current chunk and start a new one
            combined_chunks.append(current_chunk)
            current_chunk = {"start": int(item['start']), "text": item['text']}
            current_start = int(item['start'])
    
    # Append the last chunk
    combined_chunks.append(current_chunk)
    
    return combined_chunks


def preprocess(dict_list):
    # Initialize lists to store the formatted elements and plain text elements
    formatted_elements = []
    plain_text_elements = []

    # Loop through the list of dictionaries
    for item in dict_list:
        # Extract 'start' and 'text' values
        start = int(item['start'])
        text = item['text']
        
        # Append the formatted element to the formatted_elements list
        formatted_elements.append(f"time:{start} {text}")
        
        # Append the plain text to the plain_text_elements list
        plain_text_elements.append(text)

    # Join all elements into a single formatted text block with spaces in between
    formatted_text = f"\n{' '.join(formatted_elements)}\n"
    plain_text = f"\n{' '.join(plain_text_elements)}\n"
    
    # Return both lists
    return plain_text, formatted_text


def get_timestamp(model, prompt, transcript_with_time):

    template = '''This format serves as a structured way to represent a sequence of time-based events or actions in a readable format. Here’s a more general explanation of this structure:   
    Timestamped Entries (time:<TIME_STAMP> <TEXT>):
    Each entry begins with time:<TIME_STAMP>, where <TIME_STAMP> is a placeholder for an actual time or sequential marker (e.g., 0, 2, 4, etc.).
    This timestamp indicates when or in what order the associated text occurs. The text following the timestamp represents transcript at that particular time.

    Following is the time stamp included transcript:
    {transcript_with_time}'''

    # context =  '''For your help, I am also providing the summary of this as follows:
    # {summary}'''

    actual_prompt =  '''Consider youself as world class expert transcript analyst and find the time stamp/s from given prompt.
    Prompt : {prompt}

    Only output MOST relavent timestamps based on the prompt in a LIST format. Eg. [10, 60, 300, etc.]. Don't provide any text output, just provide the list!
    '''
    
    input_1 = PromptTemplate.from_template(template)
    input_1_text = input_1.format(transcript_with_time=transcript_with_time)

    # input_2 = PromptTemplate.from_template(context)
    # input_2_text = input_2.format(summary=summary)

    input_3 = PromptTemplate.from_template(actual_prompt)
    input_3_text = input_3.format(prompt=prompt)
    
    response = model.generate_content([input_1_text, input_3_text], generation_config={"temperature":0.3})
    
    return response.text

def get_timestamp_list(youtube_url, prompt, chunk_size=30):
    video_id = extract_youtube_id(youtube_url)
    print(video_id)
    # get transcript
    transcript = YouTubeTranscriptApi.get_transcript(video_id)

    # converting into chunk of size chunk_size
    data = combine_chunks(transcript, chunk_size)
    _, formated_text = preprocess(data)

    model = genai.GenerativeModel(model_name="gemini-1.5-pro-latest")

    output = get_timestamp(model, prompt, formated_text)
    output = ast.literal_eval(output)

    return output