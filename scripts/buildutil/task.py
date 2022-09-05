from enum import Enum
from buildutil import paths
from buildutil import hash
from buildutil import subproc

class TaskType(Enum):  
    # Download the segment
    # Input: segments/<Segment>.toml
    # Dependency: None
    # Output: build/download/<Segment>.mp4
    Download = 0x10

    # Download trailer, intro, credits, and outro
    # Dependency: None
    DownloadTrailer = 0x11
    DownloadIntro = 0x12
    DownloadTransition = 0x13
    DownloadOutro = 0x14
    DownloadCredits = 0x15

    # Generate time info
    # Input: None
    # Dependency: Download for the segment, GenerateTime for previous 1 segment
    # Output: build/time/<Segment>.time.toml
    GenerateTime = 0x20

    # Generate split images
    # Input: None
    # Dependency: GenerateTime for the segment
    # Output: build/splits/<Segment>/*.png
    GenerateSplit_0= 0x30
    GenerateSplit_1= 0x31
    GenerateSplit_2= 0x32
    GenerateSplit_3= 0x33
    GenerateSplit_4= 0x34
    GenerateSplit_5= 0x35
    GenerateSplit_6= 0x36
    GenerateSplit_7= 0x37

    # Time intro and generate intro splits
    # Dependency: GenerateTime for first segment, Download intro
    GenerateIntro = 0x38
    # Generate outro splits
    # Dependency: GenerateTime for last segment, Download outro
    GenerateOutro = 0x39

    # Encode overlay onto video
    # Input: None
    # Dependency: All GenerateSplit_x for the segment
    # Output: build/overlayed/<Segment>.mp4
    EncodeOverlay = 0x40
    # Encode trailer
    # Dependency: DownloadTrailer
    EncodeTrailer = 0x41
    # Encode intro
    # Dependency: GenerateIntro
    EncodeIntro = 0x42
     # Encode outro
    # Dependency: GenerateOutro
    EncodeTransition = 0x43
    # Encode outro
    # Dependency: GenerateOutro
    EncodeOutro = 0x44
    # Encode credits
    # Dependency: DownloadCredits
    EncodeCredits = 0x45

    # Generate time table html
    # Dependency: GenerateTime for last segment
    GenerateTimeTable = 0x50

    # Generate the relase web page
    # Dependency: GenerateTimeTable
    GenerateWebPage = 0x60

    # Normalize encoded video
    Normalize = 0x70
    NormalizeExtra = 0x71
    # Test segment and the
    TestMerge = 0x80

    # Merge the segments
    # Dependency: EncodeOverlay for all segments and extra videos
    MergeVideo = 0x81

class ITaskDefinition:
    
    def update_hash(self, do_update) -> bool:
        """Test input and output cache hit"""
        return hash.test_files(
            paths.hash_txt(self._name()),
            self._hash_files(),
            do_update
        )

    def execute(self):
        """Start subprocess to execute the task, and return the process"""
        return subproc.start_subprocess(
            self._exe_args(),
            paths.log_base(self._name())
        )

    def _name(self) -> str:
        """Get name of this task used for hash and logging"""
        raise Exception("No Impl")

    def _hash_files(self) -> list[str]:
        """Get list of dependency files to hash"""
        raise Exception("No Impl")

    def _exe_args(self) -> list[str]:
        """Get task args"""
        raise Exception("No Impl")

    def get_dependencies(self):
        """return dependencies (type, seg)"""
        raise Exception("No Impl")

    def is_gpu(self):
        """Return if the task should be limited with GPU concurrency limit"""
        return False
    
    def get_description(self):
        """Get description"""
        raise Exception("No Impl")

    def get_color(self):
        """Get color code"""
        return ""

    def prepare(self):
        """Run setup, like creating build directories. This is executed synchronously on the main process"""
        pass

class Task:
    def __init__(self, task_def: ITaskDefinition):
        self.completed = False
        self.failed = False
        self.task_def = task_def
        self.dependencies = None
    def is_completed(self):
        return self.completed
    def is_failed(self):
        return self.failed
    def is_self_up_to_date(self):
        return self.task_def.update_hash(False)
    def update_hash(self):
        return self.task_def.update_hash(True)
    def get_dependencies(self):
        if self.dependencies is None:
            self.dependencies = self.task_def.get_dependencies()
        return self.dependencies
    def mark_complete(self, succeeded):
        self.completed = True
        self.failed = not succeeded
    def is_gpu(self):
        return self.task_def.is_gpu()
    def prepare(self):
        return self.task_def.prepare()
    def execute(self):
        return self.task_def.execute()
    def get_description(self) -> str:
        return self.task_def.get_description()
    def get_color(self) -> str:
        return self.task_def.get_color()


