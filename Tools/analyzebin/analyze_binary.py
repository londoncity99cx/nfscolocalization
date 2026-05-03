#!/usr/bin/env python3
"""
Binary Language File Analyzer
Helps understand the structure of the game's binary language files.
"""

import struct
from pathlib import Path


def analyze_binary_file(filepath, max_entries=20):
    """Analyze the structure of a binary language file."""
    
    with open(filepath, 'rb') as f:
        data = f.read()
    
    print(f"File: {Path(filepath).name}")
    print(f"Size: {len(data)} bytes (0x{len(data):X})")
    print("\n" + "="*80)
    print("HEADER ANALYSIS (first 128 bytes)")
    print("="*80)
    
    # Display hex dump of header
    for i in range(0, min(128, len(data)), 16):
        hex_str = ' '.join(f'{b:02X}' for b in data[i:i+16])
        ascii_str = ''.join(chr(b) if 32 <= b < 127 else '.' for b in data[i:i+16])
        print(f"0x{i:08X}: {hex_str:<48} | {ascii_str}")
    
    print("\n" + "="*80)
    print("POTENTIAL STRUCTURE DETECTION")
    print("="*80)
    
    # Look for patterns
    # Pattern 1: Looking for 4-byte little-endian values that might be offsets
    print("\nSearching for 4-byte little-endian values (potential offsets/lengths)...")
    
    potential_offsets = []
    for i in range(0, min(200, len(data)-4), 4):
        value = struct.unpack('<I', data[i:i+4])[0]
        # Check if this could be a valid offset (reasonable size)
        if 0x1000 < value < len(data):
            potential_offsets.append((i, value))
    
    if potential_offsets:
        print(f"\nFound {len(potential_offsets)} potential offset values:")
        for offset, value in potential_offsets[:10]:
            print(f"  At 0x{offset:06X}: value = 0x{value:08X} ({value})")
    
    # Pattern 2: Look for null-terminated strings
    print("\n\nSearching for null-terminated strings...")
    strings_found = []
    current_string = b''
    current_pos = 0
    
    for i, byte in enumerate(data):
        if 32 <= byte <= 126 or byte in (9, 10, 13):  # Printable ASCII + whitespace
            current_string += bytes([byte])
        elif byte == 0 and len(current_string) > 2:  # Null terminator
            try:
                decoded = current_string.decode('utf-8')
                strings_found.append((current_pos, decoded))
            except:
                pass
            current_string = b''
            current_pos = i + 1
        else:
            current_string = b''
    
    if strings_found:
        print(f"Found {len(strings_found)} strings:")
        for pos, s in strings_found[:15]:
            print(f"  0x{pos:06X}: {s[:60]}")
    
    print("\n" + "="*80)
    print("NEXT STEPS")
    print("="*80)
    print("""
To properly reverse the format, we need:
1. Compare ENGLISH_FRONTEND.BIN with another language version if available
2. Use a hex editor to identify the structure
3. Look for patterns in how offsets/hashes correlate to string positions

Options:
a) Provide a hex dump comparison between two language versions
b) Provide the game's source code or documentation
c) Use binary diffing tools to understand the mapping
    """)


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python analyze_binary.py <binary_file>")
        print("\nExample:")
        print("  python analyze_binary.py ENGLISH_FRONTEND.BIN")
        sys.exit(1)
    
    filepath = sys.argv[1]
    if not Path(filepath).exists():
        print(f"Error: File not found: {filepath}")
        sys.exit(1)
    
    analyze_binary_file(filepath)
