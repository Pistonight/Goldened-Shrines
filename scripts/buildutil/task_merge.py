from buildutil.task import ITaskDefinition, TaskType
from buildutil import paths
import os

class TaskDefMerge(ITaskDefinition):
    def __init__(self, segment_names):
        super().__init__()
        self.total_segment = len(segment_names)
        self.segment_names = segment_names

    def is_gpu(self):
        return True
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

    def _exe_args(self):

        args = [
            "python3", "scripts/build_merge.py",
            "1", "1",
            "build/merge/merged.mp4",
            "build/merge/middle.mp4",
            "build/merge/mergelist.txt"
        ]
        args.extend(self.segment_names)

        return args


