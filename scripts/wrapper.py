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
