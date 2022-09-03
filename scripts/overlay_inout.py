import overlay
import info
import sys
def generate_intro(first_segment, intro_length):
    time_info = info.get_seg_time_info(first_segment, None)
    time_info["shrine_number"] = 0
    start=-intro_length
    time_info["start_frame"] = start
    time_info["segment_time"]=intro_length
    fonts = overlay.load_fonts()
    base = overlay.get_base_image("_empty", time_info, fonts)
    for i in range(intro_length):
        frame_image = overlay.draw_frame(base, start, i, fonts)
        frame_image.save("build/splits/_intro/%05d.png" % i)

def generate_outro(last_segment):
    time_info = info.get_seg_time_info(last_segment, None)
    time_info["shrine_number"] = 120
    final_time = time_info["segment_time"] + time_info["start_frame"]
    time_info["splits"][-1]["segment_time"] = time_info["segment_time"]
    time_info["splits"][-1]["split_time"] = final_time
    fonts = overlay.load_fonts()
    base = overlay.get_base_image("_gg", time_info, fonts)
    frame_image = overlay.draw_frame(base, final_time+1, -1, fonts)
    frame_image.save("build/splits/_outro/split.png")

if __name__ == "__main__":
    if sys.argv[1] == "intro":
        generate_intro(sys.argv[2], int(sys.argv[3]))
    elif sys.argv[1] == "outro":
        generate_outro(sys.argv[2])
