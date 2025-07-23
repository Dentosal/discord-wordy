# Autoupdate wrapper. Restarts the script if there are changes in the git repository.

import subprocess
import argparse
import time
import signal

def pull_changes():
    """Returns true if restart is needed."""

    p = subprocess.check_output(["git", "pull", "--ff-only"])
    return b"Already up to date" not in p

def autoupdate(update_interval):
    while True:
        if pull_changes():
            yield True
        time.sleep(update_interval)

parser = argparse.ArgumentParser(
                    prog='autoupdate.py',
                    description='Periodically run git pull and restart script if changes occur.')

parser.add_argument('-i', '--interval', default=60 * 10, type=int)
parser.add_argument('rest', nargs=argparse.REMAINDER)

args = parser.parse_args()
pull_changes()
child = subprocess.Popen(args.rest)
for _ in autoupdate(args.interval):
    print("Restarting...")
    child.send_signal(signal.SIGINT)
    time.sleep(1)  # Give it a moment to handle the signal
    child.terminate()
    child.wait()
    child = subprocess.Popen(args.rest)
    print("Restart done...")
