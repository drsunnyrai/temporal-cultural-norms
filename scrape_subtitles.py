import pandas as pd
import os
from dotenv import load_dotenv
import time
# TODO: replace with desired country and correct directory for your setup
country = "United States"
data = pd.read_csv("data/" + country +" .csv")

os.makedirs("subs/" + country, exist_ok=True)

import requests


# Load environment variables from .env file
load_dotenv()

#TODO: replace with your API key, username and password
API_URL = "https://api.opensubtitles.com/api/v1"
API_KEY = ''


USERNAME = ''
PASSWORD = ''

headers = {
    "Api-Key": API_KEY,
    "Content-Type": "application/json"
}

def login():
    url = f"{API_URL}/login"
    data = {
        "username": USERNAME,
        "password": PASSWORD
    }
    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 200:
        return response.json()['token']
    else:
        raise Exception(f"Failed to log in: {response.status_code}, {response.text}")

def download_subtitle_file(file_id, output_path):
    token = login()
    download_url = f"{API_URL}/download"
    headers["Authorization"] = f"Bearer {token}"

    data = {
        "file_id": file_id
    }

    response = requests.post(download_url, json=data, headers=headers)
    
    if response.status_code == 429:
        time.sleep(5)
        print("Sleeping...")
        response = requests.post(download_url, json=data, headers=headers)
        if response.status_code == 429:
            time.sleep(5)
            print("Sleeping...")
            response = requests.post(download_url, json=data, headers=headers)

    
    if response.status_code == 200:
        download_link = response.json()['link']
        subtitle_content = requests.get(download_link)
        
        with open(output_path, 'wb') as file:
            file.write(subtitle_content.content)
        print(f"Subtitle downloaded to {output_path}")
    else:
        raise Exception("Failed to download subtitle")
def search_subtitles_by_imdb(imdb_id):
    search_url = f"{API_URL}/subtitles"
    params = {
        "imdb_id": imdb_id,
        "languages": "en"  # You can specify other languages
    }
    response = requests.get(search_url, headers=headers, params=params)
    if response.status_code == 429:
        time.sleep(5)
        print("Sleeping...")
        response = requests.post(search_url, json=data, headers=headers)
        if response.status_code == 429:
            time.sleep(5)
            print("Sleeping...")
            response = requests.post(search_url, json=data, headers=headers)
    
    if response.status_code == 200:
        subtitles = response.json().get('data', [])
        
        file_id = subtitles[0]['attributes']['files'][0]['file_id']
        #print(f"File ID: {file_id}, Filename: {subtitles[0]['attributes']['files'][0]['file_name']}")
        return file_id
    else:
        raise Exception(f"Failed to search subtitles: {response.status_code}, {response.text}")

for index, row in data.iterrows():

    print(index)

    if row["startYear"]+ "_" + str(row["title"]) + ".srt" not in os.listdir("subs/" + country):
        if row["titleType"] == "movie" :
            try:
                imdb_id = row["titleId"]  # Example IMDb ID
                file_id = search_subtitles_by_imdb(imdb_id)
            
                # Example usage
                output_path = "subs/" + country + "/" + row["startYear"]+ "_" + str(row["title"]) + ".srt"
                download_subtitle_file(file_id, output_path)
            except Exception as e:
                #pass
                print("Skipped", e)
    else: pass
