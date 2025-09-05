import sys
import threading

# Define ANSI color codes
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'

# Thread-safe lock for printing and logging
_lock = threading.Lock()

def print_and_log(message, output_file=None, log_to_file=True):
    """
    Prints a message to the console and optionally saves it to a file.
    This function is thread-safe for file writing and can distinguish
    between console-only and file-and-console output.
    """
    with _lock:
        try:
            print(message)
            if output_file and log_to_file:
                with open(output_file, 'a') as f:
                    # Strip ANSI color codes before writing to file
                    stripped_message = message.replace(Colors.GREEN, '').replace(Colors.YELLOW, '').replace(Colors.RED, '').replace(Colors.ENDC, '')
                    f.write(f"{stripped_message}\n")
        except Exception as e:
            print(f"{Colors.RED}[!] Error writing to file '{output_file}': {e}{Colors.ENDC}", file=sys.stderr)

def log_valid_bucket(url, status_code, output_file):
    """
    Logs a valid bucket URL and its status code to the output file in a specific format.
    This function is thread-safe.
    """
    if output_file:
        with _lock:
            try:
                with open(output_file, 'a') as f:
                    f.write(f"{url} (Status: {status_code})\n")
            except Exception as e:
                print(f"{Colors.RED}[!] Error writing to file '{output_file}': {e}{Colors.ENDC}", file=sys.stderr)

def initialize_output_file(filepath):
    """
    Initializes a new output file by creating it and writing a header.
    Returns the file path instead of a file object.
    """
    try:
        with open(filepath, 'w') as f:
            f.write("Skybrute Scan Results\n")
            f.write("=======================\n")
            f.write(f"Time: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        print(f"{Colors.GREEN}[*] Saving output to '{filepath}'{Colors.ENDC}")
        return filepath
    except Exception as e:
        print(f"{Colors.RED}[!] Error initializing output file '{filepath}': {e}{Colors.ENDC}", file=sys.stderr)
        return None
