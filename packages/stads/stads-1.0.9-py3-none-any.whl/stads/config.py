import os

from .read_images import get_frames_from_mp4

# Get absolute path to the root of your project
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

# Path to the hardcoded video file
VIDEO_PATH = os.path.join(PROJECT_ROOT, "data","yideo_sequences", "video.mp4")

# Now load the reference frames
SIGMA = 4
KERNEL_SIZE = int(SIGMA * 3) + 1

# Get the video file path using importlib.resources
REFERENCE_VIDEO_SEQUENCE = get_frames_from_mp4(VIDEO_PATH, 100)