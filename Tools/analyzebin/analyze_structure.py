#!/usr/bin/env python3
"""
Binary File Structure Analyzer
Analyzes the relationship between entry table and string data.
"""

import struct
from pathlib import Path


def analyze_structure(binary_path):
    """Detailed analysis of binary file structure."""
    data = Path(binary_path).read_bytes()
    
    # Header
    magic = struct.unpack('<I', data[0x00:0x04])[0]
    file_size = struct.unpack('<I', data[0x04:0x08])[0]
    entry_count = struct.unpack('<I', data[0x08:0x0C])[0]
    header_size = struct.unpack('<I', data[0x0C:0x10])[0]
    data_offset = struct.unpack('<I', data[0x10:0x14])[0]
    
    print("BINARY FILE STRUCTURE ANALYSIS")
    print("="*80)
    print(f"File: {Path(binary_path).name}")
    print(f"Size: {len(data)} bytes")
    print(f"Magic: 0x{magic:08X}")
    print(f"Entry count: {entry_count}")
    print(f"Data section starts at: 0x{data_offset:06X} ({data_offset})")
    
    print(f"\nENTRY TABLE ANALYSIS")
    print("="*80)
    print(f"Entry table location: 0x{header_size:06X} to 0x{data_offset:06X}")
    print(f"Entry table size: {data_offset - header_size} bytes")
    print(f"Bytes per entry: {(data_offset - header_size) // entry_count}")
    
    # Analyze first 10 entries
    print(f"\nFIRST 10 ENTRIES:")
    print(f"{'#':>3} {'Entry Offset':>12} {'Hash':>10} {'Metadata':>10} {'Hex Meta':>10}")
    print("-" * 60)
    
    entries_data = []
    for i in range(min(10, entry_count)):
        entry_pos = header_size + (i * 8)
        hash_val = struct.unpack('<I', data[entry_pos:entry_pos+4])[0]
        metadata = struct.unpack('<I', data[entry_pos+4:entry_pos+8])[0]
        
        entries_data.append((hash_val, metadata))
        print(f"{i:3d} 0x{entry_pos:08X}   0x{hash_val:08X}  {metadata:10d}  0x{metadata:08X}")
    
    # Analyze data section strings
    print(f"\nDATA SECTION ANALYSIS")
    print("="*80)
    print(f"Scanning for null-terminated strings starting at 0x{data_offset:06X}...\n")
    
    strings = []
    pos = data_offset
    string_num = 0
    
    while pos < len(data) and string_num < 15:
        end = data.find(b'\x00', pos)
        if end == -1:
            break
        
        string_bytes = data[pos:end]
        if len(string_bytes) > 0:
            try:
                text = string_bytes.decode('utf-8', errors='ignore')
                strings.append((pos, len(string_bytes), text))
                print(f"{string_num:3d} 0x{pos:06X} (len={len(string_bytes):3d}): {text[:60]}")
                string_num += 1
            except:
                pass
        
        pos = end + 1
    
    # Analyze relationship
    print(f"\n\nRELATIONSHIP ANALYSIS")
    print("="*80)
    print(f"Comparing entry metadata with string lengths:\n")
    print(f"Entry# Hash         Metadata  String#  Str Pos   Str Len  Match?")
    print("-" * 70)
    
    for i, (hash_val, metadata) in enumerate(entries_data[:10]):
        if i < len(strings):
            str_pos, str_len, str_text = strings[i]
            match = "✓" if metadata == str_len else ("≈" if abs(metadata - str_len) < 5 else "✗")
            print(f"{i:5d}  0x{hash_val:08X}  {metadata:8d}  {i:7d}  0x{str_pos:06X}  {str_len:6d}  {match}")
    
    # Check if metadata could be offset
    print(f"\n\nCHECKING IF METADATA IS OFFSET:")
    print(f"Entry# Metadata(Dec) Metadata(Hex) Points to byte:")
    print("-" * 60)
    
    for i, (hash_val, metadata) in enumerate(entries_data[:5]):
        if metadata < len(data):
            byte_val = data[metadata]
            print(f"{i:5d}  {metadata:10d}   0x{metadata:08X}      {chr(byte_val) if 32 <= byte_val < 127 else f'0x{byte_val:02X}'}")


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python analyze_structure.py <binary_file>")
        print("\nExample:")
        print("  python analyze_structure.py BR/ENGLISH_FRONTEND.BIN")
        sys.exit(1)
    
    filepath = sys.argv[1]
    if not Path(filepath).exists():
        print(f"Error: File not found: {filepath}")
        sys.exit(1)
    
    analyze_structure(filepath)
