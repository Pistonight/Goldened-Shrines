from enum import Enum
from subproc import start_subprocess
import os
import info
import hash


class TaskDefGenerateMergeVideo(ITaskDefinition):
    def __init__(self, total_segments):
        super().__init__()
        self.total_segments = total_segments
    def get_description(self):
        return "Encoding final merged video                                                                 "
    def get_dependencies(self):
        deps = [
            (TaskType.EncodeTrailer,0), 
            (TaskType.EncodeCredits,0), 
            (TaskType.EncodeIntro,0),
            (TaskType.EncodeOutro,0)
        ]

        for s in range(self.total_segments):
            deps.append((TaskType.EncodeOverlay, s))
        return deps
    def update_hash(self, do_update):
        return hash.test_files(
            "build/hash/merge.hash.txt",
            [
                "build/merge/filelist.txt",
                "build/merge/merged.mp4",
                "build/encode/_intro.mp4",
                "build/encode/_outro.mp4",
                "build/encode/_trailer.mp4",
                "build/encode/_credits.mp4"
            ],
            do_update
        )
    def prepare(self):
        os.makedirs("build/merge", exist_ok=True)
        with open("build/merge/filelist.txt", "w+", encoding="utf-8") as out_file:
            #out_file.write("file ../encode/_trailer.mp4\n")
            #out_file.write("file ../encode/_intro.mp4\n")
            seg_names = info.load_seg_names()
            for seg_name in seg_names:
                out_file.write(f"file ../../{info.get_seg_overlay_mp4(seg_name)}\n")
            #out_file.write("file ../encode/_outro.mp4\n")
            #out_file.write("file ../encode/_credits.mp4\n")

    def execute(self):
        return start_subprocess(
            [
                "ffmpeg",
                "-y",
                "-hwaccel", "nvdec",
                "-hwaccel_output_format", "cuda",
                "-f", "concat",
                "-safe", "0",
                "-i", "build/merge/filelist.txt",
                "-framerate", "30",
                "-filter_complex",
                "scale_cuda=1920:1080,hwdownload,format=nv12 [base]",
                "-c", "copy",
                "-map", "[base]",
                "-map", "0:a",
                "-c:v", "h264_nvenc",
                "-b:v", "6M",
                "-c:a", "copy",
                "-fps_mode", "passthrough",
                "build/merge/merged.mp4"
            ],
            "build/logs/merge"
        )
