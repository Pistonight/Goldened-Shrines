import sys
from buildutil import info, overlay, time

def generate_intro(first_segment):
    time_info = info.get_seg_time_info(first_segment)
    intro_length = time.execute_seg_frame_count("_intro")
    time_info["shrine_number"] = 0
    start=-intro_length
    time_info["start_frame"] = start
    time_info["segment_time"]=intro_length
    fonts = overlay.load_fonts()
    base = overlay.get_base_image("_intro", time_info, fonts)
    for i in range(intro_length):
        frame_image = overlay.draw_frame(base, start, i, fonts)
        info.set_seg_split_overlay_frame("_intro", frame_image, i)

def generate_outro(segment_name, last_segment):
    time_info = info.get_seg_time_info(last_segment)
    time_info["shrine_number"] = 120
    final_time = time_info["segment_time"] + time_info["start_frame"]
    time_info["splits"][-1]["segment_time"] = time_info["segment_time"]
    time_info["splits"][-1]["split_time"] = final_time
    fonts = overlay.load_fonts()
    base = overlay.get_base_image(segment_name, time_info, fonts)
    frame_image = overlay.draw_frame(base, final_time+1, -1, fonts)
    info.set_seg_split_overlay_frame(segment_name, frame_image, 0)

def generate_overlay(segment, seed, step):
    fonts = overlay.load_fonts()
    time_info = info.get_seg_time_info(segment)
    base = overlay.get_base_image(segment, time_info, fonts)
    start = time_info["start_frame"]
    for i in range(seed, time_info["segment_time"], step):
        frame_image = overlay.draw_frame(base, start, i, fonts)
        info.set_seg_split_overlay_frame(segment, frame_image, i)

if __name__ == "__main__":
    segment = sys.argv[1]
    if segment == "_intro":
        generate_intro(sys.argv[2])
    elif segment.startswith("_outro"):
        generate_outro(sys.argv[1], sys.argv[2])
    else:
        seed = int(sys.argv[2])
        step = int(sys.argv[3])
        generate_overlay(segment, seed, step)
