import json
from channels.generic.websocket import AsyncWebsocketConsumer
from yt_dlp import YoutubeDL
import logging
import asyncio

HIDE_NULL = True

class VideoDownloadConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        video_url = text_data_json.get('video_url')

        if video_url:
            video_info = await self.get_video_info(video_url)

            if video_info:
                response_data = {
                    'status': 'success',
                    'video_info': video_info
                }
            else:
                response_data = {
                    'status': 'error',
                    'error_message': 'Failed to fetch video info.'
                }

            await self.send(text_data=json.dumps(response_data))

    async def get_video_info(self, video_url):
        loop = asyncio.get_event_loop()
        try:
            video_info = await loop.run_in_executor(None, self.fetch_video_info, video_url)
            return video_info
        except Exception as e:
            logging.error(f"Error fetching video info: {e}")
            return None

    def fetch_video_info(self, video_url):
        try:
            ydl_opts = {
                'quiet': False,
                'extract_flat': True,
                'force_generic_extractor': True
            }
            with YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(video_url, download=False)
                video_info = {
                    'video_title': info_dict.get('title'),
                    'views': info_dict.get('view_count'),
                    'publish_date': info_dict.get('upload_date'),
                    'thumbnail_url': info_dict.get('thumbnail'),
                    'streams_info': [
                        {
                            'type': format.get('ext'),
                            'resolution': format.get('height'),
                            'filesize': format.get('filesize') / (1024 * 1024) if format.get('filesize') else None,
                            'url': format.get('url')
                        }
                        for format in info_dict.get('formats', [])
                    ]
                }

                if HIDE_NULL:
                    video_info['streams_info'] = [stream for stream in video_info['streams_info'] if stream['filesize'] is not None]

                categorized_streams = {}
                for stream in video_info['streams_info']:
                    stream_type = stream['type']
                    if stream_type not in categorized_streams:
                        categorized_streams[stream_type] = []
                    categorized_streams[stream_type].append(stream)

                for stream_type, streams in categorized_streams.items():
                    streams.sort(key=lambda x: (-x['filesize'] if x['filesize'] else float('inf')))
                    streams.sort(key=lambda x: (-x['resolution'] if x['resolution'] else 0))
                video_info['streams_info'] = [stream for streams in categorized_streams.values() for stream in streams]
                return video_info

        except Exception as e:
            logging.error(f"Error fetching video info: {e}")
            return None
