# AUTOGENERATED! DO NOT EDIT! File to edit: 01_utils.ipynb (unless otherwise specified).

__all__ = ['to_hhmmss', 'to_secs', 'trim_video', 'check_resolution', 'check_fps', 'change_audio_format', 'trim_audio']

# Internal Cell
import os
import subprocess
import time
from pathlib import Path
from subprocess import CalledProcessError
from typing import Dict, Union

import cv2
from fastcore.test import *
import imageio
from IPython.display import Audio, Video
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
from nbdev.showdoc import *
from pydub import AudioSegment

# Internal Cell
class URLs:
    base = 'https://staging.deepword.co:3000/api'
    credits_url = f'{base}/api_get_credits/'
    list_vids_url = f'{base}/list_video_api/'
    txt2speech_url = f'{base}/api_text_to_speech/'
    download_vid_url = f'{base}/api_download_video/'
    download_yt_vid_url = f'{base}/api_download_youtube_video/'
    generate_vid_url = f'{base}/generate_video_api'
    validate_token_url = f'{base}/check_apikey'
    api_get_audio_sample = f'{base}/api_get_audio_sample'
    api_get_video_actors = f'{base}/api_get_video_actors'

# Cell
def to_hhmmss(x: int) -> str:
    """Convert time from secs (int) to hh:mm:ss (str).
    """
    if not x >= 0: raise Exception(f'seconds cannot be negative, got {x}')
    return time.strftime("%H:%M:%S", time.gmtime(x))

# Cell
def to_secs(x: str) -> int:
    """Convert time from hh:mm:ss (str) format to seconds (int).
    """
    h, m, s = x.split(':')
    return int(h) * 3600 + int(m) * 60 + int(s)

# Internal Cell
def _exists(x): return Path(x).exists()

# Cell
def trim_video(video: Union[str, Path], start_time: int, end_time: int, outfile: Union[str, Path] = 'trimmed_video.mp4') -> None:
    """
    Trim a video in place from start (secs) to end (secs). If you don't want to trim inplace, provide output filename.
    For youtube videos you can use ``download_youtube_video`` before trimming them.
    """
    ffmpeg_extract_subclip(f"{video}", start_time, end_time, targetname=f"{outfile}")
    print(f'Successfully trimmed video!')

# Cell
def check_resolution(video: Union[str, Path]) -> Dict:
    """Check the resolution of a video.
    """
    try:
        vid = cv2.VideoCapture(video)
        h, w = vid.get(cv2.CAP_PROP_FRAME_HEIGHT), vid.get(cv2.CAP_PROP_FRAME_WIDTH)
        return {'height': int(h), 'width': int(w)}
    except Exception as e:
        raise ValueError(e)

# Cell
def check_fps(video: Union[str, Path]) -> float:
    """Get the fps of a video
    """
    reader = imageio.get_reader(video)
    fps = reader.get_meta_data()['fps']
    return fps

# Cell
def change_audio_format(audio: Union[str, Path], outfile: Union[str, Path]) -> None:
    """Change the format of audio file. Example, converting mp3 to wav. Works with
       all formats supported by ffmpeg.
    """
    audio, outfile = Path(audio), Path(outfile)
    ext, o_ext = audio.suffix[1:], outfile.suffix[1:]
    f = AudioSegment.from_file(audio, ext)
    f.export(outfile, format = o_ext)

# Cell
def trim_audio(audio: Union[str, Path], start_time: int, end_time: int, outfile: Union[str, Path] = 'trimmed_audio.mp3') -> None:
    """Trim an audio file. Start and end times are in seconds. Works with all formats supported by ffmpeg.
    """
    audio, outfile = Path(audio), Path(outfile)
    ext, o_ext = audio.suffix[1:], outfile.suffix[1:]
    f = AudioSegment.from_file(audio, ext)

    start_time = start_time * 1000
    end_time = end_time * 1000

    f = f[start_time:end_time]
    f.export(outfile, format = o_ext)