import os
import yt_dlp as youtube_dl
from googleapiclient.discovery import build
import pandas as pd

# Set up your YouTube Data API key
with open("apikey.txt", "r") as file:
    API_KEY = file.read().strip()


def youtube_video_info(video_id, api_key):
    youtube = build("youtube", "v3", developerKey=api_key)
    request = youtube.videos().list(
        part="snippet,contentDetails,statistics", id=video_id
    )
    response = request.execute()

    video_info = {
        "title": response["items"][0]["snippet"]["title"]
        if "items" in response and response["items"]
        else "",
        "description": response["items"][0]["snippet"]["description"]
        if "items" in response and response["items"]
        else "",
        "duration": response["items"][0]["contentDetails"]["duration"]
        if "items" in response and response["items"]
        else "",
        "views": int(response["items"][0]["statistics"]["viewCount"])
        if "items" in response and response["items"]
        else 0,
        "genre": response["items"][0]["snippet"]["categoryId"]
        if "items" in response and response["items"]
        else "",
        "upload_date": response["items"][0]["snippet"]["publishedAt"]
        if "items" in response and response["items"]
        else "",
        # Add more details as needed
    }

    return video_info


def download_video(video_url, output_path):
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": os.path.join(output_path, "%(title)s.%(ext)s"),
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
        "verbose": True,  # Add verbose key for detailed output
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        try:
            info_dict = ydl.extract_info(video_url, download=False)
            video_url = info_dict["url"]
            ydl.download([video_url])
        except youtube_dl.utils.DownloadError:
            print("Error: Unable to download the video.")


def create_video_dataframe(video_info):
    video_df = pd.DataFrame([video_info])
    return video_df


def main():
    # Example YouTube video URL
    youtube_video_url = (
        "https://www.youtube.com/watch?v=9z-Mh9Qeinw&ab_channel=bonnietylerVEVO"
    )

    # Directory to store downloaded videos
    output_directory = "downloaded_videos"

    # Set up your YouTube Data API key
    api_key = "AIzaSyD5h1myju5oxuNDA1XDUaIKy_piFUfEPIU"

    # Extract video information from YouTube Data API
    with youtube_dl.YoutubeDL() as ydl:
        info_dict = ydl.extract_info(youtube_video_url, download=False)
        video_id = info_dict.get("id", "")
    video_info = youtube_video_info(video_id, api_key)

    # Display video information
    print("Video Information:")
    for key, value in video_info.items():
        print(f"{key}: {value}")

    # Download the video using youtube_dl with verbose
    download_video(youtube_video_url, output_directory)

    # Create a DataFrame with extracted features
    video_dataframe = create_video_dataframe(video_info)

    # Display the DataFrame
    print("\nDataFrame:")
    print(video_dataframe)


if __name__ == "__main__":
    main()
