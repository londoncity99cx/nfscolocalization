#!/usr/bin/env python3
"""
Game Language Binary File Converter
Converts translated text files to game binary language files.

This tool:
1. Reads a binary template file (e.g., ENGLISH_FRONTEND.BIN)
2. Reads a tab-separated text file with translations
3. Maps translations to the correct hash values
4. Generates a new binary file with the updated strings

Format expected:
  Chunk<TAB>HexOffset<TAB>HexWithPrefix<TAB>Translation
  0<TAB>000BA070<TAB>0x000BA070<TAB>MISSING_STRING
"""

import struct
import sys
from pathlib import Path
from collections import OrderedDict
import io


class BinaryLanguageFile:
    """Handler for game binary language files."""
    
    def __init__(self, filepath):
        """Load and parse a binary language file."""
        self.filepath = Path(filepath)
        self.data = bytearray(self.filepath.read_bytes())
        self.entries = OrderedDict()  # hash -> string
        self.hash_positions = {}  # hash -> file position
        
        self._parse_structure()
    
    def _parse_structure(self):
        """Parse the binary file structure."""
        # Header structure:
        # 0x00-0x03: Version/Magic
        # 0x04-0x07: File size
        # 0x08-0x0B: Number of entries  
        # 0x0C-0x0F: Header size
        # 0x10-0x13: Data section offset
        # 0x14+: Filename string
        
        if len(self.data) < 20:
            raise ValueError("File too small to be a valid binary language file")
        
        magic = struct.unpack('<I', self.data[0x00:0x04])[0]
        file_size = struct.unpack('<I', self.data[0x04:0x08])[0]
        entry_count = struct.unpack('<I', self.data[0x08:0x0C])[0]
        header_size = struct.unpack('<I', self.data[0x0C:0x10])[0]
        data_offset = struct.unpack('<I', self.data[0x10:0x14])[0]
        
        print(f"File: {self.filepath.name}")
        print(f"  Magic: 0x{magic:08X}")
        print(f"  File size: {file_size} bytes (actual: {len(self.data)})")
        print(f"  Entry count: {entry_count}")
        print(f"  Header size: {header_size}")
        print(f"  Data offset: 0x{data_offset:06X}")
        
        # Extract filename
        filename_end = self.data.find(b'\x00', 0x14)
        filename = self.data[0x14:filename_end].decode('utf-8', errors='ignore')
        print(f"  Filename: {filename}")
        
        # Parse entry table
        # Starting at header_size, we have hash-offset pairs
        pos = header_size
        print(f"\nParsing {entry_count} entries starting at 0x{pos:06X}...")
        
        entry_num = 0
        while pos < min(len(self.data), data_offset) and entry_num < entry_count:
            if pos + 8 > len(self.data):
                break
            
            # Try to read hash and length
            hash_val = struct.unpack('<I', self.data[pos:pos+4])[0]
            metadata = struct.unpack('<I', self.data[pos+4:pos+8])[0]
            
            # Skip obvious invalid entries
            if hash_val == 0:
                pos += 8
                continue
            
            self.hash_positions[f"0x{hash_val:08X}"] = pos
            entry_num += 1
            pos += 8
        
        print(f"Found {len(self.hash_positions)} entries with hash values")
    
    def extract_strings(self):
        """Extract strings from the binary file, trying to map to hashes."""
        strings = {}
        
        # Find all null-terminated strings
        pos = 0
        while pos < len(self.data):
            # Try to find a string
            end = self.data.find(b'\x00', pos)
            if end == -1:
                break
            
            try:
                string_bytes = self.data[pos:end]
                if len(string_bytes) >= 2:  # Minimum length
                    decoded = string_bytes.decode('utf-8')
                    if len(decoded) > 0 and not any(ord(c) < 32 or ord(c) > 126 for c in decoded if c not in '\t\n\r'):
                        strings[pos] = decoded
                        print(f"  0x{pos:06X}: {decoded[:50]}{'...' if len(decoded) > 50 else ''}")
                pos = end + 1
            except:
                pos = end + 1
        
        return strings
    
    def get_hash_at_position(self, pos):
        """Get the hash value at a given position in the entry table."""
        if pos + 4 <= len(self.data):
            return struct.unpack('<I', self.data[pos:pos+4])[0]
        return None


