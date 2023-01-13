import subprocess
import psutil
from keymappings.debug import with_decoration, debug_arguments, debug_print


@with_decoration
@debug_arguments
def run(shell_process: str) -> None:
    subprocess.call(shell_process, shell=True)

@with_decoration
@debug_arguments
def run_if_process_does_not_exist(shell_command: str, process: str) -> None:
    """
    Example:
        run_if_process_does_not_exist('Chrome', 'chrome.exe')
        run_if_process_does_not_exist('Chrome') # Will search for `Chrome.exe` and `chrome.exe`.

    :param shell_command: what to run.
    :param process: for which process to check.
    """
    running_processes = (p.name() for p in psutil.process_iter())

    if any(process_to_be_created in running_processes for process_to_be_created in
           [process, shell_command + '.exe', shell_command.upper() + '.exe']):
        debug_print(f'{shell_command} is already running')
        return

    run(shell_command)

