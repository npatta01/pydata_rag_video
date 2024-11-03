from moviepy.editor import VideoFileClip
from pathlib import Path
from pytubefix import YouTube
from pprint import pprint
import json
import os
from PIL import Image
import matplotlib.pyplot as plt
from youtube_transcript_api import YouTubeTranscriptApi
import re


def get_video_metadata(yt:YouTube):
    #yt = YouTube(video_id)

    return {
        "video_id": yt.video_id,
        "title": yt.title,
        "author": yt.author,
        "keywords": yt.keywords,

        "publish_date": yt.publish_date.isoformat(),

        "length": yt.length,
        "likes": yt.likes,
        "views": yt.views,
        "channel_id": yt.channel_id,
        "thumbnail_url": yt.thumbnail_url,
        "description": yt.description,

    }


def get_youtube_id(link:str):
    """Extracts the video ID from a YouTube video link."""
    if "youtube.com" in link:
        pattern = r'youtube\.com/watch\?v=([a-zA-Z0-9_-]+)'
        video_id = re.search(pattern, link).group(1)
        return video_id
    elif "youtu.be" in link:
        pattern = r"youtu\.be/([a-zA-Z0-9_-]+)"
        video_id = re.search(pattern, link).group(1)
        return video_id
    else:
        return None

def get_transcript(video_id:str):
    try:
        transcript_dict = YouTubeTranscriptApi.get_transcript(video_id)
        final_transcript = " ".join(i["text"] for i in transcript_dict)
        return final_transcript , transcript_dict
    except Exception as e:
        print(e)


def get_transcript_time(link:str):
    """Gets the transcript of a YouTube video with timestamps."""
    video_id =get_youtube_id(link)

    try:
        transcript_dict = YouTubeTranscriptApi.get_transcript(video_id)
        final_transcript = ""
        for i in transcript_dict:
            timevar = round(float(i["start"]))
            hours = int(timevar // 3600)
            timevar %= 3600
            minutes = int(timevar // 60)
            timevar %= 60
            timevex = f"{hours:02d}:{minutes:02d}:{timevar:02d}"
            final_transcript += f'{i["text"]} "time:{timevex}" '
        return final_transcript
    except Exception as e:
        print(e)
        return video_id



def download_video(video_id:str, output_path):
    """
    Download a video from a given url and save it to the output path.

    Parameters:
    url (str): The url of the video to download.
    output_path (str): The path to save the video to.

    Returns:
    dict: A dictionary containing the metadata of the video.
    """

    url =  f"https://www.youtube.com/watch?v={video_id}"
    print (url)
    yt = YouTube(url, use_po_token=False)
    metadata = get_video_metadata(yt)

    transcript,transcript_dict = get_transcript(video_id)

    with open(os.path.join(output_path,"transcript.txt"),"w") as f:
        f.write(transcript)



    with open(os.path.join(output_path,"metadata.json"),"w") as f:
        json.dump(metadata,f, indent=4)

    yt.streams.get_highest_resolution().download(
        output_path=output_path, filename="video.mp4"
    )
    return metadata


def video_to_images(video_path, output_folder,fps=0.2):
    """
    Convert a video to a sequence of images and save them to the output folder.

    Parameters:
    video_path (str): The path to the video file.
    output_folder (str): The path to the folder to save the images to.

    """
    clip = VideoFileClip(video_path)

    os.makedirs(os.path.join(output_folder,"images"), exist_ok=True)
    clip.write_images_sequence(
        os.path.join(output_folder,"images", "frame%04d.png"), fps=fps
    )
