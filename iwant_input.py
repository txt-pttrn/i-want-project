# This program fetches comments and submissions from two specific 
# subreddits (AskReddit and TrollXChromosomes) using the Pushshift 
# API, filtering them based on a set of pre-defined keywords. It 
# then cleans the extracted text and combines them to create a 
# series of transition strings. Finally, the program generates a 
# PDF file containing these transition strings, with each string 
# presented on a new page.

import re
import csv
import configparser
import random
import requests
import time
import praw
import textwrap
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, inch

# Define a variable for the common folder path
folder_path = "C:/Users/Paula/Desktop/Programmieren/iwant/"

# Read credentials from config file
config = configparser.ConfigParser()
config.read('credentials.ini')

# OAuth login with the credentials
reddit = praw.Reddit(client_id=config.get('REDDIT', 'CLIENT_ID'),
                     client_secret=config.get('REDDIT', 'CLIENT_SECRET'),
                     username=config.get('REDDIT', 'USERNAME'),
                     password=config.get('REDDIT', 'PASSWORD'),
                     user_agent=config.get('REDDIT', 'USER_AGENT'))

# Dictionary containing both sets of request data
subreddits_and_keywords = {
    "AskReddit": ["females should", "all females should",
                  "females will", "all females will",
                  "females need", "all females need",
                  "females gotta", "all females gotta",
                  "females must", "all females must"],
    "TrollXChromosomes": ["i want", "i wanna",
                          "i really want", "i really wanna",
                          "i just want", "i just wanna",
                          "i'm looking for", "i'm searching for",
                          "i need", "i'm in need of",
                          "i wish", "i desire",
                          "i crave", "i'm dying for",
                          "i'd love", "i'd like"]
}

# This function fetches new comments or submissions from a specified subreddit based on provided query_string.
# It uses the Pushshift API to perform the search and returns a list of sentences matching the criteria.
def extract_text(subreddit, query_string, is_submission=False, num_sentences=100):
    # Set the base URL for the Pushshift API search, depending it it's submissions (for the "i want" part) or comments ("females" part)
    pushshift_base_url = f"https://api.pushshift.io/reddit/{'submission' if is_submission else 'comment'}/search"

    # Initialize a set to store only unique sentences
    sentences = set()

    # Initialize a variable to store the timestamp for pagination. It's for skipping already searched content
    before = None

    # Create a requests session to make API calls
    with requests.Session() as session:
        # Continue fetching data until the desired number of sentences is reached (100 each)
        while len(sentences) < num_sentences:
            # Set query parameters for the API call
            query_params = {
                "subreddit": subreddit,
                "size": 500,
                "before": before,
                "q": query_string,
            }

            # Include fields for submission search, if required (only titles and text, no metadata)
            if is_submission:
                query_params["fields"] = "title,selftext"

            # Make the API call using the session
            response = session.get(pushshift_base_url, params=query_params)

            # Check if the API call was successful (error handling currently in main function)
            if response.status_code == 20:
                # Parse the response JSON data
                json_data = response.json()

                # Update the 'before' timestamp for the next iteration (skipping viewed content)
                before = json_data['data'][-1]['created_utc']

                # Iterate through the data items and extract the text
                for item in json_data['data']:
                    if is_submission:
                        text = item['title'].strip() + " " + item['selftext'].strip()
                    else:
                        text = item['body'].strip()

                    # Convert the text to lowercase for keyword comparison
                    lower_text = text.lower()

                    # Check if the text starts with any of the keywords specified, joined into a single query 
                    for keyword in query_string.split("|"):
                        keyword = keyword.strip('"')

                        if lower_text.startswith(keyword):
                            # If the text is not empty (duh) and is a match, add it to the set of sentences
                            if text:
                                sentences.add(text)
                            break

                    # Stop processing if the desired number of sentences is reached
                    if len(sentences) >= num_sentences:
                        break
            else:
                # Print an error message if the API is down
                print("Pushshift API is down.")
                break

            # Wait for 1 second before making the next API call to avoid rate limits
            time.sleep(1)

    # Return the list of extracted sentences
    return list(sentences)


