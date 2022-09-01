
from proc import ProcessHolder
from taskdefs import ITaskDefinition, TaskType

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
    def cleanup(self):
        return self.task_def.cleanup()
    def get_description(self):
        return self.task_def.get_description()

class TaskManager:
    def __init__(self, gpu_limit):
        self.process_holder = ProcessHolder()
        self.process_holder.start(None)
        self.segment_names = None
        self.task_matrix = dict()
        self.task_queue = []
        self.gpu_limit = gpu_limit
        self.gpu_usage = 0
        self.total = 0
        self.completed = 0
        self.skipped = 0
        self.failed = 0
        self.last_up_line = 1

    def initialize(self, segment_names):
        self.segment_names = segment_names
        for type in TaskType:
            self.task_matrix[type] = [None] * len(segment_names)

    def schedule_task(self, type, segment):
        """Add the task and all its dependencies, return True if the task is scheduled or False if the task is already up-to-date"""
        # is the task already scheduled?
        if self.task_matrix[type][segment] is not None:
            return not self.task_matrix[type][segment].is_completed()
        # Create the task object and put it in the queue temporarily
        task = self.task_factory(type, segment)
        self.task_matrix[type][segment] = task
        up_to_date = True
        # Get its dependencies
        dependencies = task.get_dependencies()
        for (dep_type, dep_segment) in dependencies:
            # Try scheduling dependency
            dep_scheduled = self.schedule_task(dep_type, dep_segment)
            # If one of the dependencies is not up to date, then this task is not
            if dep_scheduled:
                up_to_date = False
        
        # Finally test if self is up to date
        if up_to_date:
            up_to_date = task.is_self_up_to_date()
        
        if up_to_date:
            self.skipped+=1
            task.mark_complete(True)
            return False
        
        return True

    def queue_scheduled_tasks(self):
        """Queue up scheduled tasks in an optimized order"""
        for task_type in (
            TaskType.GenerateMergeVideo, 
            TaskType.GenerateWebPage, 
            TaskType.GenerateTimeTable
        ):
            for task in self.task_matrix[task_type]:
                if task is not None:
                    self.add_to_queue(task)
                    break

        for segment in range(len(self.segment_names)-1, -1, -1):
            for task_type in (
                TaskType.EncodeOverlay,
                TaskType.GenerateSplit_0,
                TaskType.GenerateSplit_1,
                TaskType.GenerateSplit_2,
                TaskType.GenerateSplit_3,
                TaskType.GenerateSplit_4,
                TaskType.GenerateSplit_5,
                TaskType.GenerateSplit_6,
                TaskType.GenerateSplit_7,
                TaskType.GenerateSplit_8,
                TaskType.GenerateSplit_9,
                TaskType.GenerateSplit_a,
                TaskType.GenerateSplit_b,
                TaskType.GenerateSplit_c,
                TaskType.GenerateSplit_d,
                TaskType.GenerateSplit_e,
                TaskType.GenerateTime,
                TaskType.Download,
            ):
                self.add_to_queue(self.task_matrix[task_type][segment])            

    def add_to_queue(self, task: Task):
        if task is None:
            return
        self.total+=1
        if task.is_completed():
            self.completed+=1
            return
        self.task_queue.append(task)
        
    def executable_task(self) -> Task | None:
        """Get one task that can be executed right now, or None if nothing is found"""
        polled = []
        return_task = None
        while self.task_queue:
            task = self.task_queue.pop()
            # Purge completed tasks in queue
            if task.is_completed():
                continue
            # Determine if task can be executed
            if task.is_gpu() and self.gpu_usage >= self.gpu_limit:
                polled.append(task)
                break

            can_execute = True
            dependencies = task.get_dependencies()
            for (dep_type, dep_segment) in dependencies:
                dep_task = self.task_matrix[dep_type][dep_segment]
                if not dep_task.is_completed():
                    can_execute = False
                    # Not ready yet, add the task back later
                    polled.append(task)
                    break
                if dep_task.is_failed():
                    can_execute = False
                    # Fail this task
                    task.mark_complete(False)
                    self.failed+=1
                    # Don't add failed task back
                    break
            if can_execute:
                return_task = task
                break
        self.task_queue.extend(polled)
        if task.is_gpu():
            self.gpu_usage+=1
        return return_task

    def on_finish_task(self, task: Task):
        if task.is_gpu():
            self.gpu_usage-=1
        self.completed+=1
        task.update_hash()

    def is_queue_empty(self):
        return not self.task_queue
    
    def print_status(self, process_holders: list[ProcessHolder]):
        print(f"\033[{self.last_up_line}A")
        line = 2
        if self.total == 0:
            progress = "Calculating tasks"
        else:
            progress = f"{self.completed} Completed ({self.skipped} Skipped). {self.total} Total. {self.failed} Failed.   "
        
        elapsed = self.process_holder.elapsed_time()
        
        print(f"[{elapsed}] {progress}")
        for process_holder in process_holders:
            if process_holder.is_active():
                elapsed = process_holder.elapsed_time()
                description = process_holder.get_task().get_description()
                print(f"   [{elapsed}] {description}")
                line+=1
        extra = 1
        if line < self.last_up_line:
            for _ in range(self.last_up_line - line):
                print(f"                                                                                             ")
                extra += 1
        print(f"\033[{extra}A")
        self.last_up_line = line

    def print_report(self):
        fails = []
        for task_type_tasks in self.task_matrix:
            for task in task_type_tasks:
                if task is not None and task.is_failed():
                    fails.append(task.get_description())
        if not fails:
            print("BUILD SUCCEEDED")
        else:
            for f in fails:
                print(f"Task Failed: {f}")
            print()
            print("BUILD FAILED") 

    def task_factory(type, segment) -> Task:
        pass
