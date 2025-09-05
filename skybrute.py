import argparse
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
import fnmatch

# Assuming these are in the 'utils' directory relative to the script
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))

from combine_words import combine_words
from config_manager import load_cloud_configs
from httprequests import threaded_scanner
from output_manager import print_and_log, initialize_output_file, Colors

def scan_target_and_cloud(wordlist, target, config, output_file, verbose, status_code_filter):
    """
    Handles the scan for a single target and a single cloud configuration.
    Designed to be run in a separate thread.
    """
    cloud_name = config['name']
    cloud_domain = config['domain']
    rate_limit_rps = config.get('rate_limit_rps', 10)
    timeout = config.get('timeout', 5)
    excluded_status_codes = config.get('excluded_status_codes', [404])

    # Console-only messages
    print_and_log(f"\n{Colors.YELLOW}[*] Starting scan for target: '{target}' on cloud: '{cloud_name}'{Colors.ENDC}")
    print_and_log(f"{Colors.YELLOW}[*] Brute-forcing {cloud_name} with a rate limit of {rate_limit_rps} RPS...{Colors.ENDC}")

    urls_to_check = [f"https://{word}.{cloud_domain}" for word in wordlist]

    # threaded_scanner handles saving only valid buckets
    found_buckets = threaded_scanner(
        urls_to_check,
        rate_limit_rps,
        timeout,
        excluded_status_codes,
        output_file,
        verbose,
        status_code_filter
    )

    # Console-only summary
    if not found_buckets:
        print_and_log(f"{Colors.YELLOW}[*] No valid buckets found for {cloud_name} for target '{target}'.{Colors.ENDC}")
    else:
        print_and_log(f"{Colors.GREEN}[+] Scan completed for '{target}' on '{cloud_name}'. Found {len(found_buckets)} valid buckets.{Colors.ENDC}")

def main():
    parser = argparse.ArgumentParser(description="Skybrute: A cloud bucket brute-forcer.")
    parser.add_argument('-t', '--target', help="The target name to combine with the wordlist.")
    parser.add_argument('-tl', '--target-list', help="A file containing a list of targets.")
    parser.add_argument('-o', '--output', help="File to save the output of valid buckets.")
    parser.add_argument('-et', '--exclude-template', nargs='+', help="Excludes cloud templates. Supports wildcards (*). Example: 'ibm*', 'aws,ibm*'.")
    parser.add_argument('-se', '--select-template', nargs='+', help="Selects only specified cloud templates. Supports wildcards (*). Example: 'aws', 'ibm*'.")
    parser.add_argument('-v', '--verbose', action='store_true', help="Enable verbose mode to show all checked URLs and their status codes.")
    parser.add_argument('-sc', '--status-code', type=int, help="Only show buckets with this specific status code.")
    parser.add_argument('-pt', '--parallel-threads', type=int, default=5, help="Number of cloud scans to run in parallel. Default is 5.")
    args = parser.parse_args()

    if not args.target and not args.target_list:
        parser.error("You must provide either a single target (-t) or a target list (-tl).")
    if args.target and args.target_list:
        parser.error("You cannot use both a single target (-t) and a target list (-tl) at the same time.")

    output_file = initialize_output_file(args.output) if args.output else None

    # Load targets
    targets = []
    if args.target:
        targets.append(args.target)
    elif args.target_list:
        try:
            with open(args.target_list, 'r') as f:
                targets = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            print_and_log(f"{Colors.RED}[!] Error: Target list file '{args.target_list}' not found. Exiting.{Colors.ENDC}")
            sys.exit(1)

    try:
        print_and_log(f"{Colors.YELLOW}[*] Loading cloud configurations from 'templates/'{Colors.ENDC}")
        cloud_configs = load_cloud_configs()
        if not cloud_configs:
            print_and_log(f"{Colors.RED}[!] No cloud templates found. Exiting.{Colors.ENDC}")
            sys.exit(1)

        # Exclude templates (-et)
        if args.exclude_template:
            patterns = []
            for item in args.exclude_template:
                patterns.extend(item.split(','))
            patterns = [p.strip() for p in patterns if p.strip()]
            if patterns:
                original_count = len(cloud_configs)
                cloud_configs = [
                    c for c in cloud_configs
                    if not any(fnmatch.fnmatch(c['name'], pattern) for pattern in patterns)
                ]
                print_and_log(f"{Colors.YELLOW}[*] Excluding templates matching: {', '.join(patterns)}{Colors.ENDC}")

        # Select only specified templates (-se)
        if args.select_template:
            patterns = []
            for item in args.select_template:
                patterns.extend(item.split(','))
            patterns = [p.strip() for p in patterns if p.strip()]
            if patterns:
                cloud_configs = [
                    c for c in cloud_configs
                    if any(fnmatch.fnmatch(c['name'], pattern) for pattern in patterns)
                ]
                print_and_log(f"{Colors.YELLOW}[*] Selecting only templates matching: {', '.join(patterns)}{Colors.ENDC}")

        # Process each target
        for target in targets:
            print_and_log(f"\n{Colors.YELLOW}===================================================={Colors.ENDC}")
            print_and_log(f"{Colors.YELLOW}[*] Starting all jobs for target: '{target}'{Colors.ENDC}")
            print_and_log(f"{Colors.YELLOW}===================================================={Colors.ENDC}")

            if not combine_words(target):
                print_and_log(f"{Colors.RED}[!] Word combination failed for target '{target}'. Skipping.{Colors.ENDC}")
                continue

            try:
                with open('tmp/words.tmp', 'r') as f:
                    wordlist = [line.strip() for line in f if line.strip()]
            except FileNotFoundError:
                print_and_log(f"{Colors.RED}[!] Error: 'tmp/words.tmp' not found. Skipping target '{target}'.{Colors.ENDC}")
                continue

            target_jobs = [(target, c) for c in cloud_configs]
            if not target_jobs:
                print_and_log(f"{Colors.RED}[!] No valid scan jobs for '{target}' after filtering. Skipping.{Colors.ENDC}")
                continue

            print_and_log(f"{Colors.YELLOW}[*] Starting parallel scan for '{target}' with {args.parallel_threads} threads for {len(target_jobs)} jobs...{Colors.ENDC}")

            # Run parallel scans for this target
            with ThreadPoolExecutor(max_workers=args.parallel_threads) as executor:
                future_to_job = {
                    executor.submit(scan_target_and_cloud, wordlist, t, c, output_file, args.verbose, args.status_code): (t, c)
                    for t, c in target_jobs
                }
                for future in as_completed(future_to_job):
                    future.result()  # wait for all to finish

            print_and_log(f"{Colors.GREEN}[*] All jobs for '{target}' completed.{Colors.ENDC}")

        print_and_log(f"\n{Colors.GREEN}[*] All scans completed.{Colors.ENDC}")

    finally:
        pass  # Cleanup if needed

if __name__ == "__main__":
    main()
