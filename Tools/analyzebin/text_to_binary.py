#!/usr/bin/env python3
"""
Convert language text files to game binary language files.
The text files are tab-separated exports from the SQLite database.
"""

import os
import struct
import sys
from pathlib import Path


def parse_text_file(filepath):
    """
    Parse a tab-separated text file with translations.
    Format: Chunk\tHex_Offset\tHex_With_Prefix\tTranslation
    Returns: dict mapping hex offset strings to translation text
    """
    translations = {}
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                
                parts = line.split('\t')
                if len(parts) >= 4:
                    # Column 0: Chunk number
                    # Column 1: Hex offset (e.g., "000BA070")
                    # Column 2: Hex with prefix (e.g., "0x000BA070")
                    # Column 3+: Translation text
                    
                    hex_offset = parts[1].strip()
                    translation = '\t'.join(parts[3:]).strip()
                    
                    # Store using the 0x prefix format
                    key = f"0x{hex_offset}"
                    translations[key] = translation
        
        return translations
    
    except Exception as e:
        print(f"Error parsing text file {filepath}: {e}")
        return {}


def load_template_binary(binary_path):
    """Load the template binary file into memory."""
    try:
        with open(binary_path, 'rb') as f:
            return bytearray(f.read())
    except Exception as e:
        print(f"Error loading binary file {binary_path}: {e}")
        return None


def hex_string_to_offset(hex_str):
    """Convert hex string (e.g., '0x000BA070') to integer offset."""
    try:
        return int(hex_str, 16)
    except ValueError:
        return None


def write_translations_to_binary(template_binary, translations):
    """
    Write translations to binary file at their specified offsets.
    
    Args:
        template_binary: bytearray of the template binary file
        translations: dict mapping hex offset strings to translation text
    
    Returns:
        Modified bytearray or None if error
    """
    result = template_binary[:]
    
    for hex_offset, translation in translations.items():
        offset = hex_string_to_offset(hex_offset)
        
        if offset is None:
            print(f"Warning: Could not parse offset {hex_offset}")
            continue
        
        if offset < 0 or offset >= len(result):
            print(f"Warning: Offset {hex_offset} ({offset}) is out of bounds")
            continue
        
        # Encode translation to UTF-8 bytes
        text_bytes = translation.encode('utf-8')
        text_length = len(text_bytes)
        
        # Check if we have enough space to write
        # We need: length marker (4 bytes) + text data
        if offset + 4 + text_length > len(result):
            print(f"Warning: Not enough space at offset {hex_offset} for '{translation[:30]}...'")
            continue
        
        # Write length (4 bytes, little-endian)
        # Note: This assumes the length is stored before the string
        result[offset:offset+4] = struct.pack('<I', text_length)
        
        # Write string data
        result[offset+4:offset+4+text_length] = text_bytes
        
        print(f"Updated offset {hex_offset}: '{translation[:50]}{'...' if len(translation) > 50 else ''}'")
    
    return result


def main():
    """Main function."""
    if len(sys.argv) < 2:
        print("Usage: python text_to_binary.py <text_file> [output_binary_file]")
        print("\nExample:")
        print("  python text_to_binary.py brportuguese_frontend.bin.txt BRPORTUGUESE_FRONTEND.BIN")
        print("\nThis script will:")
        print("  1. Parse the text file with translations")
        print("  2. Use ENGLISH_FRONTEND.BIN as template")
        print("  3. Write translations to specified output binary file")
        sys.exit(1)
    
    text_file = sys.argv[1]
    
    # Determine output file
    if len(sys.argv) >= 3:
        output_file = sys.argv[2]
    else:
        # Generate output filename
        base_name = Path(text_file).stem
        if '.bin' in base_name:
            output_file = base_name.replace('.bin', '.BIN').upper()
        else:
            output_file = f"{base_name}.BIN"
    
    # Determine template file based on input
    if 'frontend' in text_file.lower():
        template_file = 'ENGLISH_FRONTEND.BIN'
    elif 'global' in text_file.lower():
        template_file = 'ENGLISH_GLOBAL.BIN'
    elif 'ingame' in text_file.lower():
        template_file = 'ENGLISH_INGAME.BIN'
    else:
        print(f"Error: Could not determine template file for {text_file}")
        print("Expected filename to contain 'frontend', 'global', or 'ingame'")
        sys.exit(1)
    
    # Get directory of script
    script_dir = Path(__file__).parent
    text_path = script_dir / text_file
    template_path = script_dir / template_file
    output_path = script_dir / output_file
    
    print(f"Text file:     {text_path}")
    print(f"Template:      {template_path}")
    print(f"Output file:   {output_path}")
    print()
    
    # Check files exist
    if not text_path.exists():
        print(f"Error: Text file not found: {text_path}")
        sys.exit(1)
    
    if not template_path.exists():
        print(f"Error: Template file not found: {template_path}")
        print(f"Please ensure {template_file} exists in the same directory")
        sys.exit(1)
    
    # Parse translations
    print("Parsing translations...")
    translations = parse_text_file(text_path)
    print(f"Found {len(translations)} translations")
    
    # Load template
    print(f"\nLoading template binary file...")
    template_binary = load_template_binary(template_path)
    if template_binary is None:
        sys.exit(1)
    print(f"Template size: {len(template_binary)} bytes")
    
    # Write translations
    print(f"\nWriting translations...")
    result = write_translations_to_binary(template_binary, translations)
    
    if result is None:
        print("Error: Failed to write translations")
        sys.exit(1)
    
    # Save output
    print(f"\nSaving to {output_path}...")
    try:
        with open(output_path, 'wb') as f:
            f.write(result)
        print(f"Success! Created {output_path}")
    except Exception as e:
        print(f"Error writing output file: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
