from buildutil.task import ITaskDefinition, TaskType
from buildutil import paths
import os

class TaskDefMerge(ITaskDefinition):
    def __init__(self, segment_names):
        super().__init__()
        self.total_segment = len(segment_names)
        self.segment_names = segment_names

    def get_description(self):
        return f"Merging all segments"
    def get_color(self):
        return "\033[1;37m"
    def get_dependencies(self):
        deps = [
            (TaskType.NormalizeTrailer, 0),
            (TaskType.NormalizeIntro, 0),
            (TaskType.NormalizeCredits, 0),
            (TaskType.NormalizeOutro, 0),
            (TaskType.NormalizeTransition, 0)
        ]
        for i in range(self.total_segment):
            deps.append((TaskType.Normalize, i))
        return deps

    def _name(self) -> str:
        return f"merge"
    def update_hash(self, _do_update) -> bool:
        return False

    def prepare(self):
        os.makedirs("build/merge", exist_ok=True)
        files = []
        files.append(paths.seg_normalized_mp4("_trailer"))
        files.append(paths.seg_normalized_mp4("_intro"))

        for i in range(self.total_segment):
            files.append(paths.seg_normalized_mp4(self.segment_names[i]))
        
        files.append(paths.seg_normalized_mp4("_outro_transition"))
        files.append(paths.seg_normalized_mp4("_outro"))
        files.append(paths.seg_normalized_mp4("_credits"))
        with open("build/merge/mergelist.txt", "w+", encoding="utf-8") as out_file:
            for file in files:
                out_file.write(f"file ../../{file}\n")

    def _exe_args(self):

        return [
            "ffmpeg",
            "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", "build/merge/mergelist.txt",
            "-c", "copy",
            "build/merge/merged.mp4"
        ]