def parse_translation_file(filepath):
    """Parse a tab-separated translation text file."""
    translations = {}
    
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            
            parts = line.split('\t')
            if len(parts) >= 4:
                # parts[0] = Chunk number
                # parts[1] = Hex offset (e.g., "000BA070")
                # parts[2] = Hex with prefix (e.g., "0x000BA070")  
                # parts[3...] = Translation text
                
                hex_offset = parts[1].strip()
                hash_key = f"0x{hex_offset.upper()}"
                translation = '\t'.join(parts[3:]).strip()
                
                translations[hash_key] = translation
    
    return translations


def main():
    """Main function."""
    if len(sys.argv) < 3:
        print("Usage: python convert_to_binary.py <text_file> <output_binary> [template_binary]")
        print("\nExample:")
        print("  python convert_to_binary.py brportuguese_frontend.bin.txt BRPORTUGUESE_FRONTEND.BIN ENGLISH_FRONTEND.BIN")
        print("\nIf template_binary is not specified, will use ENGLISH_<type>.BIN")
        sys.exit(1)
    
    text_file = sys.argv[1]
    output_file = sys.argv[2]
    
    # Determine template file
    if len(sys.argv) >= 4:
        template_file = sys.argv[3]
    else:
        # Auto-detect based on output filename
        if 'frontend' in output_file.lower():
            template_file = 'ENGLISH_FRONTEND.BIN'
        elif 'global' in output_file.lower():
            template_file = 'ENGLISH_GLOBAL.BIN'
        elif 'ingame' in output_file.lower():
            template_file = 'ENGLISH_INGAME.BIN'
        else:
            print(f"Error: Could not determine template file type from {output_file}")
            sys.exit(1)
    
    # Verify files exist
    script_dir = Path(__file__).parent
    text_path = script_dir / text_file
    output_path = script_dir / output_file
    template_path = script_dir / template_file
    
    print("="*80)
    print("GAME LANGUAGE BINARY CONVERTER")
    print("="*80)
    print(f"\nInput translation file:  {text_path}")
    print(f"Template binary file:    {template_path}")
    print(f"Output binary file:      {output_path}\n")
    
    if not text_path.exists():
        print(f"ERROR: Text file not found: {text_path}")
        sys.exit(1)
    
    if not template_path.exists():
        print(f"ERROR: Template binary file not found: {template_path}")
        sys.exit(1)
    
    # Load translation file
    print("Step 1: Loading translations...")
    translations = parse_translation_file(text_path)
    print(f"  Loaded {len(translations)} translation entries\n")
    
    # Load template binary
    print("Step 2: Analyzing template binary file...")
    try:
        binary = BinaryLanguageFile(template_path)
    except Exception as e:
        print(f"ERROR: Failed to parse template binary: {e}")
        sys.exit(1)
    
    print(f"\nStep 3: Applying translations...")
    # For now, create a copy of the template
    # TODO: Implement proper string replacement logic
    output_data = bytearray(binary.data)
    
    # Show what translations were found
    print(f"Translations to apply:")
    for hash_key, translation in list(translations.items())[:10]:
        print(f"  {hash_key}: {translation[:50]}")
    if len(translations) > 10:
        print(f"  ... and {len(translations) - 10} more")
    
    print(f"\nStep 4: Writing output file...")
    output_path.write_bytes(output_data)
    print(f"  Created {output_path}")
    
    print("\n" + "="*80)
    print("NOTE: This version creates a copy of the template.")
    print("String replacement logic is being developed.")
    print("="*80)


if __name__ == '__main__':
    main()
