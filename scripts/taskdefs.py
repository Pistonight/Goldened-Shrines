from enum import Enum
from subproc import start_subprocess
import os
import info
import hash
class TaskType(Enum):  
    # Download the segment
    # Input: segments/<Segment>.toml
    # Dependency: None
    # Output: build/download/<Segment>.mp4
    Download = 0x02

    # Generate time info
    # Input: None
    # Dependency: Download for the segment, GenerateTime for previous 1 segment
    # Output: build/time/<Segment>.time.toml
    GenerateTime = 0x03

    # Generate split images
    # Input: None
    # Dependency: GenerateTime for the segment
    # Output: build/splits/<Segment>/*.png
    GenerateSplit_0= 0x10
    GenerateSplit_1= 0x11
    GenerateSplit_2= 0x12
    GenerateSplit_3= 0x13
    GenerateSplit_4= 0x14
    GenerateSplit_5= 0x15
    GenerateSplit_6= 0x16
    GenerateSplit_7= 0x17
    GenerateSplit_8= 0x18
    GenerateSplit_9= 0x19
    GenerateSplit_a= 0x1a
    GenerateSplit_b= 0x1b
    GenerateSplit_c= 0x1c
    GenerateSplit_d= 0x1d
    GenerateSplit_e= 0x1e

    # Encode overlay onto video
    # Input: None
    # Dependency: All GenerateSplit_x for the segment
    # Output: build/overlayed/<Segment>.mp4
    EncodeOverlay = 0x05

    # Synchronous
    # Generate time table html
    # Dependency: GenerateTime for last segment
    GenerateTimeTable = 0x07

    # Synchronous
    # Generate the relase web page
    # Dependency: GenerateTimeTable
    GenerateWebPage = 0x08

    # Merge the segments
    # Dependency: EncodeOverlay for all segments
    GenerateMergeVideo = 0x09

class ITaskDefinition:
    def get_dependencies(self):
        """return dependencies (type, seg)"""
        pass
    def is_gpu(self):
        """Return if the task should be limited with GPU concurrency limit"""
        return False
    def execute(self):
        """Start subprocess to execute the task, and return the process"""
        pass
    def get_description(self):
        """Get description"""
        pass
    def update_hash(self, do_update) -> bool:
        """Test input and output cache hit"""
        pass
    def prepare(self):
        """Run setup, like creating build directories. This is executed synchronously on the main process"""
        pass

class TaskDefDownload(ITaskDefinition):
    def __init__(self, segment_name) -> None:
        super().__init__()
        self.segment_name = segment_name
    def output_mp4(self):
        return info.get_seg_source_mp4(self.segment_name)
    def get_description(self):
        return f"\033[1;31mDownload {self.output_mp4()}                               \033[0m"
    def get_dependencies(self):
        return []
    def update_hash(self, do_update):
        return hash.test_files(
            f"build/hash/{self.segment_name}.download.hash.txt",
            [
                f"segments/{self.segment_name}.toml",
                self.output_mp4()
            ],
            do_update
        )
    def prepare(self):
        os.makedirs("build/download", exist_ok=True)
        output_name = self.output_mp4()
        if os.path.exists(output_name):
            os.remove(output_name)
    def execute(self):
        link = info.get_seg_info(self.segment_name, "link")
        return start_subprocess(
            [
                "yt-dlp",
                link,
                "-o", self.output_mp4()
            ],
            f"build/logs/{self.segment_name}.download"
        )

class TaskDefTime(ITaskDefinition):
    def __init__(self, segment, segment_name, segment_context) -> None:
        super().__init__()
        self.segment = segment
        self.segment_name = segment_name
        self.segment_context = segment_context

    def input_mp4(self):
        return info.get_seg_source_mp4(self.segment_name)
    def output_toml(self):
        return info.get_seg_time_toml(self.segment_name)
    def get_description(self):
        return f"\033[1;32mTime {self.input_mp4()}                                  \033[0m"
    def get_dependencies(self):
        deps = [(TaskType.Download, self.segment)]
        if self.segment > 0:
            deps.append((TaskType.GenerateTime, self.segment-1))
        return deps
    def update_hash(self, do_update):
        return hash.test_files(
            f"build/hash/{self.segment_name}.time.hash.txt",
            [
                self.output_toml(),
                self.input_mp4(),
                info.get_seg_name_file()
            ],
            do_update
        )
    def prepare(self):
        os.makedirs("build/time", exist_ok=True)
    def execute(self):
        args = [
                    "python3", "scripts/timeseg.py",
                    self.segment_name
                ]
        for context_name in self.segment_context:
            args.append(context_name)
        return start_subprocess(args,f"build/logs/{self.segment_name}.time")

GENERATE_SPLIT_STEP = 15
class TaskDefGenerateSplits(ITaskDefinition):
    def __init__(self, segment, segment_name, seed) -> None:
        super().__init__()
        self.segment = segment
        self.segment_name = segment_name
        self.seed = seed

    def input_toml(self):
        return info.get_seg_time_toml(self.segment_name)
    def get_description(self):
        return f"\033[1;33mGenerate Splits for {self.segment_name} (Group {self.seed+1})                  \033[0m"
    def get_dependencies(self):
        return [(TaskType.GenerateTime, self.segment)]
    def update_hash(self, do_update):
        return hash.test_files(
            f"build/hash/{self.segment_name}.split{self.seed}.hash.txt",
            [
                self.input_toml(),
                info.format_seg_split_frame(self.segment_name, self.seed)
            ],
            do_update
        )
    def prepare(self):
        os.makedirs(info.get_seg_split_overlay_dir(self.segment_name), exist_ok=True)
    def execute(self):
        return start_subprocess(
            [
                "python3", "scripts/overlay.py",
                self.segment_name,
                str(self.seed),
                str(GENERATE_SPLIT_STEP)
            ],
            f"build/logs/{self.segment_name}.splits{self.seed}"
        )

class TaskDefGenerateMergeVideo:
    def __init__(self, total_segments):
        self.total_Segments = total_segments
    def get_description(self):
        return "Merge final video                                                                 "
    def get_dependencies(self):
        deps = []
        for s in range(self.total_segments):
            deps.append((TaskType.EncodeOverlay, s))
        return deps
    def update_hash(self, do_update):
        return hash.test_files(
            "build/hash/merge.hash.txt",
            [
                "build/merge/filelist.txt",
                "build/merge/merged.mp4"
            ],
            do_update
        )
    def prepare(self):
        os.makedirs("build/merge", exist_ok=True)
        with open("build/merge/filelist.txt", "w+", encoding="utf-8") as out_file:
            seg_names = info.load_seg_names()
            for seg_name in seg_names:
                out_file.write(f"file {info.get_seg_overlay_mp4(seg_name)}\n")

    def execute(self):
        return start_subprocess(
            [
                "ffmpeg",
                "-y",
                "-f", "concat",
                "-i", "build/merge/filelist.txt",
                "-safe", "0",
                "-c", "copy",
                "build/merge/merged.mp4"
            ],
            "build/logs/merge"
        )
