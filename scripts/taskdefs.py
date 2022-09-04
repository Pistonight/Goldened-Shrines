from enum import Enum
from subproc import start_subprocess
import os
import info
import hash

def encoding_overlay_args(input_mp4, input_png, output_mp4):
    if input_png is None:
        # re-encode
        return [
                "ffmpeg",
                "-y",
                "-hwaccel", "nvdec",
                "-hwaccel_output_format", "cuda",
                "-i", input_mp4,
                "-framerate", "30",
                "-filter_complex",
                "scale_cuda=1920:1080,hwdownload,format=nv12 [base]",
                "-map", "[base]",
                "-map", "0:a",
                "-c:v", "h264_nvenc",
                "-b:v", "6M",
                "-c:a", "copy",
                "-fps_mode", "passthrough",
                output_mp4
        ]
    return [
                "ffmpeg.exe",
                "-y",
                "-hwaccel",               "nvdec",
                "-hwaccel_output_format", "cuda",
                "-i",                     input_mp4,
                "-framerate",             "30",
                "-thread_queue_size",     "4096",
                "-i",                     input_png,
                "-filter_complex", 
                "scale_cuda=1920:1080,hwdownload,format=nv12 [base]; [base][1:v]overlay=10:728 [out]",
                "-map",                   "[out]", 
                "-map",                   "0:a",
                "-c:v",                   "h264_nvenc",
                "-c:a",                   "copy",
                "-b:v",                   "6M",
                "-fps_mode",              "passthrough",
                output_mp4
            ]

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

    # Download trailer, intro, credits, and outro
    # Dependency: None
    DownloadTrailer = 0x21
    DownloadIntro = 0x22
    DownloadOutro = 0x23
    DownloadCredits = 0x24

    # Time intro and generate intro splits
    # Dependency: GenerateTime for first segment, Download intro
    GenerateIntro = 0x30
    # Generate outro splits
    # Dependency: GenerateTime for last segment, Download outro
    GenerateOutro = 0x31

    # Encode intro
    # Dependency: GenerateIntro
    EncodeIntro = 0x40

    # Encode outro
    # Dependency: GenerateOutro
    EncodeOutro = 0x41

    # Encode trailer
    # Dependency: DownloadTrailer
    EncodeTrailer = 0x42

    # Encode credits
    # Dependency: DownloadCredits
    EncodeCredits = 0x43

    # Generate time table html
    # Dependency: GenerateTime for last segment
    GenerateTimeTable = 0x09

    # Generate the relase web page
    # Dependency: GenerateTimeTable
    GenerateWebPage = 0x0A

    # Merge the segments
    # Dependency: EncodeOverlay for all segments and extra videos
    GenerateMergeVideo = 0x0B

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

