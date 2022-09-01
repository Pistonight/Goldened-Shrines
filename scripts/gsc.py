"""Standalone step to generate overlay for one segment with multi processes"""

import gensplit
import info
import sys
from multiprocessing import Process

MULTI = 15

def gen_one_frame_set(seed, segment, base_image, start_frame, total_frame):
    fonts = gensplit.load_fonts()
    for i in range(seed, total_frame, MULTI):
        frame_image = gensplit.draw_frame(base_image, start_frame, i, fonts)
        info.set_seg_split_overlay_frame(segment, frame_image, i)

def generate_overlay_multi(segment):

    info.ensure_seg_split_overlay_dir(segment)
    time_info = info.get_seg_time_info(segment, None)
    base_image = gensplit.get_base_image(segment, time_info)
    start = time_info["start_frame"]
    total = time_info["segment_time"]

    processes = []

    for i in range(MULTI):
        processes.append(Process(target = gen_one_frame_set, args=(i, segment, base_image, start, total)))
        processes[i].start()
        
    for p in processes:
        p.join()


if __name__ == "__main__":
    segment = sys.argv[1]

    print(f"Using {MULTI} processes to generate overlay...", end="", flush=True)
    generate_overlay_multi(segment)
    print("Done")


    