def clean_text(sentences):
    
    # Used to format the sentences like a book instead of 1 sentence per line
    punctuation_marks = ['.', '!', '?']
    
    # This regex pattern will match most emojis (not all though!)
    # I can't get the pdf making function to keep the emoticons intact, so for now I'm deleting them
    emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
        u"\U00002702-\U000027B0"  # Dingbats
        u"\U000024C2-\U0001F251"  # Enclosed characters
        "]+", flags=re.UNICODE)
    
    cleaned_sentences = []
    
    for sentence in sentences:
        # Remove "[deleted]", newlines, and trim whitespace
        # Emergency workaround for the ampersand, font problems (see above)
        cleaned = sentence.replace("[deleted]", "").replace('\n', ' ').replace('&','and').strip()
        
        # Remove emojis
        cleaned = emoji_pattern.sub(r'', cleaned)
        
        # Add cleaned sentence back to collection if it's not empty
        if len(cleaned) > 0:
            # Add a period to the end of the sentence if it doesn't already end with punctuation
            if cleaned[-1] not in punctuation_marks:
                cleaned += '.'
            cleaned_sentences.append(cleaned)

    return cleaned_sentences


# Backup to make a collection if the API is down (happens sometimes)
def create_random_dict_from_backup(backup_file_path):
    
    # Initialize an empty dictionary to store randomized sentences
    randomized_sentences = {}
    
    # Open the backup file for reading
    with open(backup_file_path, 'r', newline='', encoding='utf-8') as csvfile:
        # Create a CSV reader to read the file
        reader = csv.reader(csvfile)
        # Convert the CSV reader iterator to a list of rows
        rows = list(reader)

    # Randomly shuffle the rows in the list
    random.shuffle(rows)

    # Iterate over the rows and their indices
    for idx, row in enumerate(rows):
        # Iterate over the subreddits and sentences in the row
        for subreddit, sentence in zip(subreddits_and_keywords.keys(), row):
            # Initialize an empty list for each subreddit on the first iteration
            if idx == 0:
                randomized_sentences[subreddit] = []
            # If a sentence exists (it does), append it to the corresponding subreddit's list
            if sentence:
                randomized_sentences[subreddit].append(sentence)
    
    # Return the dictionary containing randomized sentences for each subreddit
    return randomized_sentences


# this function is for formatting: it makes sure that each page ends with a complete sentence instead of cutting off. usually.
def truncate_text(sentences):
    # Initialize an empty string to store the truncated text
    text = ""
    
    # If there are sentences, start with the first one
    if sentences:
        text = sentences[0]

    # Iterate over the remaining sentences
    for sentence in sentences[1:]:
        # Check if the combined length of the current text and the next sentence is within the limit (3850 characters)
        if len(text + sentence) <= 3850:
            # If within the limit, append the sentence to the current text
            text += " " + sentence
        else:
            # If the limit is exceeded, stop processing the remaining sentences
            break

    # Return the truncated text
    return text


# This is where the generated sentences get sorted into pages 
# the original page of "i want..." sentences gets replaced bit by bit with the "females..." comments.
def generate_transitions(text_trollx, text_askreddit):
    
    # Initialize the list of transition strings starting with text_trollx (the first page)
    transition_strings = [text_trollx]
    
    # Set the total number of strings, including the initial and final strings (= pages)
    num_strings = 40

    # Calculate the total number of characters to replace on each page (about 100 in this version)
    chars_per_page = len(text_trollx) // (num_strings - 1)
    if chars_per_page % 2 != 0:
        chars_per_page += 1

    # Initialize a set to store the indices of characters that have already been substituted 
    # Used so that already subtituted characters get skipped in the process
    substituted_indices = set()
    
    # Randomly select characters to replace for the first transition
    indices_to_replace = random.sample(range(len(text_trollx)), chars_per_page)

    # Generate the transition strings (corrupt the original page more each iteration)
    for i in range(1, num_strings):
        # Create a new string as a copy of the last string in the list
        new_string = list(transition_strings[-1])

        # Replace characters at the selected indices (following the last substituted character)
        for j, index in enumerate(indices_to_replace):
            # If the index has already been substituted, find an unsubstituted one
            while index in substituted_indices:
                index = (index + 1) % len(new_string)

            # Replace the character if the index is within the range of the last page
            if index < len(text_askreddit):
                new_string[index] = text_askreddit[index]
                substituted_indices.add(index)

            # Update index for replacing the next character after the last replaced character
            next_index = (index + 1) % len(new_string)
            while next_index in substituted_indices:
                next_index = (next_index + 1) % len(new_string)
            indices_to_replace[j] = next_index

        # Add the new string to the list of transition strings
        transition_strings.append("".join(new_string))

    # Replace the last string in the list with text_askreddit (completed transmission)
    transition_strings[-1] = text_askreddit

    return transition_strings


