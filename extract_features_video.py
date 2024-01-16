import os
import yt_dlp as youtube_dl
from googleapiclient.discovery import build
import pandas as pd

# Set up your YouTube Data API key
API_KEY = "AIzaSyD5h1myju5oxuNDA1XDUaIKy_piFUfEPIU"


def get_playlist_id(playlist_url):
    with youtube_dl.YoutubeDL() as ydl:
        info_dict = ydl.extract_info(playlist_url, download=False)
        return info_dict.get("id", "")


def get_video_ids_from_playlist(playlist_id, api_key):
    youtube = build("youtube", "v3", developerKey=api_key)
    request = youtube.playlistItems().list(
        part="contentDetails", playlistId=playlist_id, maxResults=50
    )
    response = request.execute()

    video_ids = [item["contentDetails"]["videoId"] for item in response["items"]]
    return video_ids


def download_playlist_videos(video_ids, output_path):
    for video_id in video_ids:
        video_info = youtube_video_info(video_id, API_KEY)
        title = video_info.get("title", "")
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        download_video(video_url, output_path, title)


def download_video(video_url, output_path, title):
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": os.path.join(output_path, f"{title}.%(ext)s"),
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
            print(f"Error: Unable to download the video {title}.")


def create_playlist_dataframe(video_ids, api_key):
    video_info_list = []

    for video_id in video_ids:
        video_info = youtube_video_info(video_id, api_key)
        video_info_list.append(video_info)

    video_dataframe = pd.DataFrame(video_info_list)
    return video_dataframe


def main():
    # Example YouTube playlist URL
    youtube_playlist_url = "https://music.youtube.com/playlist?list=RDCLAK5uy_n20FRYQXNt1p1wS55Nj2r14IouO5weaYU&playnext=1&si=Mcuq363m5ScFqZfM"

    # Directory to store downloaded videos
    output_directory = "downloaded_videos"

    # Set up your YouTube Data API key
    api_key = "AIzaSyD5h1myju5oxuNDA1XDUaIKy_piFUfEPIU"

    # Get playlist ID and video IDs
    playlist_id = get_playlist_id(youtube_playlist_url)
    video_ids = get_video_ids_from_playlist(playlist_id, api_key)

    # Download playlist videos
    download_playlist_videos(video_ids, output_directory)

    # Create a DataFrame with extracted features for the playlist videos
    playlist_dataframe = create_playlist_dataframe(video_ids, api_key)

    # Display the DataFrame
    print("\nDataFrame:")
    print(playlist_dataframe)

    # Save the DataFrame to a CSV file
    csv_file_path = "playlist_videos.csv"
    playlist_dataframe.to_csv(csv_file_path, index=False)
    print(f"\nDataFrame saved to {csv_file_path}")


main()
