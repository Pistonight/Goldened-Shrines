from buildutil.task import ITaskDefinition
from buildutil import paths
from buildutil import info
import os

class TaskDefDownload(ITaskDefinition):
    def __init__(self, segment_name) -> None:
        super().__init__()
        self.segment_name = segment_name

    def get_description(self):
        return f"Download {self.segment_name} segment"
    def get_color(self):
        return "\033[1;31m"
    def get_dependencies(self):
        return []
    
    def _name(self) -> str:
        return f"{self.segment_name}.download"
    def _hash_files(self) -> list[str]:
        return [
            paths.seg_toml(self.segment_name),
            paths.seg_download_mp4(self.segment_name)
        ]

    def prepare(self):
        os.makedirs("build/download", exist_ok=True)
        output_name = paths.seg_download_mp4(self.segment_name)
        if os.path.exists(output_name):
            os.remove(output_name)

    def _exe_args(self):
        link = info.get_seg_info(self.segment_name)["link"]
        return [
            "yt-dlp",
            link,
            "-o", paths.seg_download_mp4(self.segment_name)
        ]
