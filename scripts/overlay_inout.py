import overlay
import info
import sys
import subprocess
def time_intro():
    result = subprocess.run(
        ["ffprobe.exe","-i",
         info.get_seg_source_mp4("_intro"),
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

def generate_intro(first_segment):
    time_info = info.get_seg_time_info(first_segment, None)
    intro_length = time_intro()
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
    frame_image.save("build/splits/_outro.png")

if __name__ == "__main__":
    if sys.argv[1] == "intro":
        generate_intro(sys.argv[2])
    elif sys.argv[1] == "outro":
        generate_outro(sys.argv[2])
