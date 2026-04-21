import time
import asyncio
from typing import (
    Any,
    Callable,
    Optional
)
from fractions import (
    Fraction
)

from aiortc.contrib.media import MediaRelay
from av import (
    VideoFrame,
    AudioFrame
)
from aiortc import (
    VideoStreamTrack,
    AudioStreamTrack,
    MediaStreamTrack,
    RTCPeerConnection,
    RTCSessionDescription,
    RTCDataChannel
)


class CustomVideoTrack(VideoStreamTrack):
    def __init__(
            self,
            frame_read_function: Callable,
            frame_per_second: int = 25,
            frame_format : str = 'bgr24',
    ):
        super().__init__()
        self.__frame_read_function = frame_read_function
        self.__frame_per_second = frame_per_second
        self.__frame_format = frame_format

        self.__time_base = Fraction(
            numerator=1,
            denominator=frame_per_second,
        )
        self.__presentation_timestamp = 0

        self.__loop: Optional[asyncio.AbstractEventLoop] = None

        self.__next_received_timestamp = time.time()
        self.__received_interval = 1 / frame_per_second

    async def recv(self) -> VideoFrame:
        if self.__loop is None:
            self.__loop = asyncio.get_running_loop()

        frame = await self.__loop.run_in_executor(
            executor=None,
            func=self.__frame_read_function,
        )

        frame = VideoFrame.from_ndarray(
            array=frame,
            format=self.__frame_format,
        )
        frame.time_base = self.__time_base
        frame.pts = self.__presentation_timestamp
        self.__presentation_timestamp += 1

        # sleep
        self.__next_received_timestamp += self.__received_interval
        wait_time = max(0.0, self.__next_received_timestamp - time.time())
        if wait_time > 0:
            await asyncio.sleep(wait_time)

        return frame


class CustomAudioTrack(AudioStreamTrack):
    def __init__(
            self,
            read_frame_function: Callable,
            sample_rate: int = 48000,
            samples_per_second: int = 960,
            channels: int = 1,
    ):
        super().__init__()
        self.__read_frame_function = read_frame_function
        self.__sample_rate = sample_rate
        self.__samples_per_second = samples_per_second
        self.__channels = channels

        self.__time_base = Fraction(
            numerator=1,
            denominator=sample_rate,
        )
        self.__presentation_timestamp = 0

        self.__loop: Optional[asyncio.AbstractEventLoop] = None

        self.__next_received_timestamp = time.time()
        self.__received_interval = 1 / samples_per_second

    async def recv(self) -> AudioFrame:
        if self.__loop is None:
            self.__loop = asyncio.get_running_loop()

        frame = await self.__loop.run_in_executor(
            executor=None,
            func=self.__read_frame_function,
        )

        frame = AudioFrame.from_ndarray(
            array=frame,
            format="s16",
            layout="mono" if self.__channels == 1 else "stereo",
        )
        frame.sample_rate = self.__sample_rate
        frame.time_base = self.__time_base
        frame.pts = self.__presentation_timestamp
        self.__presentation_timestamp += self.__samples_per_second

        # sleep
        self.__next_received_timestamp += self.__received_interval
        wait_time = max(0.0, self.__next_received_timestamp - time.time())
        if wait_time > 0:
            await asyncio.sleep(wait_time)

        return frame


class MediaStream:
    def __init__(
            self,
            video_frame_read_function:Optional [Callable] = None,
            audio_frame_read_function: Optional[Callable] = None,
            video_frame_per_second: int = 30,
    ):


        self.__video_track: Optional[CustomVideoTrack] = None
        if video_frame_read_function is not None:
            self.__video_track = CustomVideoTrack(
                frame_read_function=video_frame_read_function,
                frame_per_second=video_frame_per_second
            )

        self.__audio_track: Optional[CustomAudioTrack] = None
        if audio_frame_read_function is not None:
            self.__audio_track = CustomAudioTrack(
                read_frame_function=audio_frame_read_function,
            )

        self.__media_relay = MediaRelay()

    @property
    def video_track(self) -> MediaStreamTrack | None:
        if self.__video_track is None:
            return None
        return self.__media_relay.subscribe(self.__video_track)

    @property
    def audio_track(self) -> MediaStreamTrack | None:
        if self.__audio_track is None:
            return None
        return self.__media_relay.subscribe(self.__audio_track)

    @property
    def has_video_track(self) -> bool:
        return self.__video_track is not None

    @property
    def has_audio_track(self) -> bool:
        return self.__audio_track is not None
