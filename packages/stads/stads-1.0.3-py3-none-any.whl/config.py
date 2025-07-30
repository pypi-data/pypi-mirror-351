from importlib.resources import files, as_file
import data.video_sequences

from .read_images import get_frames_from_mp4

SIGMA = 4
KERNEL_SIZE = int(SIGMA * 3) + 1

video_resource = files(data.video_sequences).joinpath("dendrites_one.mp4")
with as_file(video_resource) as video_path:
    REFERENCE_VIDEO_SEQUENCE = get_frames_from_mp4(str(video_path), 100)

if REFERENCE_VIDEO_SEQUENCE is None:
    raise FileNotFoundError(f"Video could not be loaded: {video_path}")
