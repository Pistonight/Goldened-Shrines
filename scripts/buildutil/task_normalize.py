from buildutil.task import ITaskDefinition, TaskType
from buildutil import paths
from buildutil import info
import os

from buildutil.task_encode import TaskDefEncodeOverlay

class TaskDefNormalize(ITaskDefinition):
    def __init__(self, segment, segment_name):
        super().__init__()
        self.segment = segment
        self.segment_name = segment_name

    def get_description(self):
        return f"Normalize {self.segment_name}"
    def get_color(self):
        return "\033[1;35m"
    def get_dependencies(self):
        if self.segment_name.startswith("_"):
            return [
                (TaskType.EncodeTransition, 0)
            ]
        return [
            (TaskType.EncodeOverlay, self.segment)
        ]
    def _name(self) -> str:
        return f"{self.segment_name}.normalize"
    def _hash_files(self) -> list[str]:
        return [
            paths.profiles_toml(),
            paths.hash_txt(TaskDefEncodeOverlay(self.segment, self.segment_name)._name())
        ]

    def prepare(self):
        os.makedirs("build/normalize", exist_ok=True)

    def _exe_args(self):
        profile_name = info.get_seg_info(self.segment_name)["profile"]
        profile = info.get_profiles()[profile_name]
        target = profile["audio_normalize_target"]

        return [
            "ffmpeg-normalize",
            paths.seg_overlay_mp4(self.segment_name),
            "-o", paths.seg_normalized_mp4(self.segment_name),
            "-c:a", "aac",
            "-t", target,
            "-nt", "rms", 
            "-f"
        ]

