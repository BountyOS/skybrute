import os
import yaml
import sys

# Define ANSI color codes
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'

def load_cloud_configs(directory='templates'):
    """
    Loads all YAML configuration files from a specified directory.
    Returns a list of cloud configurations.
    """
    configs = []
    if not os.path.exists(directory):
        print(f"{Colors.RED}[!] Error: '{directory}' directory not found.{Colors.ENDC}")
        return configs
        
    for filename in os.listdir(directory):
        if filename.endswith(('.yaml', '.yml')):
            filepath = os.path.join(directory, filename)
            try:
                with open(filepath, 'r') as file:
                    data = yaml.safe_load(file)
                    if data and 'clouds' in data:
                        configs.extend(data['clouds'])
                        print(f"{Colors.GREEN}[*] Loaded cloud config from '{filepath}'{Colors.ENDC}")
            except Exception as e:
                print(f"{Colors.RED}[!] Error loading '{filepath}': {e}{Colors.ENDC}")
                
    return configs

if __name__ == "__main__":
    # Example usage
    loaded_configs = load_cloud_configs()
    if loaded_configs:
        print(f"{Colors.YELLOW}[*] All loaded configurations:{Colors.ENDC}")
        for config in loaded_configs:
            print(f"  - Name: {config.get('name')}, Domain: {config.get('domain')}, Rate Limit: {config.get('rate_limit_rps')} RPS, Timeout: {config.get('timeout')}s")
