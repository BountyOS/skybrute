# Skybrute

**Skybrute** is a multi-cloud bucket brute-forcing tool.  
It automates the process of discovering misconfigured or exposed cloud storage buckets across various cloud providers by combining target names with wordlists and cloud templates.

---

## ✨ Features

- 🚀 Brute-force across **multiple cloud providers** simultaneously.  
- 📂 Uses **cloud templates** (`templates/`) for provider-specific configurations.  
- 🎯 Supports **single target** or **list of targets**.  
- ⚡ **Parallel scanning** with configurable thread count.  
- 🎛️ Filtering options:
  - **Exclude** or **select** specific cloud templates (supports wildcards).  
  - Show results only for a **specific status code**.  
- 📜 Detailed console output with colorized logs.  
- 📝 Optional output file to save valid buckets.

---

## ⚙️ Installation

Clone the repository and install the requirements:

```
git clone https://github.com/BountyOS/skybrute.git
cd skybrute
pip3 install -r requirements.txt --break-system-packages
```

Usage:
```
usage: skybrute.py [-h] [-t TARGET] [-tl TARGET_LIST] [-o OUTPUT] [-et EXCLUDE_TEMPLATE [EXCLUDE_TEMPLATE ...]]
                   [-se SELECT_TEMPLATE [SELECT_TEMPLATE ...]] [-v] [-sc STATUS_CODE] [-pt PARALLEL_THREADS]

Skybrute: A cloud bucket brute-forcer.

options:
  -h, --help            show this help message and exit
  -t TARGET, --target TARGET
                        The target name to combine with the wordlist.
  -tl TARGET_LIST, --target-list TARGET_LIST
                        A file containing a list of targets.
  -o OUTPUT, --output OUTPUT
                        File to save the output of valid buckets.
  -et EXCLUDE_TEMPLATE [EXCLUDE_TEMPLATE ...], --exclude-template EXCLUDE_TEMPLATE [EXCLUDE_TEMPLATE ...]
                        Excludes cloud templates. Supports wildcards (*). Example: 'ibm*', 'aws,ibm*'.
  -se SELECT_TEMPLATE [SELECT_TEMPLATE ...], --select-template SELECT_TEMPLATE [SELECT_TEMPLATE ...]
                        Selects only specified cloud templates. Supports wildcards (*). Example: 'aws', 'ibm*'.
  -v, --verbose         Enable verbose mode to show all checked URLs and their status codes.
  -sc STATUS_CODE, --status-code STATUS_CODE
                        Only show buckets with this specific status code.
  -pt PARALLEL_THREADS, --parallel-threads PARALLEL_THREADS
                        Number of cloud scans to run in parallel. Default is 5.
```

Sample command:
```
python3 skybrute.py -t slack -o bucks.tmp -pt 5
```
Searching for slack buckets by using all templates, saving the output as bucks.tmp with 5 parallel jobs per cloud template.

## 🏗️ Creating Custom Cloud Templates

Skybrute uses templates stored in the `templates/` directory to define how different clouds should be scanned.
You can write templates in **YAML** format.

---

### ✅ Example Template

```yaml
clouds:
  - name: vultr-ams1
    domain: ams1.vultrobjects.com
    rate_limit_rps: 10
    timeout: 5
    excluded_status_codes:
      - 404
  - name: vultr-ewr1
    domain: ewr1.vultrobjects.com
    rate_limit_rps: 10
    timeout: 5
    excluded_status_codes:
      - 404
  - name: vultr-sjc1
    domain: sjc1.vultrobjects.com
    rate_limit_rps: 10
    timeout: 5
    excluded_status_codes:
      - 404
  - name: vultr-sgp1
    domain: sgp1.vultrobjects.com
    rate_limit_rps: 10
    timeout: 5
    excluded_status_codes:
      - 404
```
#### Parameters explained:
- `name` is the name of the cloud.
- `domain` is the domain that you should fuzz such as `FUZZ.sgp1.vultrobjects.com`
- `timeout` is the timeout of submitted requests to the cloud
- `excluded_status_codes` is the status codes you should ignore to detect the valid buckets

---

## ⚠️ Usage & Responsibility

Skybrute is a security research tool. It can be powerful, but with that comes responsibility:  
- Use it only on systems you **own** or have **explicit permission** to test.  
- The author(s) are **not responsible for any misuse, damages, or legal consequences** caused by this tool.  
- What you do with Skybrute is **entirely your responsibility**.  

If someone chooses to use it for the wrong reasons — that’s on them, not on the project.  

