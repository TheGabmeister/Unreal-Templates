"""Drive this project's Unreal Editor from the command line through Unreal's Python remote execution.

The project is the folder above this script, and its editor is found by project path, so several
editors (each on its own project) can run at once. Windows only.

  python Tools/ue.py nodes                 List running editors that accept remote execution
  python Tools/ue.py exec "print(1)"       Run Python in this project's running editor
  python Tools/ue.py exec -f script.py     Run a file (or pipe code on stdin with no argument)
  python Tools/ue.py start [--headless]    Start this project's editor and wait until it accepts commands
  python Tools/ue.py stop [--discard]      Quit this project's headless editor
  python Tools/ue.py run "print(1)"        One-off headless run with no editor left running (also -f / stdin)
"""

import argparse
import json
import msvcrt
import os
import re
import socket
import subprocess
import sys
import tempfile
import time
from contextlib import contextmanager
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
UPROJECT = next(PROJECT_DIR.glob('*.uproject'))
LOCK_FILE = PROJECT_DIR / 'Saved' / 'ue.lock'
RUN_LOG = PROJECT_DIR / 'Saved' / 'Logs' / 'ue_run.log'
LOCK_TIMEOUT = 600


def find_engine_dir():
    if os.environ.get('UE_ENGINE_DIR'):
        return Path(os.environ['UE_ENGINE_DIR'])
    version = json.loads(UPROJECT.read_text(encoding='utf-8'))['EngineAssociation']
    launcher = Path(os.environ.get('PROGRAMDATA', 'C:/ProgramData')) / 'Epic/UnrealEngineLauncher/LauncherInstalled.dat'
    if launcher.exists():
        for item in json.loads(launcher.read_text(encoding='utf-8'))['InstallationList']:
            if item['AppName'] == f'UE_{version}':
                return Path(item['InstallLocation'])
    sys.exit(f'Unreal Engine {version} not found. Set UE_ENGINE_DIR to the engine install folder.')


ENGINE_DIR = find_engine_dir()
EDITOR = ENGINE_DIR / 'Engine/Binaries/Win64/UnrealEditor.exe'
EDITOR_CMD = ENGINE_DIR / 'Engine/Binaries/Win64/UnrealEditor-Cmd.exe'
sys.path.insert(0, str(ENGINE_DIR / 'Engine/Plugins/Experimental/PythonScriptPlugin/Content/Python'))
import remote_execution as rx  # noqa: E402


def _receive_message(self, expected_type):
    # The engine's version stops at the first short read, which can cut off large results. Read until the JSON is complete.
    data = b''
    while part := self._command_channel_socket.recv(65536):
        data += part
        try:
            json.loads(data)
            break
        except ValueError:
            continue
    message = rx._RemoteExecutionMessage(None, None)
    if data and message.from_json_bytes(data) and message.passes_receive_filter(self._node_id) and message.type_ == expected_type:
        return message
    raise RuntimeError('Remote party failed to send a valid response!')


rx._RemoteExecutionCommandConnection._receive_message = _receive_message


def same_path(a, b):
    return os.path.normcase(os.path.normpath(a)) == os.path.normcase(os.path.normpath(b))


def free_port():
    with socket.socket() as s:
        s.bind(('127.0.0.1', 0))
        return s.getsockname()[1]


@contextmanager
def project_lock():
    # The editor keeps one command connection at a time, so calls for this project take turns.
    LOCK_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOCK_FILE, 'a+b') as f:
        deadline = time.time() + LOCK_TIMEOUT
        while True:
            try:
                f.seek(0)
                msvcrt.locking(f.fileno(), msvcrt.LK_NBLCK, 1)
                break
            except OSError:
                if time.time() > deadline:
                    sys.exit('Timed out waiting for another ue.py call on this project to finish.')
                time.sleep(0.2)
        try:
            yield
        finally:
            f.seek(0)
            msvcrt.locking(f.fileno(), msvcrt.LK_UNLCK, 1)


@contextmanager
def session():
    config = rx.RemoteExecutionConfig()
    # Each call listens on its own port; the engine's fixed default would let parallel calls receive each other's replies.
    config.command_endpoint = ('127.0.0.1', free_port())
    remote = rx.RemoteExecution(config)
    remote.start()
    try:
        yield remote
    finally:
        remote.stop()


