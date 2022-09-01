"""Wrapper for external commands"""
import subprocess 
import os
import info
import sys
import shutil

def execute_clean_segment(seg_name):
    if os.path.exists(info.get_seg_source_mp4(seg_name)):
        os.remove(info.get_seg_source_mp4(seg_name))
    if os.path.exists(info.get_seg_overlay_mp4(seg_name)):
        os.remove(info.get_seg_overlay_mp4(seg_name))
    if os.path.exists(info.get_times_gen_toml(seg_name)):
        os.remove(info.get_times_gen_toml(seg_name))
    if os.path.isdir(info.get_seg_split_overlay_dir(seg_name)):
        shutil.rmtree(info.get_seg_split_overlay_dir(seg_name))
    for p in ("merged.mp4", "filelist.txt", "docs/latest.html"):
        if os.path.exists(p):
            os.remove(p)

def execute_get_frame_count(seg_name):
    result = subprocess.run(
        ["ffprobe.exe","-i",
         info.get_seg_source_mp4(seg_name),
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
    
def execute_overlay_splits(seg_name):
    if os.path.exists(info.get_seg_overlay_mp4(seg_name)):
        os.remove(info.get_seg_overlay_mp4(seg_name))
    result = subprocess.run(
        ["ffmpeg.exe",
         "-y",
         "-hwaccel",               "nvdec",
         "-hwaccel_output_format", "cuda",
         "-i",                     info.get_seg_source_mp4(seg_name),
         "-framerate",             "30",
         "-thread_queue_size",     "4096",
         "-i",                     info.get_seg_split_overlay_series(seg_name),
         "-filter_complex", 
         "scale_cuda=1920:1080,hwdownload,format=nv12 [base]; [base][1:v]overlay=10:728 [out]",
         "-map",                   "[out]", 
         "-map",                   "0:a",
         "-c:v",                   "h264_nvenc",
         "-b:v", "6M",
         info.get_seg_overlay_mp4(seg_name)
        ]
        # ,
        # stdout=subprocess.DEVNULL,
        # stderr=subprocess.STDOUT
    )
    if result.returncode != 0:
        sys.exit(result.returncode)

def execute_merge():
    with open("filelist.txt", "w+", encoding="utf-8") as out_file:
        seg_names = info.load_seg_names()
        for seg_name in seg_names:
            out_file.write(f"file {info.get_seg_overlay_mp4(seg_name)}\n")

    result = subprocess.run(
        ["ffmpeg.exe",
        "-y",
        "-f", "concat",
        "-i", "filelist.txt",
        "-safe", "0",
        "-c", "copy",
        "merged.mp4"
        ]
        ,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT
    )
    if result.returncode != 0:
        sys.exit(result.returncode)