class TaskDefDownloadExtra(ITaskDefinition):
    def __init__(self, extra_name) -> None:
        super().__init__()
        self.extra_name = extra_name
    def output_mp4(self):
        return f"build/download/_{self.extra_name}.mp4"
    def get_description(self):
        return f"\033[1;31mDownload {self.output_mp4()}                               \033[0m"
    def get_dependencies(self):
        return []
    def update_hash(self, do_update):
        return hash.test_files(
            f"build/hash/_{self.extra_name}.download.hash.txt",
            [
                "video.toml",
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
        link = info.get_extra_video_link(self.extra_name)
        return start_subprocess(
            [
                "yt-dlp",
                link,
                "-o", self.output_mp4()
            ],
            f"build/logs/_{self.extra_name}.download"
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

class TaskDefEncodeOverlay(ITaskDefinition):
    def __init__(self, segment, segment_name):
        super().__init__()
        self.segment = segment
        self.segment_name = segment_name
    def is_gpu(self):
        return True
    def get_description(self):
        return f"\033[1;34mEncode Overlay for {self.segment_name}                                                      \033[0m"
    def get_dependencies(self):
        return [
            (TaskType.GenerateSplit_0, self.segment),
            (TaskType.GenerateSplit_1, self.segment),
            (TaskType.GenerateSplit_2, self.segment),
            (TaskType.GenerateSplit_3, self.segment),
            (TaskType.GenerateSplit_4, self.segment),
            (TaskType.GenerateSplit_5, self.segment),
            (TaskType.GenerateSplit_6, self.segment),
            (TaskType.GenerateSplit_7, self.segment),
            (TaskType.GenerateSplit_8, self.segment),
            (TaskType.GenerateSplit_9, self.segment),
            (TaskType.GenerateSplit_a, self.segment),
            (TaskType.GenerateSplit_b, self.segment),
            (TaskType.GenerateSplit_c, self.segment),
            (TaskType.GenerateSplit_d, self.segment),
            (TaskType.GenerateSplit_e, self.segment),
        ]

    def update_hash(self, do_update):
        return hash.test_files(
             f"build/hash/{self.segment_name}.encode.hash.txt",
            [
                info.format_seg_split_frame(self.segment_name, 0),
                info.get_seg_source_mp4(self.segment_name),
                info.get_seg_overlay_mp4(self.segment_name)
            ],
            do_update
        )
    def prepare(self):
        os.makedirs("build/encode", exist_ok=True)

    def execute(self):
        return start_subprocess(
            encoding_overlay_args(
                info.get_seg_source_mp4(self.segment_name),
                info.get_seg_split_overlay_series(self.segment_name),
                info.get_seg_overlay_mp4(self.segment_name)
            ),
            f"build/logs/{self.segment_name}.encode"
        )

class TaskDefGenerateTimeTable(ITaskDefinition):
    def __init__(self, segment_names) -> None:
        super().__init__()
        self.total_segments = len(segment_names)
        self.segment_names = segment_names

    def get_description(self):
        return f"Generate Time Table                                                     "
    def get_dependencies(self):
        return [(TaskType.GenerateTime, self.total_segments-1)]
    def update_hash(self, do_update):
        dep_files = []
        for segment_name in self.segment_names:
            dep_files.append(info.get_seg_time_toml(segment_name))
        dep_files.append("docs/latest.html")
        return hash.test_files(
            f"build/hash/timetable.hash.txt",
            dep_files,
            do_update
        )
    def prepare(self):
        pass
    def execute(self):
        return start_subprocess(
            [
                "python3", "scripts/timetable.py"
            ],
            f"build/logs/timetable"
        )

class TaskDefGenerateIntro(ITaskDefinition):
    def __init__(self, first_seg_name) -> None:
        super().__init__()
        self.first_segment_name = first_seg_name

    def get_description(self):
        return f"\033[1;32mGenerate Intro Split\033[0m                                                    "
    def get_dependencies(self):
        return [(TaskType.GenerateTime, 0)]
    def update_hash(self, do_update):
        dep_files = []
        dep_files.append(info.get_seg_time_toml(self.first_segment_name))
        dep_files.append("build/splits/_intro/00000.png")
        dep_files.append("build/download/_intro.mp4")
        return hash.test_files(
            f"build/hash/_intro.split.hash.txt",
            dep_files,
            do_update
        )
    def prepare(self):
        os.makedirs("build/splits/_intro", exist_ok=True)
    def execute(self):
        return start_subprocess(
            [
                "python3", "scripts/overlay_inout.py",
                "intro",
                self.first_segment_name
            ],
            f"build/logs/_intro.split"
        )

class TaskDefGenerateOutro(ITaskDefinition):
    def __init__(self, last_seg_name, total_segments) -> None:
        super().__init__()
        self.total_segments = total_segments
        self.last_segment_name = last_seg_name

    def get_description(self):
        return f"\033[1;32mGenerate Outro Split\033[0m                                                    "
    def get_dependencies(self):
        return [(TaskType.GenerateTime, self.total_segments-1)]
    def update_hash(self, do_update):
        dep_files = []
        dep_files.append(info.get_seg_time_toml(self.last_segment_name))
        dep_files.append("build/splits/_outro.png")
        dep_files.append("build/download/_outro.mp4")
        return hash.test_files(
            f"build/hash/_outro.split.hash.txt",
            dep_files,
            do_update
        )
    def prepare(self):
        os.makedirs("build/splits", exist_ok=True)
    def execute(self):
        return start_subprocess(
            [
                "python3", "scripts/overlay_inout.py",
                "outro",
                self.last_segment_name
            ],
            f"build/logs/_outro.split"
        )

class TaskDefEncodeIntro(ITaskDefinition):
    def __init__(self):
        super().__init__()
    def is_gpu(self):
        return True
    def get_description(self):
        return f"\033[1;34mEncode Intro                                                      \033[0m"
    def get_dependencies(self):
        return [(TaskType.GenerateIntro, 0)]

    def update_hash(self, do_update):
        return hash.test_files(
             f"build/hash/_intro.encode.hash.txt",
            [
                info.format_seg_split_frame("_intro", 0),
                info.get_seg_source_mp4("_intro"),
                info.get_seg_overlay_mp4("_intro")
            ],
            do_update
        )
    def prepare(self):
        os.makedirs("build/encode", exist_ok=True)

    def execute(self):
        return start_subprocess(
            encoding_overlay_args(
                info.get_seg_source_mp4("_intro"),
                info.get_seg_split_overlay_series("_intro"),
                info.get_seg_overlay_mp4("_intro")
            ),
            "build/logs/_intro.encode"
        )

class TaskDefEncodeOutro(ITaskDefinition):
    def __init__(self):
        super().__init__()
    def is_gpu(self):
        return True
    def get_description(self):
        return f"\033[1;34mEncode Outro                                                     \033[0m"
    def get_dependencies(self):
        return [(TaskType.GenerateOutro, 0)]

    def update_hash(self, do_update):
        return hash.test_files(
             f"build/hash/_outro.encode.hash.txt",
            [
                "build/splits/_outro.png",
                info.get_seg_source_mp4("_outro"),
                info.get_seg_overlay_mp4("_outro")
            ],
            do_update
        )
    def prepare(self):
        os.makedirs("build/encode", exist_ok=True)

    def execute(self):
        return start_subprocess(
            encoding_overlay_args(
                info.get_seg_source_mp4("_outro"),
                "build/splits/_outro.png",
                info.get_seg_overlay_mp4("_outro")
            ),
            "build/logs/_outro.encode"
        )

class TaskDefGenerateWebPage(ITaskDefinition):
    def __init__(self, last_seg_name) -> None:
        super().__init__()
        self.last_segment_name = last_seg_name

    def get_description(self):
        return f"Writing index.html                                                    "
    def get_dependencies(self):
        return [(TaskType.GenerateTimeTable, 0)]
    def update_hash(self, do_update):
        dep_files = ["docs/latest.html", "docs/index.html"]
        return hash.test_files(
            f"build/hash/webpage.hash.txt",
            dep_files,
            do_update
        )
    def prepare(self):
        pass
    def execute(self):
        return start_subprocess(
            [
                "python3", "scripts/webpage.py", self.last_segment_name
            ],
            f"build/logs/webpage"
        )

class TaskDefEncodeExtra(ITaskDefinition):
    def __init__(self, video, dependency):
        super().__init__()
        self.video = video
        self.dependency = dependency
    def is_gpu(self):
        return True
    def get_description(self):
        return f"\033[1;34mEncode {self.video}                                                     \033[0m"
    def get_dependencies(self):
        return [(self.dependency, 0)]

    def update_hash(self, do_update):
        return hash.test_files(
             f"build/hash/{self.video}.encode.hash.txt",
            [
                info.get_seg_source_mp4(self.video),
                info.get_seg_overlay_mp4(self.video)
            ],
            do_update
        )
    def prepare(self):
        os.makedirs("build/encode", exist_ok=True)

    def execute(self):
        return start_subprocess(
            encoding_overlay_args(
                info.get_seg_source_mp4(self.video),
                None,
                info.get_seg_overlay_mp4(self.video)
            ),
            f"build/logs/{self.video}.encode"
        )

class TaskDefGenerateMergeVideo(ITaskDefinition):
    def __init__(self, total_segments):
        super().__init__()
        self.total_segments = total_segments
    def get_description(self):
        return "Making final merged video                                                                 "
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
            out_file.write("file ../encode/_trailer.mp4\n")
            out_file.write("file ../encode/_intro.mp4\n")
            seg_names = info.load_seg_names()
            for seg_name in seg_names:
                out_file.write(f"file ../../{info.get_seg_overlay_mp4(seg_name)}\n")
            out_file.write("file ../encode/_outro.mp4\n")
            out_file.write("file ../encode/_credits.mp4\n")

    def execute(self):
        return start_subprocess(
            [
                "ffmpeg",
                "-y",
                "-f", "concat",
                "-safe", "0",
                "-i", "build/merge/filelist.txt",
                "-c", "copy",
                "build/merge/merged.mp4"
            ],
            "build/logs/merge"
        )
