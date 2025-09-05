import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import sys
from output_manager import print_and_log, Colors

def check_url(url, timeout=5):
    """
    Submits an HTTP HEAD request to a given URL.
    Returns the status code or 0 on connection error.
    """
    try:
        response = requests.head(url, timeout=timeout)
        return response.status_code
    except requests.exceptions.RequestException:
        return 0

def threaded_scanner(urls, rate_limit_rps, timeout, excluded_status_codes, output_file=None, verbose=False, status_code_filter=None):
    """
    Submits concurrent requests with rate-limiting and filters results based on excluded status codes.
    Returns a dictionary of valid buckets found.
    """
    from output_manager import log_valid_bucket  # import here to avoid circular imports
    valid_buckets = {}
    
    with ThreadPoolExecutor(max_workers=rate_limit_rps) as executor:
        future_to_url = {executor.submit(check_url, url, timeout): url for url in urls}
        
        start_time = time.time()
        requests_sent_this_second = 0
        
        for future in as_completed(future_to_url):
            url = future_to_url[future]
            
            requests_sent_this_second += 1
            if requests_sent_this_second >= rate_limit_rps:
                elapsed_time = time.time() - start_time
                if elapsed_time < 1.0:
                    time.sleep(1.0 - elapsed_time)
                requests_sent_this_second = 0
                start_time = time.time()
            
            try:
                status_code = future.result()
                
                # Verbose output for all requests (console only)
                if verbose:
                    color = Colors.GREEN if status_code not in excluded_status_codes and status_code != 0 else Colors.RED
                    print_and_log(f"{color}[-] Checking: {url} (Status: {status_code}){Colors.ENDC}", output_file, log_to_file=False)
                
                is_valid = status_code not in excluded_status_codes and status_code != 0
                if status_code_filter is not None:
                    is_valid = is_valid and status_code == status_code_filter
                
                if is_valid:
                    valid_buckets[url] = status_code
                    if output_file:
                        log_valid_bucket(url, status_code, output_file)  # ✅ save only valid buckets
                
            except Exception as e:
                # Errors can remain console-only
                print_and_log(f"{Colors.RED}[!] Error for {url}: {e}{Colors.ENDC}", output_file, log_to_file=False)
                
    return valid_buckets
