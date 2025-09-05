# core/directory_bruteforcer.py
import re
import requests
from typing import Optional, List

WORDLIST_PATH = "resources/word.txt"

def load_wordlist() -> List[str]:
    """Loads paths from the wordlist file."""
    try:
        with open(WORDLIST_PATH, "r", encoding="utf-8", errors="ignore") as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"⚠️ Warning: Wordlist file not found at '{WORDLIST_PATH}'. Using a small default list.")
        return ["admin", "login", "test", "api", "dashboard"]

def extract_target(msg: str) -> Optional[str]:
    """
    Extracts a URL or IP address from the user's message.
    It looks for patterns like http(s)://, www., or IP address formats.
    """
    # Regex to find a URL, domain name, or IP address.
    # It prioritizes URLs with schemes (http/https), then www, then domain-like names, then IPs.
    target_pattern = re.compile(
        r"https?://[a-zA-Z0-9.-]+[^\s]*"  # http(s)://...
        r"|[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"  # domain.com, sub.domain.co.uk
        r"|\b(?:\d{1,3}\.){3}\d{1,3}\b"     # 192.168.1.1
    )
    
    match = target_pattern.search(msg)
    if not match:
        return None
    
    target = match.group(0)
    # If the user provided a scheme, respect it. Otherwise, default to http.
    if not re.match(r"https?://", target):
        return f"http://{target}"
    
    return target

def bruteforce_directories(base_url: str) -> List[str]:
    """
    Checks for common directories/paths on a given base URL.
    Returns a list of found (200 OK) URLs.
    """
    common_paths = load_wordlist()
    if not common_paths:
        print("[-] Wordlist is empty. Aborting scan.")
        return []

    found_paths = []
    print(f"[*] Starting directory scan on {base_url}")
    for path in common_paths: # This is line 58
        target_url = f"{base_url.rstrip('/')}/{path}" # This block is now indented
        try:
            # Using a HEAD request is faster as it doesn't download the body
            response = requests.head(target_url, timeout=5, allow_redirects=True)
            if response.status_code == 200:
                print(f"[+] Found: {target_url}")
                found_paths.append(target_url)
        except requests.RequestException:
            # Ignore connection errors, timeouts, etc.
            pass
    return found_paths