def find_project_node(remote, wait=3.0):
    deadline = time.time() + wait
    while True:
        for node in remote.remote_nodes:
            if same_path(node.get('project_root', ''), PROJECT_DIR):
                return node
        if time.time() >= deadline:
            return None
        time.sleep(0.1)


def require_project_node(remote):
    node = find_project_node(remote)
    if not node:
        sys.exit(f'No editor for {UPROJECT.stem} is accepting remote execution. '
                 'Start one with "ue.py start --headless", or use "ue.py run" for a one-off change.')
    return node


@contextmanager
def script_file(args):
    # Always hand Unreal a file: it treats literal code that contains ".py " as a file path.
    if args.file:
        yield Path(args.file).resolve()
        return
    code = sys.stdin.read() if args.code in (None, '-') else args.code
    with tempfile.NamedTemporaryFile('w', suffix='.py', prefix='ue_', delete=False, encoding='utf-8') as f:
        f.write(code)
    try:
        yield Path(f.name)
    finally:
        os.remove(f.name)


def run_on_node(remote, node, path):
    remote.open_command_connection(node['node_id'])
    try:
        return remote.run_command(f'"{path}"', exec_mode=rx.MODE_EXEC_FILE)
    finally:
        remote.close_command_connection()


def query(remote, node, code):
    """Run code that prints one JSON line and return the parsed value."""
    with tempfile.NamedTemporaryFile('w', suffix='.py', prefix='ue_', delete=False, encoding='utf-8') as f:
        f.write(code)
    try:
        result = run_on_node(remote, node, f.name)
    finally:
        os.remove(f.name)
    if not result['success']:
        sys.exit(result['result'])
    return json.loads(result['output'][-1]['output'])


def print_result(result):
    for entry in result['output']:
        text = entry['output'].rstrip('\n')
        print(text if entry['type'] == 'Info' else f"{entry['type']}: {text}", flush=True)
    if not result['success']:
        if not any(entry['type'] == 'Error' for entry in result['output']):  # the traceback is usually already in the output
            print(result['result'], file=sys.stderr)
        return 1
    return 0


def cmd_nodes(args):
    with session() as remote:
        time.sleep(2)  # editors answer the once-per-second discovery ping
        nodes = remote.remote_nodes
    for node in nodes:
        info = {key: node.get(key) for key in ('project_name', 'project_root', 'engine_version', 'node_id')}
        info['this_project'] = same_path(node.get('project_root', ''), PROJECT_DIR)
        print(json.dumps(info))
    if not nodes:
        print('No editors with remote execution found.')


def cmd_exec(args):
    with project_lock(), session() as remote, script_file(args) as path:
        return print_result(run_on_node(remote, require_project_node(remote), path))


def cmd_start(args):
    with project_lock(), session() as remote:
        node = find_project_node(remote)
        if node:
            print(f'{UPROJECT.stem} editor is already running.')
            return 0
        if args.headless:
            command = [str(EDITOR_CMD), str(UPROJECT), '-nullrhi', '-unattended', '-nosplash']
        else:
            command = [str(EDITOR), str(UPROJECT)]
        flags = subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
        launch = dict(stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, close_fds=True)
        try:
            # Break away from the caller's job object so the editor outlives this command.
            process = subprocess.Popen(command, creationflags=flags | subprocess.CREATE_BREAKAWAY_FROM_JOB, **launch)
        except OSError:
            process = subprocess.Popen(command, creationflags=flags, **launch)
        started = time.time()
        while not find_project_node(remote, wait=1.0):
            if process.poll() is not None:
                sys.exit(f'Editor exited with code {process.returncode}. See Saved/Logs/{UPROJECT.stem}.log.')
            if time.time() - started > args.timeout:
                sys.exit(f'Editor did not accept remote execution within {args.timeout}s. Is remote execution enabled in Config/DefaultEngine.ini?')
        mode = 'headless' if args.headless else 'windowed'
        print(f'{UPROJECT.stem} editor started ({mode}, pid {process.pid}) in {time.time() - started:.0f}s.')
        return 0


