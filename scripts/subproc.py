from multiprocessing import Process
import subprocess
import sys
def subproc_main(args):
    """Entry point for task sub processes"""
    subprocess_args, log = args
    with open(f"{log}.out.txt", "w+", encoding="utf-8") as stdout_file:
        with open(f"{log}.err.txt", "w+", encoding="utf-8") as stdout_file:
            result = subprocess.run(
                subprocess_args,
                stdout=stdout_file,
                stderr=stdout_file
            )
    
    sys.exit(result.returncode)

def start_subprocess(args, log):
    process = Process(target=subproc_main, args=(args, log), daemon=True)
    process.start()
    return process
