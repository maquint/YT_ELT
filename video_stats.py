import requests
import json

import os
from dotenv import load_dotenv

load_dotenv(dotenv_path="./.env")

API_KEY = os.getenv("API_KEY")
CHANNEL_HANDLE = "MrBeast"
maxResults = 50

def get_playlist_id():
    try:
        url = f"https://youtube.googleapis.com/youtube/v3/channels?part=contentDetails&forHandle={CHANNEL_HANDLE}&key={API_KEY}"
        
        response = requests.get(url)

        response.raise_for_status()  # Check if the request was successful
  
        data = response.json()

        # print(json.dumps(data, indent=4))

        channel_items = data["items"][0]

        channel_playlists = channel_items["contentDetails"]["relatedPlaylists"]["uploads"]
        
        # print(channel_playlists)

        return channel_playlists

    except requests.exceptions.RequestException as e:
        raise e

def get_video_ids(playlistId):

    videos_ids = []

    pageToken = None

    base_url = f"https://youtube.googleapis.com/youtube/v3/playlistItems?part=contentDetails&maxResults={maxResults}&playlistId={playlistId}&key={API_KEY}"

    try:

        while True:
            
            url = base_url
            if pageToken:
                url += f"&pageToken={pageToken}"

            response = requests.get(url)

            response.raise_for_status()  # Check if the request was successful

            data = response.json()

            items = data.get("items", [])

            for item in items:
                video_id = item["contentDetails"]["videoId"]
                videos_ids.append(video_id)

            pageToken = data.get("nextPageToken")
            if not pageToken:
                break

        return videos_ids

    except requests.exceptions.RequestException as e:
        raise e

def batch_list(video_id_list, batch_size):
    for i in range(0, len(video_id_list), batch_size):
        yield video_id_list[i:i + batch_size]

        

def extract_video_data(videos_ids):
    
    extracted_data = []

    def batch_list(video_id_list, batch_size):
        for i in range(0, len(video_id_list), batch_size):
            yield video_id_list[i:i + batch_size]

    
    
    try:
        for batch in batch_list(videos_ids, maxResults):
            video_ids_str = ",".join(batch)

            url = f"https://youtube.googleapis.com/youtube/v3/videos?part=contentDetails&part=snippet&part=statistics&id={video_ids_str}&key={API_KEY}"
            
            response = requests.get(url)

            response.raise_for_status()  # Check if the request was successful

            data = response.json()

            items = data.get("items", [])

            for item in items:
                video_data = {
                    "videoId": item["id"],
                    "title": item["snippet"]["title"],
                    "publishedAt": item["snippet"]["publishedAt"],
                    "duration": item["contentDetails"]["duration"],
                    "viewCount": item["statistics"].get("viewCount", None),
                    "likeCount": item["statistics"].get("likeCount", None),
                    "commentCount": item["statistics"].get("commentCount", None)
                }
                extracted_data.append(video_data)

        return extracted_data

    except requests.exceptions.RequestException as e:
        raise e
    

if __name__ == "__main__":
    playlistId = get_playlist_id()
    video_ids=(get_video_ids(playlistId))
    print(extract_video_data(video_ids))