STATE_CODE = '''
import json, unreal
utils = unreal.EditorLoadingAndSavingUtils
packages = list(utils.get_dirty_content_packages()) + list(utils.get_dirty_map_packages())
print(json.dumps({
    'headless': '-nullrhi' in unreal.SystemLibrary.get_command_line().lower(),
    'dirty': [p.get_name() for p in packages if not p.get_name().startswith('/Temp/')],
}))
'''


def cmd_stop(args):
    with project_lock(), session() as remote:
        node = find_project_node(remote)
        if not node:
            print(f'{UPROJECT.stem} editor is not running.')
            return 0
        state = query(remote, node, STATE_CODE)
        if not state['headless']:
            sys.exit('This is a windowed editor. Close it in its own window so nothing unsaved is lost.')
        if state['dirty'] and not args.discard:
            sys.exit('Unsaved packages: ' + ', '.join(state['dirty']) + '. Save them first, or pass --discard.')
        query(remote, node, 'import unreal; unreal.SystemLibrary.quit_editor(); print("null")')
        deadline = time.time() + 120
        while any(n['node_id'] == node['node_id'] for n in remote.remote_nodes):
            if time.time() > deadline:
                sys.exit('Editor did not exit within 120s.')
            time.sleep(0.5)
        print(f'{UPROJECT.stem} headless editor stopped.')
        return 0


LOG_LINE = re.compile(r'^\[[^\]]*\]\[[^\]]*\](\w+): (.*)$')


def script_output(log_text):
    """Python output plus warnings and errors from the script's part of a commandlet log."""
    lines = log_text.splitlines()
    start = next((i for i, line in enumerate(lines) if 'Running Python script:' in line), None)
    if start is None:
        return lines[-20:]  # failed before the script ran
    output, keep = [], False
    for line in lines[start + 1:]:
        if 'LogPythonScriptCommandlet:' in line:
            break
        match = LOG_LINE.match(line)
        if match:
            category, message = match.groups()
            keep = category == 'LogPython' or message.startswith(('Error:', 'Warning:'))
            if keep:
                output.append(message if category == 'LogPython' else f'{category}: {message}')
        elif keep and line:
            output.append(line)
    return output


def cmd_run(args):
    with project_lock(), script_file(args) as path:
        with session() as remote:
            if find_project_node(remote):
                sys.exit(f'{UPROJECT.stem} is open in an editor. Use "ue.py exec" so the two don\'t overwrite each other.')
        command = (f'"{EDITOR_CMD}" "{UPROJECT}" -run=pythonscript -Script="{path}" '
                   f'-unattended -nullrhi -nosplash -nopause -abslog="{RUN_LOG}"')
        subprocess.run(command, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    log_text = RUN_LOG.read_text(encoding='utf-8', errors='replace')
    print('\n'.join(script_output(log_text)), flush=True)
    # The exit code is 1 whenever anything logged an error, so the commandlet's own message decides success.
    if 'Python script executed successfully' not in log_text:
        print(f'Failed. Full log: {RUN_LOG}', file=sys.stderr)
        return 1
    return 0


def main():
    sys.stdout.reconfigure(errors='replace')
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    commands = parser.add_subparsers(dest='command', required=True)
    commands.add_parser('nodes', help='list running editors that accept remote execution').set_defaults(func=cmd_nodes)
    for name, func, help_text in (('exec', cmd_exec, "run Python in this project's running editor"),
                                  ('run', cmd_run, 'run Python in a one-off headless process')):
        sub = commands.add_parser(name, help=help_text)
        sub.add_argument('code', nargs='?', help='Python code; omit or pass - to read it from stdin')
        sub.add_argument('-f', '--file', help='Python file to run instead of code')
        sub.set_defaults(func=func)
    start = commands.add_parser('start', help="start this project's editor")
    start.add_argument('--headless', action='store_true', help='run without a window or rendering (-nullrhi)')
    start.add_argument('--timeout', type=int, default=600, help='seconds to wait for the editor (default 600)')
    start.set_defaults(func=cmd_start)
    stop = commands.add_parser('stop', help="quit this project's headless editor")
    stop.add_argument('--discard', action='store_true', help='quit even if packages are unsaved')
    stop.set_defaults(func=cmd_stop)
    args = parser.parse_args()
    sys.exit(args.func(args) or 0)


if __name__ == '__main__':
    main()
