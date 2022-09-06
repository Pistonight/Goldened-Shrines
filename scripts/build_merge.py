"""Wrapper for merging segments"""

import subprocess
import sys
from buildutil import paths, timecode, time

def execute_merge(segment_names,has_beginning,has_ending,output_mp4,middle_mp4,output_filelist):
    if not has_beginning and not has_ending:
        middle_mp4 = output_mp4

    # First encode all middle segments together with audio patches
    args = [
        "ffmpeg",
        "-y",
        "-hwaccel", "nvdec"
    ]
    concat_inputs = "" # [0:v][0:a][1:v][1:a]...
    concat_n = len(segment_names)
    patch_filters = [] # joined by ; in the end
    amix_inputs = ["[acon]"]
    total_previous_frames = 0
    for i,segment_name in enumerate(segment_names):
        input_file = paths.seg_normalized_mp4(segment_name)
        input_frames = time.execute_frame_count(input_file) # use the exact input frames in case it's different from download
        args.extend([
            "-i", input_file
        ])
        concat_inputs+=f"[{i}:v][{i}:a]"
        if i == concat_n -1:
            break # no need to patch for last middle segment
        trim_start = str(timecode.frm_to_sec(input_frames-6))
        delay_start = str((timecode.frm_to_sec(input_frames-3) + timecode.frm_to_sec(total_previous_frames))*1000)
        patch_filters.append(f"[{i}:a]atrim=start={trim_start}:duration=200ms, afade=t=in:st=0:d=100ms, adelay={delay_start}|{delay_start}[{i}apatch]")
        amix_inputs.append(f"[{i}apatch]")
        
        total_previous_frames+=input_frames+1 # for some reason need to add 1 to make the offset right


    concat_filter = f"{concat_inputs}concat=n={concat_n}:v=1:a=1 [vcon][acon]"
    patch_filter = ";".join(patch_filters)
    amix_n = len(amix_inputs)
    amix_input = "".join(amix_inputs)
    amix_filter = f"{amix_input}amix=inputs={amix_n}:duration=longest:normalize=0[acon]"

    filter_complex = f"{concat_filter};{patch_filter};{amix_filter}"
    args.extend([
        "-filter_complex", filter_complex,
        "-map", "[vcon]",
        "-map", "[acon]",
        "-c:v", "h264_nvenc",
        "-b:v", "6M",
        "-c:a", "aac",
        middle_mp4
    ])
    print(args)
    result = subprocess.run(args)
    if result.returncode != 0:
        print("Wrapper: failed to encode middle segments")
        sys.exit(result.returncode)

    if not has_beginning and not has_ending:
        return

    # Second use concat demuxer to combine the beginning and end
   
    files = []
    if has_beginning:
        files.extend([
            paths.seg_normalized_mp4("_trailer"),
            paths.seg_normalized_mp4("_intro")
        ])
    files.append(middle_mp4)
    if has_ending:
        files.extend([
            paths.seg_normalized_mp4("_outro_transition"),
            paths.seg_normalized_mp4("_outro"),
            paths.seg_normalized_mp4("_credits")
        ])

    with open(output_filelist, "w+", encoding="utf-8") as filelist:
        for file in files:
            filelist.write(f"file ../../{file}\n")

    result = subprocess.run([
        "ffmpeg",
        "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", output_filelist,
        "-c", "copy",
        output_mp4
    ])
    
    sys.exit(result.returncode)

if __name__ == "__main__":
    has_beginning = sys.argv[1] != "0"
    has_ending = sys.argv[2] != "0"
    output_mp4 = sys.argv[3]
    middle_mp4 = sys.argv[4]
    output_filelist = sys.argv[5]
    segment_names = sys.argv[6:]
    execute_merge(segment_names, has_beginning, has_ending, output_mp4, middle_mp4, output_filelist)
