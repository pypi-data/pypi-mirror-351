#!/usr/bin/env python3
import hashlib
import os
import json
import time
from datetime import datetime

LOG_FILE = "ids.log"

def log_event(entry):
    with open(LOG_FILE, "a") as f:
        f.write(f"{datetime.now()} - {entry}\n")
    trim_log()




def load_monitor_paths():
    path_file = "monitor_paths.txt"
    if not os.path.exists(path_file):
        print(f"[!] Missing {path_file}. Please create it with paths to monitor.")
        return []
    with open(path_file) as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("#")]

MONITOR_PATHS = load_monitor_paths()

HASH_DB = "hashes.json"


def load_ignore_files():
    ignore_file = "ignore_files.txt"
    if not os.path.exists(ignore_file):
        return []
    with open(ignore_file) as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("#")]

IGNORE_FILES = load_ignore_files()

def hash_file(path):
    try:
        with open(path, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()
    except Exception:
        return None


def build_hash_db():
    file_hashes = {}
    for root_path in MONITOR_PATHS:
        for dirpath, _, filenames in os.walk(root_path):
            for f in filenames:
                full_path = os.path.join(dirpath, f)
                if full_path in IGNORE_FILES:
                    continue
                h = hash_file(full_path)
                if h:
                    file_hashes[full_path] = h
    with open(HASH_DB, "w") as f:
        json.dump(file_hashes, f, indent=2)


def check_integrity():
    try:
        with open(HASH_DB) as f:
            old_hashes = json.load(f)
    except FileNotFoundError:
        print("No baseline found. Run with --init first.")
        return

    current_hashes = {}
    modified = []
    added = []
    deleted = []

    for root_path in MONITOR_PATHS:
        for dirpath, _, filenames in os.walk(root_path):
            for f in filenames:
                full_path = os.path.join(dirpath, f)
                if full_path in IGNORE_FILES:
                    continue
                h = hash_file(full_path)
                if h:
                    current_hashes[full_path] = h
                    if full_path in old_hashes:
                        if old_hashes[full_path] != h:
                            modified.append(full_path)
                    else:
                        added.append(full_path)

    for old_file in old_hashes:
        if old_file in IGNORE_FILES:
            continue
        if old_file not in current_hashes:
            deleted.append(old_file)

    if modified or added or deleted:
        def color(text, code):
            return f"\033[{code}m{text}\033[0m"

        print(color("[!] File changes detected:", "91"))
        log_event("File changes detected:")

        if modified:
            print("  [+] Modified:")
            for f in modified:
                print(f"    - {f}")
                log_event(f"MODIFIED: {f}")

        if added:
            print("  [+] Added:")
            for f in added:
                print(f"    - {f}")
                log_event(f"ADDED: {f}")

        if deleted:
            print("  [+] Deleted:")
            for f in deleted:
                print(f"    - {f}")
                log_event(f"DELETED: {f}")
    else:
        print("[+] No file changes detected.")
        log_event("No file changes detected.")


    with open(HASH_DB, "w") as f:
        json.dump(current_hashes, f, indent=2)



def watch_loop(interval=60):
    try:
        while True:
            check_integrity()
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\n[+] Monitor mode stopped.")



def trim_log(file_path="ids.log"):
    max_lines = 10000
    try:
        with open("config.json") as f:
            max_lines = json.load(f).get("log_retention_lines", max_lines)

    except Exception:
        pass

    if not os.path.exists(file_path):
        return
    with open(file_path, "r") as f:
        lines = f.readlines()
    if len(lines) > max_lines:
        with open(file_path, "w") as f:
            f.writelines(lines[-max_lines:])



if __name__ == "__main__":
    import sys
    if "--init" in sys.argv:
        build_hash_db()
        print("[+] Baseline hash database created.")
    elif "--monitor" in sys.argv:
        try:
            idx = sys.argv.index("--interval")
            interval = int(sys.argv[idx + 1])
        except (ValueError, IndexError):
            interval = 60
        watch_loop(interval)
    else:
        check_integrity()