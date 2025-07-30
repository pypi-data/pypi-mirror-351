"""
Core functionality for terminal recording and playback.

This module provides the main functionality for recording terminal sessions
and playing them back with original timing.
"""

import pty
import os
import subprocess
import sys
import threading
import select
import time
import struct
import fcntl
import termios
import tty
from typing import Tuple


def set_pty_size(fd: int, rows: int, cols: int) -> bool:
    """
    Set the size of a pseudoterminal.

    Args:
        fd: File descriptor of the PTY
        rows: Number of rows
        cols: Number of columns

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        winsize = struct.pack('HHHH', rows, cols, 0, 0)
        fcntl.ioctl(fd, termios.TIOCSWINSZ, winsize)
        return True
    except (OSError, IOError):
        return False


def get_terminal_size() -> Tuple[int, int]:
    """
    Get the current terminal size.

    Returns:
        Tuple[int, int]: A tuple of (rows, columns)
    """
    try:
        winsize = fcntl.ioctl(sys.stdin.fileno(),
                              termios.TIOCGWINSZ, b'\x00' * 8)
        rows, cols, xpixel, ypixel = struct.unpack('HHHH', winsize)
        return rows, cols
    except (OSError, IOError):
        return 24, 80


def record(command: str) -> None:
    """
    Record a terminal session.

    Args:
        command: The command to execute and record
    """
    t = time.time_ns()
    with open("record.trc", 'wb', buffering=0) as file:
        master, slave = pty.openpty()
        rows, cols = get_terminal_size()
        set_pty_size(master, rows, cols)
        set_pty_size(slave, rows, cols)
        process = subprocess.Popen(
            command,
            stdin=slave,
            stdout=slave,
            stderr=slave,
            shell=True
        )
        os.close(slave)

        def stdin_to_master() -> None:
            """Forward terminal input to master."""
            try:
                while process.poll() is None:
                    if select.select([sys.stdin], [], [], 0.1)[0]:
                        data = os.read(sys.stdin.fileno(), 1024)
                        if data:
                            os.write(master, data)
            except (OSError, IOError):
                pass

        def master_to_stdout() -> None:
            """Forward master output to terminal and record file."""
            try:
                while process.poll() is None:
                    if select.select([master], [], [], 0.1)[0]:
                        data = os.read(master, 1024)
                        if data:
                            os.write(sys.stdout.fileno(), data)
                            sys.stdout.flush()
                            t_now = (time.time_ns()-t).to_bytes(32, 'big')
                            t_x = len(data).to_bytes(4, 'big')
                            file.write(t_now+t_x+data)
            except (OSError, IOError):
                pass

        old_settings = termios.tcgetattr(sys.stdin)
        try:
            tty.setraw(sys.stdin.fileno())

            input_thread = threading.Thread(
                target=stdin_to_master, daemon=True)
            output_thread = threading.Thread(
                target=master_to_stdout, daemon=True)

            input_thread.start()
            output_thread.start()

            process.wait()

        except KeyboardInterrupt:
            print("\nProcess interrupted")
        finally:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
            os.close(master)
            process.terminate()


def play() -> None:
    """
    Play back a recorded terminal session from record.trc file.
    """
    with open("record.trc", 'rb') as file:
        r = b""
        t_now = 0
        t_x = 0
        mode = 0
        st = time.time_ns()
        while True:
            r = r + file.read(1024)
            if not r:
                break
            while True:
                if mode == 0:
                    if len(r) < 36:
                        break
                    t_now = int.from_bytes(r[:32], 'big')
                    r = r[32:]
                    t_x = int.from_bytes(r[:4], 'big')
                    r = r[4:]
                    mode = 1
                if mode == 1:
                    if len(r) < t_x:
                        break
                    while time.time_ns() - st < t_now:
                        time.sleep(0.001)
                    sys.stdout.write(r[:t_x].decode('utf-8', errors='ignore'))
                    sys.stdout.flush()
                    r = r[t_x:]
                    mode = 0


def main() -> None:
    """
    Main entry point for the command-line interface.
    """
    if len(sys.argv) < 2:
        print("Usage: termrecord <command> [args...]")
        print("Commands:")
        print("  record <command>  Record a terminal session")
        print("  play             Play back a recorded session")
        sys.exit(1)

    cmd = sys.argv[1]
    if cmd == 'record':
        if len(sys.argv) < 3:
            print("Error: No command specified for recording")
            sys.exit(1)
        run_cmd = ' '.join(sys.argv[2:])
        record(run_cmd)
    elif cmd == 'play':
        play()
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)


if __name__ == '__main__':
    main()
