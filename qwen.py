import os
import requests
import pandas as pd
import jieba
import re

# Define the API URL
url = "http://127.0.0.1:1234/v1/completions"

# List of files to analyze
files_to_analyze = [
    "关于印发2030年前碳达峰行动方案的通知.txt",
    "关于大力实施可再生能源替代行动的指导意见.txt",
    "关于完整准确全面贯彻新发展理念做好碳达峰碳中和工作的意见.txt",
    "关于深入打好污染防治攻坚战的意见.txt"
]

# Directory containing the text files
txt_directory = "Final"  # Replace with your directory path

# Output CSV file
output_csv = "parsed_sentiments2.csv"

# Function to split text by punctuation and tokenize with Jieba
def split_and_tokenize(text):
    # Split text by punctuation (。！？；, etc.)
    sentences = re.split(r"[。！？；…]", text)
    # Tokenize each sentence using Jieba
    tokenized_words = []
    for sentence in sentences:
        tokens = jieba.lcut(sentence.strip())
        tokenized_words.extend(tokens)
    return tokenized_words

# Function to process a single text file
def process_file(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()

    # Split and tokenize content
    words = split_and_tokenize(content)
    
    results = []
    for word in words:
        if word.strip():  # Skip empty words
            # Prepare the prompt with additional context
            prompt = f"""
            Provide a single word that answers or completes the following: [For the domain identified as Environmental Protection and Carbon Neutrality, analyze the sentiment label the sentiment of the following text as 'positive', 'neutral', or 'negative'. You only need to generate one single word as a result: The context is that the document is strongly positive towards carbon emission reduction and environmental protection. Analyze the sentiment of: {word}]. Only give one word as the response, without explanation.
            """
            # Set up the payload
            payload = {
                "prompt": prompt,
                "max_tokens": 2,
                "temperature": 0.7
            }
            
            try:
                # Make API request
                response = requests.post(url, json=payload)
                response.raise_for_status()
                sentiment = response.json().get("choices", [{}])[0].get("text", "").strip()
                
                # Append the word and sentiment to the results
                results.append({"word": word, "sentiment": sentiment})
            except requests.exceptions.RequestException as e:
                print(f"Error processing word '{word}': {e}")
                results.append({"word": word, "sentiment": "error"})
    
    return results

# Main function to process all files
def process_all_files(file_list, directory, output_csv):
    all_results = []
    for file_name in file_list:
        file_path = os.path.join(directory, file_name)
        if os.path.exists(file_path):
            print(f"Processing file: {file_path}")
            file_results = process_file(file_path)
            all_results.extend(file_results)
        else:
            print(f"File not found: {file_path}")
    
    # Convert results to a DataFrame
    df = pd.DataFrame(all_results)
    
    # Save to CSV
    df.to_csv(output_csv, index=False)
    print(f"Results saved to {output_csv}")

# Run the processing for specified files
process_all_files(files_to_analyze, txt_directory, output_csv)
