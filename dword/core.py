# AUTOGENERATED! DO NOT EDIT! File to edit: 00_core.ipynb (unless otherwise specified).

__all__ = ['DeepWord']

# Internal Cell
import base64
import json
import os
import random
import time
from pathlib import Path
from typing import Dict, List, Union

import cv2
import pytube
import requests
import urllib3
from pytube import YouTube

from .utils import *
from .utils import URLs, _exists, TextDicts
from IPython.display import Audio
from nbdev.showdoc import show_doc

urllib3.disable_warnings()

# Cell
class DeepWord:
    """
    A class for logging into your DeepWord account in Python and generating videos at scale
    """
    def __init__(self, api_key: str, secret_key: str) -> None:
        """Initialize a new DeepWord object. Login to your DeepWord account to generate api keys.
        """
        self.session = requests.session()
        self.session.verify = False
        self.headers = {'api_key': api_key, 'secerat_key': secret_key, 'Content-Type': 'application/json'}
        self._authenticate_user()

    def _authenticate_user(self):
        url = URLs.validate_token_url
        response = self.session.post(url, headers=self.headers)
        output = self._process_output(response.text)
        if output['success']:
            print('login successful')
        else:
            raise ValueError('Invalid api_key or secret_key')

    @staticmethod
    def _process_output(x): return json.loads(x)

    @property
    def available_credits(self) -> int:
        """Get the number of credits available in your DeepWord account.
        """
        url = URLs.credits_url
        response = self.session.post(url, headers=self.headers)
        try:
            output = self._process_output(response.text)
            return output['available_credits']
        except:
            raise ValueError(response.text)

    def list_videos(self) -> List[Dict]:
        """Get a list of all the videos you've generated using your DeepWord account.
        """
        url = URLs.list_vids_url
        response = self.session.post(url, headers=self.headers)
        try:
            output = self._process_output(response.text)
            return output['data']
        except:
            raise ValueError(response.text)

    @property
    def _available_languages(self) -> List: return TextDicts.langs

    def _available_speakers(self, lang) -> List: return TextDicts.speakers[lang]

    def text2speech(self, text: str, language: str, speaker: str, outfile = 'text2speech.mp3') -> str:
        if language not in self._available_languages:
            raise ValueError(f'Language {language} not available. To see available languages print obj._available_languages')

        if speaker not in self._available_speakers(language):
            raise ValueError(f'Invalid model for language {language}. To see available models print obj._available_speakers(language)')

        if Path(outfile).exists():
            os.remove(f'{outfile}')

        code = TextDicts.lang2code[language]
        sp, gender = speaker.split(' ')

        payload='{"text":"%s","name":"%s","gender":"%s","code":"%s"}'% (text,sp,gender,code)
        url = URLs.txt2speech_url
        response = self.session.post(url, headers=self.headers,data=payload)

        try:
            decode_bytes = base64.b64decode(response.text)
            with open(outfile, "wb") as wav_file:
                wav_file.write(decode_bytes)
            return (f"Successfully generated audio file {outfile}")
        except Exception as e:
            raise ValueError(response.text)

    def download_video(self, video_id: str) -> None:
        """Download one of the synthetically generated videos on your DeepWord account.
           The video id can be found using the ``list_generated_videos()`` function. The video
           should have finished processing to be downloadable.
           Optionally, you can use download_all_videos().
        """
        url = URLs.download_vid_url + video_id
        response = self.session.get(url, headers=self.headers)
        if response.json()['status'] is False:
            raise ValueError("Video is still processing. Unable to download it at this time.")
        try:
            r = requests.get(response.json()['video_url'], stream=True)
            with open(response.json()['video_name'], 'wb') as f:
                for chunk in r.iter_content(chunk_size=1024):
                    if chunk: # filter out keep-alive new chunks
                        f.write(chunk)
            return (f"Successfully downloaded video {video_id}!")
        except Exception as e:
            raise ValueError(response.text)

    def download_all_videos(self, folder: Union[str, Path]  = 'downloaded_videos') -> None:
        """Download all vidoes generated with your DeepWord account. You can also pass
        a folder or nested folders where you want the vidoes to be saved.
        """
        url = URLs.list_vids_url
        path = Path().cwd()

        folder = Path(folder)
        folder.mkdir(parents = True, exist_ok = True)

        response = self.session.post(url, headers=self.headers)
        try:
            for item in response.json()['data']:
                r = requests.get(item['video_url'], stream=True)

                fname1 = item['title'].replace(".mp4",'')+'.mp4'
                full_path = f'{path/folder/fname1}'

                with open(full_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=1024):
                        if chunk: # filter out keep-alive new chunks
                            f.write(chunk)
            print(f"Successfully downloaded all videos in folder {folder}!")
        except Exception as e:
            raise ValueError(response.text)

    def download_youtube_video(self, url: str, types: str = 'video', folder = 'youtube'):
        """Download a video from YouTube. You can also donwload an audio by providing
           types = 'audio'.
        """
        folder = Path(folder)
        folder.mkdir(exist_ok=True)
        if types == "video":
            pytube.YouTube(url).streams.get_highest_resolution().download(folder)
            print("downloaded youtube video successfully!")
        else:
            yt = YouTube(url)
            stream = yt.streams.filter(only_audio=True).first()
            out_file  = stream.download(folder)
            base, ext = os.path.splitext(out_file)
            new_file = base + '_audio.mp3'
            os.rename(out_file, new_file)
            print("downloaded youtube audio successfully!")

    def download_audio_samples(self):
        """Download all the audio samples available on the DeepWord website
        """
        folder = Path().cwd() / 'audio_samples'
        folder.mkdir(exist_ok = True)

        url = URLs.api_get_audio_sample
        response = self.session.post(url, headers=self.headers)
        try:
            for dic in self._process_output(response.text)['sample_audio_files']:
                doc = self.session.get(dic['audio_url'])
                fname = folder / (dic['title']+dic['extension'])
                f = open(fname,"wb")
                f.write(doc.content)
                f.close()
            return ("Successfully downloaded all audio samples")
        except Exception as e:
            raise ValueError(response.text)

    def download_video_actors(self):
        """Download all the video actors available on the DeepWord website.
        """
        folder = Path().cwd() / 'video_actors'
        folder.mkdir(exist_ok = True)

        url = URLs.api_get_video_actors
        response = self.session.post(url, headers=self.headers)
        try:
            for dic in self._process_output(response.text)['sample_video_files']:
                with self.session.get(dic['video_url'], stream=True) as r:
                    r.raise_for_status()
                    fname = folder / (dic['title']+dic['extension'])
                    with open(fname, 'wb') as f:
                        for chunk in r.iter_content(chunk_size=8192):
                            f.write(chunk)
            return ("Successfully downloaded all video actors")
        except Exception as e:
            raise ValueError(response.text)

    def generate_video(self, video: str, audio: str, title: str = None):
        """Generate a synthetic video using a video of a person talking and the audio
           you want them to say. You can check the status of the video using
           ``list_generated_videos`` and download it using ``download_video`` or
           ``download_all_videos``
        """
        if not _exists(video): raise ValueError(f'File not found {video}')
        if not _exists(audio): raise ValueError(f'File not found {audio}')
        payload = {}
        if title is not None:
            payload={'name': title}
        self.headers.pop("Content-Type", None)
        url = URLs.generate_vid_url
        files = {'video_file': open(video,'rb'),'audio_file': open(audio,'rb')}
        response = self.session.post(url, headers=self.headers,files=files,data=payload)
        try:
            print('Generating video. This will take a few minutes.')
            return response.json()
        except Exception as e:
            raise ValueError(e)