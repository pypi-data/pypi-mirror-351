from importlib.resources import files, as_file
from .read_images import get_frames_from_mp4

SIGMA = 4
KERNEL_SIZE = int(SIGMA * 3) + 1

# Get the video file path using importlib.resources
try:
    video_resource = files("stads.data.video_sequences").joinpath("dendrites.mp4")
    with as_file(video_resource) as video_path:
        REFERENCE_VIDEO_SEQUENCE = get_frames_from_mp4(str(video_path), 100)

    if REFERENCE_VIDEO_SEQUENCE is None:
        raise FileNotFoundError(f"Video could not be loaded: {video_path}")
except Exception as e:
    raise ImportError(f"Failed to load reference video: {str(e)}")