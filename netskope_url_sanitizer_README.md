# Netskope URL Sanitizer

This Python script sanitizes URLs according to Netskope validation rules, processing text files containing arbitrary numbers of URLs.

## Features

- **Rule Compliance**: Implements all Netskope URL validation rules
- **Automatic Sanitization**: Removes schemes, fixes encoding issues, validates hostnames
- **Duplicate Removal**: Automatically removes duplicate entries
- **Error Reporting**: Shows which URLs fail validation and why
- **Wildcard Support**: Validates wildcard domains (*.example.com)
- **Comment Handling**: Ignores comment lines starting with # or ;
- **Summary Statistics**: Provides analysis of processed URLs

## Usage

### Basic Usage
```bash
python netskope_url_sanitizer.py input_file.txt
```
This creates `input_file_sanitized.txt` with cleaned URLs.

### Specify Output File
```bash
python netskope_url_sanitizer.py input_file.txt output_file.txt
```

### Skip Summary
```bash
python netskope_url_sanitizer.py input_file.txt --no-summary
```

## Validation Rules Applied

1. **Hostname Validation**:
   - Only letters, digits, and dashes allowed
   - Cannot start or end with dash
   - No percent-encoding in hostnames (use punycode instead)

2. **Wildcard Validation**:
   - Only one '*' allowed, must be first character
   - Must be followed by '.' (e.g., *.google.com)

3. **URL Sanitization**:
   - Removes http/https schemes (ignored by Netskope)
   - Rejects user:password@host format
   - Encodes spaces in paths as %20
   - Removes trailing slashes from root domains

4. **Content Filtering**:
   - Ignores blank lines
   - Ignores comment lines (starting with # or ;)
   - Removes duplicate URLs

## Input File Format

Your input file can contain:
- One URL per line
- Comment lines starting with # or ;
- Blank lines (ignored)
- URLs with or without schemes
- Wildcard domains

## Example Input
```
# Company domains
*.google.com
www.example.com/
https://third.domain.com
some.domain.tld/

# IP addresses
94.82.173.165/brex
```

## Example Output
```
# Sanitized URLs for Netskope
# Total URLs: 4

*.google.com
94.82.173.165/brex
third.domain.com
some.domain.tld
www.example.com
```

## Error Handling

The script will report and skip invalid URLs:
- URLs with spaces in hostnames
- Invalid wildcard formats
- URLs with user:password authentication
- Malformed hostnames

## Requirements

- Python 3.6+
- No external dependencies (uses only standard library)

## Files Included

- `netskope_url_sanitizer.py` - Main script
- `netskope_url_sanitizer_README.md` - This documentation
