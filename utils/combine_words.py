import argparse
import os
import sys

# Define ANSI color codes
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'

def combine_words(target_name, wordlist_file='words.txt', output_file='tmp/words.tmp'):
    """
    Combines a target name with words from a wordlist, and saves the result to a file.
    It also includes the target name alone.
    """
    if not os.path.exists('tmp'):
        os.makedirs('tmp')
    
    try:
        with open(wordlist_file, 'r') as infile, open(output_file, 'w') as outfile:
            # Write the target name alone first
            outfile.write(target_name + '\n')
            
            # Then combine the target name with each word from the wordlist
            for line in infile:
                word = line.strip()
                if word:
                    combined_word = f"{target_name}-{word}"
                    outfile.write(combined_word + '\n')
                    
        print(f"{Colors.GREEN}[*] Combined words and target name saved to '{output_file}'{Colors.ENDC}")
        return True
    except FileNotFoundError:
        print(f"{Colors.RED}[!] Error: '{wordlist_file}' not found.{Colors.ENDC}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Combine a target name with a wordlist.")
    parser.add_argument('-t', '--target', required=True, help="The target name to combine with the wordlist.")
    
    args = parser.parse_args()
    if not combine_words(args.target):
        sys.exit(1)

if __name__ == "__main__":
    main()
