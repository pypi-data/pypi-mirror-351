import os
import whisper
from moviepy.editor import VideoFileClip
from .config import DEFAULT_PATHS

DEFAULT_WHISPER_MODEL_PATH = DEFAULT_PATHS["whisper"]

def get_whisper_model(module_size: str = "base", whisper_model_path: str = None):
    whisper_model_path = whisper_model_path or DEFAULT_WHISPER_MODEL_PATH
    return whisper.load_model(module_size, download_root=whisper_model_path)


def transcribe(
    audio_path: str,
    model_size: str = "small",
    language: str = "english",
    use_silence: bool = True,
    task=None,
    whisper_model_path: str = None
):
    model = get_whisper_model(module_size=model_size, whisper_model_path=whisper_model_path)
    return model.transcribe(audio_path, language=language)


def extract_audio_from_video(video_path: str, audio_path: str = None):
    if audio_path is None:
        dirname = os.path.dirname(video_path)
        audio_path = os.path.join(dirname, 'audio.wav')
    if os.path.isfile(video_path):
        clip = VideoFileClip(video_path)
        clip.audio.write_audiofile(audio_path)
        clip.close()
    return audio_path