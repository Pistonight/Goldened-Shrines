TABLE_BEFORE="""
<!-- This is the HTML segment for segment tables. Not meant to be used as a page-->
<style>
    .time-table{
        text-align: center;
    }
    .time-table td {
        border: 1px solid grey;
    }
</style>
<table class="time-table">
    <thead>
        <tr>
            <th></th>
            <th>SRN #</th>
            <th>Segment Name</th>
            <th>Segment Time</th>
            <th>Split Time</th>
            <th>Runner</th>
            <th>Video Link</th>
        </tr>
    </thead>
    <tbody>
"""
TABLE_AFTER="""
    </tbody>
</table>
"""

import info
import tc

def generate_table():
    with open("docs/latest.html", "w+", encoding="utf-8") as out_file:
        out_file.write(TABLE_BEFORE)
        seg_names = info.load_seg_names()

        for seg in seg_names:
            out_file.write("<tr>\n")
           
            seg_info = info.get_seg_info(seg)
            seg_time_info = info.get_seg_time_info(seg)
            # Image
            icon_name = seg_info["icon"]
            out_file.write(f"<td><img width=\"24px\" height=\"auto\" src=\"./images/{icon_name}_Gold_.png\"/></td>\n")
            # Shrine Number
            shrine_number = info.get_3char_seg_num(seg_time_info["shrine_number"])
            out_file.write(f"<td>{shrine_number}</td>\n")
            # Name
            split_name = info.get_seg_spaced_name(seg)
            out_file.write(f"<td>{split_name}</td>\n")
            # Segment Time
            seg_frames = seg_time_info["segment_time"]
            seg_time = tc.frm_to_strh(seg_frames)
            out_file.write(f"<td>{seg_time}</td>\n")
            # Split Time
            split_frames = seg_time_info["start_frame"] + seg_frames
            split_time = tc.frm_to_strh(split_frames)
            out_file.write(f"<td>{split_time}</td>\n")
            # Runner
            runner = seg_info["runner"]
            out_file.write(f"<td>{runner}</td>\n")
            # Link
            link = seg_info["link"]
            if link.find("youtu") != -1:
                vendor = "YouTube"
            else:
                vendor = "Video"
            out_file.write(f"<td><a href=\"{link}\">{vendor}</a></td>\n")
            out_file.write("</tr>\n")
        out_file.write(TABLE_AFTER)