# This function makes a new line so that sentences run on in the next line instead of cutting off
def add_newline(x, y, c, left_margin, top_margin, line):
    
    # Check if there is enough space above the bottom margin (0.75 inches) for a new line
    if y - 12 < 0.75 * inch:
        return False

    # Draw the line at the current x, y position
    c.drawString(x, y, line)

    # Reset the x position to the left margin and move the y position up by 12 units
    x = left_margin
    y -= 12

    # Check if the updated y position is above the bottom margin (0.75 inches)
    if y < 0.75 * inch:
        return False

    # Return the updated x and y positions
    return x, y


# This function creates a pdf from the List of pages (transition_strings).
def create_pdf_from_transitions(transition_strings, output_file_path):
    
    # Create a new PDF with the letter size and specified output file path
    c = canvas.Canvas(output_file_path, pagesize=letter)
    width, height = letter

    # Set the left, top, and right margins
    left_margin = 0.75 * inch
    top_margin = height - 0.75 * inch
    right_margin = width - 1.5 * inch

    # Calculate the available width between the left and right margins
    available_width = right_margin - left_margin

    # Iterate through each transition string to create a new page
    for text in transition_strings:
        # Set the font for the current page
        c.setFont("Courier", 11)

        # Initialize the x and y positions to the left and top margins
        x = left_margin
        y = top_margin

        # Wrap the text to fit within the available width
        wrapped_text = textwrap.wrap(text, width=int(available_width / 6.5))

        # Draw each line of wrapped text on the page
        for line in wrapped_text:
            result = add_newline(x, y, c, left_margin, top_margin, line)
            if result:
                x, y = result  # Update the x and y positions
            else:
                break  # Stop drawing text on the page if there's not enough space

        # Add a new page for the next transition string
        c.showPage()

    # Save the generated PDF
    c.save()
    
    
def main():
    
    # Initialize an empty dictionary to store sentences for each subreddit
    sentences_dict = {}

    # Iterate through subreddits and their respective keywords
    for subreddit, keywords in subreddits_and_keywords.items():
        print("I'm gonna get some sentences from Reddit!")
        # Create a query string from the keywords
        query_string = '|'.join(f'"{keyword}"' for keyword in keywords)
        # Check if the current subreddit is a submission or not
        is_submission = subreddit == "TrollXChromosomes"
        # Extract sentences from the subreddit based on the query string
        sentences = extract_text(subreddit, query_string, is_submission=is_submission)
        # Print the number of fetched sentences for each subreddit
        for subreddit, sentences in sentences_dict.items():
            print(f"Fetched {len(sentences)} sentences from {subreddit}")
        # If no sentences are found (because the API server is down), create a randomized dictionary from the backup file
        if len(sentences) == 0:
            print("Creating a randomized dictionary from the backup file.")
            backup_file_path = folder_path + 'sentences-backup.csv'
            sentences_dict = create_random_dict_from_backup(backup_file_path)  # Fixed function name
            break

        # Clean and preprocess the sentences
        cleaned_sentences = clean_text(sentences)
        # Store the cleaned sentences in the dictionary
        sentences_dict[subreddit] = cleaned_sentences

    # Create text strings for TrollXChromosomes and AskReddit
    text_trollx = truncate_text(sentences_dict["TrollXChromosomes"])
    text_askreddit = truncate_text(sentences_dict["AskReddit"])

    # Generate the list of 40 transition strings (pages)
    transition_strings = generate_transitions(text_trollx, text_askreddit)

    # Create and save the output PDF file
    output_pdf_path = folder_path + "iwant-output.pdf"
    create_pdf_from_transitions(transition_strings, output_pdf_path)
    print("Made the depressing pdf!")

    
# Run the main function when the script is executed
if __name__ == '__main__':
    main()

