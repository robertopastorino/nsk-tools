#!/usr/bin/env python3
"""
Netskope URL Sanitizer

This script processes a text file containing URLs and sanitizes them according to 
Netskope URL validation rules.

Usage: python netskope_url_sanitizer.py input_file.txt [output_file.txt]
"""

import sys
import re
import urllib.parse
from typing import List, Set, Optional
import argparse


class NetskopeURLSanitizer:
    def __init__(self):
        # Valid characters for hostname (letters, digits, dashes)
        self.hostname_pattern = re.compile(r'^[a-zA-Z0-9\-\.]+$')
        # Pattern for valid wildcard (*.domain.com)
        self.wildcard_pattern = re.compile(r'^\*\.[a-zA-Z0-9\-\.]+$')
        # Comment patterns
        self.comment_pattern = re.compile(r'^[#;]')
        
    def is_valid_hostname(self, hostname: str) -> bool:
        """Validate hostname according to Netskope rules."""
        if not hostname:
            return False
            
        # Check for user:password format
        if '@' in hostname:
            return False
            
        # Check for percent encoding in hostname (not allowed)
        if '%' in hostname:
            return False
            
        # Split by dots to check each part
        parts = hostname.split('.')
        for part in parts:
            if not part:  # Empty part
                return False
            if part.startswith('-') or part.endswith('-'):  # Cannot start/end with dash
                return False
            if not re.match(r'^[a-zA-Z0-9\-]+$', part):  # Only letters, digits, dashes
                return False
                
        return True
    
    def is_valid_wildcard(self, url: str) -> bool:
        """Check if wildcard format is valid."""
        if not url.startswith('*.'):
            return False
            
        # Must have exactly one asterisk at the beginning
        if url.count('*') != 1:
            return False
            
        # Check the domain part after *.
        domain_part = url[2:]  # Remove *.
        return self.is_valid_hostname(domain_part)
    
    def sanitize_url(self, url: str) -> Optional[str]:
        """Sanitize a single URL according to Netskope rules."""
        url = url.strip()
        
        # Skip empty lines
        if not url:
            return None
            
        # Skip comment lines
        if self.comment_pattern.match(url):
            return None
        
        # Handle wildcard URLs
        if url.startswith('*'):
            if self.is_valid_wildcard(url):
                return url
            else:
                print(f"Invalid wildcard format: {url}")
                return None
        
        # Remove scheme if present (http/https are ignored)
        if url.startswith(('http://', 'https://')):
            parsed = urllib.parse.urlparse(url)
            # Reconstruct without scheme
            url = parsed.netloc
            if parsed.path:
                url += parsed.path
            if parsed.query:
                url += '?' + parsed.query
            if parsed.fragment:
                url += '#' + parsed.fragment
        
        # Check for user:password format
        if '@' in url:
            print(f"User:password format not supported: {url}")
            return None
        
        # Split URL into hostname and path parts
        if '/' in url:
            hostname, path_part = url.split('/', 1)
            path_part = '/' + path_part
        else:
            hostname = url
            path_part = ''
        
        # Validate hostname
        if not self.is_valid_hostname(hostname):
            print(f"Invalid hostname: {hostname}")
            return None
        
        # Check for spaces in the entire URL (should be percent-encoded)
        if ' ' in url:
            print(f"URL contains unencoded spaces: {url}")
            # Try to fix by encoding spaces in path only
            if path_part and ' ' in path_part:
                path_part = path_part.replace(' ', '%20')
                url = hostname + path_part
                print(f"Fixed to: {url}")
            else:
                return None
        
        # Remove trailing slash if it's just the root path
        if url.endswith('/') and url.count('/') == 1:
            url = url.rstrip('/')
        
        return url
    
    def sanitize_file(self, input_file: str, output_file: Optional[str] = None) -> List[str]:
        """Sanitize URLs from a text file."""
        sanitized_urls = []
        seen_urls: Set[str] = set()
        
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except FileNotFoundError:
            print(f"Error: File '{input_file}' not found.")
            return []
        except Exception as e:
            print(f"Error reading file: {e}")
            return []
        
        print(f"Processing {len(lines)} lines from {input_file}...")
        
        for line_num, line in enumerate(lines, 1):
            sanitized = self.sanitize_url(line)
            
            if sanitized and sanitized not in seen_urls:
                sanitized_urls.append(sanitized)
                seen_urls.add(sanitized)
            elif sanitized and sanitized in seen_urls:
                print(f"Duplicate URL removed: {sanitized}")
        
        # Sort URLs for consistency
        sanitized_urls.sort()
        
        # Write to output file if specified
        if output_file:
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write('# Sanitized URLs for Netskope\n')
                    f.write(f'# Total URLs: {len(sanitized_urls)}\n\n')
                    for url in sanitized_urls:
                        f.write(url + '\n')
                print(f"Sanitized URLs written to {output_file}")
            except Exception as e:
                print(f"Error writing to output file: {e}")
        
        return sanitized_urls
    
    def print_summary(self, urls: List[str]):
        """Print summary of sanitized URLs."""
        print(f"\nSummary:")
        print(f"Total valid URLs: {len(urls)}")
        
        # Count wildcards
        wildcards = [url for url in urls if url.startswith('*.')]
        print(f"Wildcard entries: {len(wildcards)}")
        
        # Count by TLD
        tld_counts = {}
        for url in urls:
            if url.startswith('*.'):
                domain = url[2:]
            else:
                domain = url.split('/')[0]  # Get hostname part
            
            if '.' in domain:
                tld = domain.split('.')[-1]
                tld_counts[tld] = tld_counts.get(tld, 0) + 1
        
        print("\nTop TLDs:")
        for tld, count in sorted(tld_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"  .{tld}: {count}")


def main():
    parser = argparse.ArgumentParser(
        description="Sanitize URLs according to Netskope validation rules"
    )
    parser.add_argument("input_file", help="Input text file containing URLs")
    parser.add_argument("output_file", nargs='?', help="Output file for sanitized URLs")
    parser.add_argument("--no-summary", action="store_true", help="Skip summary output")
    
    args = parser.parse_args()
    
    sanitizer = NetskopeURLSanitizer()
    
    # Use default output filename if not provided
    output_file = args.output_file
    if not output_file:
        base_name = args.input_file.rsplit('.', 1)[0]
        output_file = f"{base_name}_sanitized.txt"
    
    sanitized_urls = sanitizer.sanitize_file(args.input_file, output_file)
    
    if not args.no_summary:
        sanitizer.print_summary(sanitized_urls)


if __name__ == "__main__":
    main()
