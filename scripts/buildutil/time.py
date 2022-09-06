import sys
import subprocess
from buildutil import paths

def execute_frame_count(file):
    result = subprocess.run(
        ["ffprobe.exe","-i",
         file,
         "-v", "error",
         "-count_packets",
         "-select_streams", "v:0",
         "-show_entries", "stream=nb_read_packets",
         "-of", "csv=p=0"],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL)
    if result.returncode != 0:
        sys.exit(result.returncode)
    return int(result.stdout)

def execute_seg_frame_count(seg_name):
    return execute_frame_count(paths.seg_download_mp4(seg_name))
