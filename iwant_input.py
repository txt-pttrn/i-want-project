#!/usr/bin/env python
# coding: utf-8

# In[4]:


# This program searches for specific keywords in two different subreddits 
# using the Reddit API and the Pushshift API. It extracts, cleans, and saves 
# the resulting sentences to a CSV file. If a timeout error occurs due to 
# the API server being down, the program catches the error and creates a 
# randomized version of a backup CSV file instead.

import csv
import configparser
import random
import requests
import time
import praw

# Filepath where the output gets saved to in a table
file_path = 'C:/Users/Paula/Desktop/Programmieren/iwant/sentences.csv'

# Read credentials from config file
config = configparser.ConfigParser()
config.read('credentials.ini')

# OAuth login with my credentials
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

# Get new comments starting with "females..." keywords and new submissions starting with "i want..." keywords from their respective subreddits
def extract_sentences(subreddit, query_string, is_submission=False, num_sentences=100):
    # Set up the base URL for the Pushshift API, depending on comment or submission search
    pushshift_base_url = "https://api.pushshift.io/reddit/{}/search".format("submission" if is_submission else "comment")
    sentences = set()  # A set to store only unique sentences
    before = None

    # Use a session to make requests
    with requests.Session() as session:
        # Continue fetching sentences until the desired number is reached
        while len(sentences) < num_sentences:
            # Define query parameters for the API request
            query_params = {
                "subreddit": subreddit,
                "size": 500,
                "before": before,
                "q": query_string,
            }

            # If looking for submissions, request specific fields
            if is_submission:
                query_params["fields"] = "title,selftext"

            # Make the API request
            response = session.get(pushshift_base_url, params=query_params)

            # Process the response if successful
            if response.status_code == 200:
                json_data = response.json()
                before = json_data['data'][-1]['created_utc']

                # Extract sentences from the response data
                for item in json_data['data']:
                    if is_submission:
                        text = item['title'].strip() + " " + item['selftext'].strip()
                    else:
                        text = item['body'].strip()

                    lower_text = text.lower()

                    # Check if the sentence starts with any of the specified keywords
                    for keyword in query_string.split("|"):
                        keyword = keyword.strip('"')

                        if lower_text.startswith(keyword):
                            if text:
                                sentences.add(text)
                            break
                    if len(sentences) >= num_sentences:
                        break
            # Sleep for a short time to avoid rate limiting
            time.sleep(1)
    #convert set back to list for processing
    return list(sentences)

# Function to clean list of extracted sentences
def clean_sentences(sentences):
    punctuation_marks = ['.', '!', '?']
    cleaned_sentences = []

    # Iterate through sentences, cleaning each one
    for sentence in sentences:
        # Remove "[deleted]" and newlines, and trim whitespace
        cleaned = sentence.replace("[deleted]", "").replace('\n', ' ').strip()
        # Add cleaned sentence to list if it's not empty
        if len(cleaned) > 0:
            # Add a period to the end of the sentence if it doesn't already end with punctuation
            if cleaned[-1] not in punctuation_marks:
                cleaned += '.'
            cleaned_sentences.append(cleaned)

    return cleaned_sentences

# Function to write sentences to a CSV file
def write_sentences_to_csv(sentences_dict, file_path):
    # Open the CSV file for writing
    with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile, quoting=csv.QUOTE_NONNUMERIC)
        # Determine the maximum number of sentences from any subreddit
        max_len = max(len(v) for v in sentences_dict.values())
        # Iterate through the range of maximum sentences
        for i in range(max_len):
            row = []
            # Add sentences from each subreddit to the current row
            for subreddit in subreddits_and_keywords.keys():
                sentence = sentences_dict[subreddit][i] if i < len(sentences_dict[subreddit]) else ""
                row.append(sentence)
            # Write the row to the CSV file
            writer.writerow(row)
            
# Function to shuffle the rows of the backup CSV file
def create_randomized_csv_from_backup(backup_file_path, output_file_path):
    with open(backup_file_path, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        rows = list(reader)
    
    random.shuffle(rows)

    with open(output_file_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile, quoting=csv.QUOTE_NONNUMERIC)
        for row in rows:
            writer.writerow(row)

# Main function to coordinate the entire process
def main():
    try:
        sentences_dict = {}
        for subreddit, keywords in subreddits_and_keywords.items():
            query_string = '|'.join(f'"{keyword}"' for keyword in keywords)
            is_submission = subreddit == "TrollXChromosomes"
            sentences = extract_sentences(subreddit, query_string, is_submission=is_submission)
            cleaned_sentences = clean_sentences(sentences)
            sentences_dict[subreddit] = cleaned_sentences

        write_sentences_to_csv(sentences_dict, file_path)
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
        print("Creating a randomized CSV from the backup file.")
        backup_file_path = 'C:/Users/Paula/Desktop/Programmieren/iwant/sentences-backup.csv'
        create_randomized_csv_from_backup(backup_file_path, file_path)


# Run the main function when the script is executed
if __name__ == '__main__':
    main()


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:




