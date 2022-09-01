from multiprocessing import Process
import subprocess
import sys
def subproc_main(subprocess_args, log):
    """Entry point for task sub processes"""
    with open(f"{log}.out.txt", "w+", encoding="utf-8") as stdout_file:
        with open(f"{log}.err.txt", "w+", encoding="utf-8") as stderr_file:
            result = subprocess.run(
                subprocess_args,
                stdout=stdout_file,
                stderr=stderr_file
            )
    
    sys.exit(result.returncode)

def start_subprocess(args, log):
    process = Process(target=subproc_main, args=(args, log), daemon=True)
    process.start()
    return process
