from buildutil import info, timecode, paths
import sys
GENERATOR_METATITLE = "<!-- GENERATOR METATITLE -->"
GENERATOR_TITLE = "<!-- GENERATOR TITLE -->"
GENERATOR_TABLE = "<!-- GENERATOR TABLE -->"

def generate_index_html(last_segment):
    time_info = info.get_seg_time_info(last_segment)
    final_time_frames = time_info["start_frame"] + time_info["segment_time"]
    final_time_string = timecode.frm_to_strh(final_time_frames, show_ms=False)
    lines: list[str] = []

    title = f"All Shrines in {final_time_string} by The BOTW Community"

    with open(paths.index_html(), "r", encoding="utf-8") as file:
        for line in file:
            lines.append(line)
    with open(paths.index_html(), "w", encoding="utf-8") as file:
        skip_until = None
        for line in lines:
            if skip_until is not None:
                if line.startswith(skip_until):
                    skip_until = None
                    file.write(line)
                continue
            file.write(line)
            if line.startswith(GENERATOR_METATITLE):
                skip_until = GENERATOR_METATITLE
                file.write(f"<meta property=\"og:title\" content=\"{title}\" />\n")
                continue

            if line.startswith(GENERATOR_TITLE):
                skip_until = GENERATOR_TITLE
                file.write(f"<title>{title}</title>\n")
                continue

            if line.startswith(GENERATOR_TABLE):
                skip_until = GENERATOR_TABLE
                with open(paths.timetable_html(), "r", encoding="utf-8") as table:
                    for line in table:
                        file.write(line)

if __name__ == "__main__":
    generate_index_html(sys.argv[1])
