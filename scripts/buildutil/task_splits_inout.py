from buildutil.task import ITaskDefinition, TaskType
from buildutil import paths
import os

class TaskDefGenerateSplitsInout(ITaskDefinition):
    def __init__(self, segment_name, dep_seg_name, dep_seg_index) -> None:
        super().__init__()
        self.segment_name = segment_name
        self.dep_seg_name = dep_seg_name
        self.dep_seg_index = dep_seg_index

    def get_description(self):
        return f"Generate Splits for {self.segment_name}"
    def get_color(self):
        return "\033[1;33m"
    def get_dependencies(self):
        return [
            (TaskType.GenerateTime, self.dep_seg_index),
            (TaskType.DownloadIntro, 0),
            (TaskType.DownloadOutro, 0),
        ]
    
    def _name(self) -> str:
        return f"{self.segment_name}.split"
    def _hash_files(self) -> list[str]:
        return [
            paths.seg_time_toml(self.dep_seg_name),
            paths.seg_split_frame(self.segment_name, 0),
            paths.seg_download_mp4(self.segment_name)
        ]

    def prepare(self):
        os.makedirs(paths.seg_splits_dir(self.segment_name), exist_ok=True)
    
    def _exe_args(self):
        return [
            "python3", "scripts/build_overlay.py",
            self.segment_name,
            self.dep_seg_name 
        ]
