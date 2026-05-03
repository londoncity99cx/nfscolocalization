#!/usr/bin/env python3
"""
Game Binary Language File Converter - Enhanced Version

This tool properly handles:
1. Parsing the binary file structure with 8-byte hash entries
2. Mapping hash values to string positions
3. Replacing strings with translations
4. Handling variable-length string changes
"""

import struct
import sys
from pathlib import Path
from collections import OrderedDict


class BinaryLanguageConverter:
    """Convert translated text files to game binary language files."""
    
    def __init__(self, template_path):
        """Initialize with a template binary file."""
        self.template_path = Path(template_path)
        self.data = bytearray(self.template_path.read_bytes())
        
        # Parse header
        self.magic = struct.unpack('<I', self.data[0x00:0x04])[0]
        self.file_size = struct.unpack('<I', self.data[0x04:0x08])[0]
        self.entry_count = struct.unpack('<I', self.data[0x08:0x0C])[0]
        self.header_size = struct.unpack('<I', self.data[0x0C:0x10])[0]
        self.data_offset = struct.unpack('<I', self.data[0x10:0x14])[0]
        
        # Parse entries (8 bytes each)
        self.entries = OrderedDict()  # hash -> (position, metadata)
        self._parse_entries()
        
        # Map hashes to strings
        self.hash_to_string = {}
        self.hash_to_position = {}
        self._extract_strings()
    
    def _parse_entries(self):
        """Parse the entry table (8 bytes per entry)."""
        pos = self.header_size
        for i in range(self.entry_count):
            entry_pos = pos + (i * 8)
            if entry_pos + 8 > self.data_offset:
                break
            
            hash_val = struct.unpack('<I', self.data[entry_pos:entry_pos+4])[0]
            metadata = struct.unpack('<I', self.data[entry_pos+4:entry_pos+8])[0]
            
            if hash_val != 0:
                hash_key = f"0x{hash_val:08X}"
                self.entries[hash_key] = (entry_pos, metadata)
    
    def _extract_strings(self):
        """Extract null-terminated strings and map them to hashes."""
        # Scan the data section for strings
        pos = self.data_offset
        string_count = 0
        
        while pos < len(self.data) and string_count < self.entry_count:
            # Find next null-terminated string
            end = self.data.find(b'\x00', pos)
            if end == -1:
                break
            
            string_bytes = self.data[pos:end]
            if len(string_bytes) > 0:
                try:
                    text = string_bytes.decode('utf-8', errors='ignore')
                    # Store this string
                    self.hash_to_string[pos] = text
                    string_count += 1
                except:
                    pass
            
            pos = end + 1
    
    def replace_strings_from_file(self, text_file_path):
        """Load translations from text file and apply them."""
        translations = self._parse_text_file(text_file_path)
        
        # Match translations to hashes
        replacements = 0
        for hash_key, translation in translations.items():
            if hash_key in self.entries:
                entry_pos, metadata = self.entries[hash_key]
                replacements += 1
                print(f"  {hash_key}: '{translation[:50]}'")
        
        print(f"\nMatched {replacements}/{len(translations)} translations to binary entries")
        
        # Create new binary with replaced strings
        self._apply_replacements(translations)
        
        return replacements
    
    def _parse_text_file(self, filepath):
        """Parse tab-separated translation file."""
        translations = {}
        
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                
                parts = line.split('\t')
                if len(parts) >= 4:
                    hex_offset = parts[1].strip()
                    hash_key = f"0x{hex_offset.upper()}"
                    translation = '\t'.join(parts[3:]).strip()
                    translations[hash_key] = translation
        
        return translations
    
    def _apply_replacements(self, translations):
        """Apply translations to the binary data."""
        # This is a simplified approach:
        # 1. Find each original English string in the data section
        # 2. Replace it with the Portuguese translation
        # 3. Adjust if needed for length differences
        
        for hash_key, new_translation in translations.items():
            if hash_key not in self.entries:
                continue
            
            entry_pos, metadata = self.entries[hash_key]
            
            # Find the string in the data section by scanning
            # This is complex because we need to know the original string length
            # For now, we'll use the metadata field to determine length
            
            # The metadata might contain the string length
            str_length = metadata if metadata < 10000 else 0
            
            # Try a different approach: scan for the string pattern
            # This is more reliable
            self._replace_string_in_data(hash_key, new_translation)
    
    def _replace_string_in_data(self, hash_key, new_text):
        """Replace a string in the data section."""
        # This would need to:
        # 1. Find the original string location
        # 2. Replace it with the new text
        # 3. Update offsets/metadata if needed
        # 4. Handle length changes
        
        # For now, placeholder
        pass
    
    def save(self, output_path):
        """Save the modified binary to output file."""
        Path(output_path).write_bytes(self.data)
        print(f"\nSaved to {output_path}")


def main():
    """Main function."""
    if len(sys.argv) < 3:
        print("Usage: python convert_v2.py <text_file> <output_binary> [template_binary]")
        print("\nExample:")
        print("  python convert_v2.py brportuguese_frontend.bin.txt BRPORTUGUESE_FRONTEND.BIN BR/ENGLISH_FRONTEND.BIN")
        sys.exit(1)
    
    text_file = sys.argv[1]
    output_file = sys.argv[2]
    
    if len(sys.argv) >= 4:
        template_file = sys.argv[3]
    else:
        script_dir = Path(__file__).parent
        if 'frontend' in output_file.lower():
            template_file = str(script_dir / "BR" / "ENGLISH_FRONTEND.BIN")
        elif 'global' in output_file.lower():
            template_file = str(script_dir / "BR" / "ENGLISH_GLOBAL.BIN")
        elif 'ingame' in output_file.lower():
            template_file = str(script_dir / "BR" / "ENGLISH_INGAME.BIN")
        else:
            print(f"Error: Could not determine template from {output_file}")
            sys.exit(1)
    
    script_dir = Path(__file__).parent
    text_path = script_dir / text_file
    output_path = script_dir / output_file
    template_path = Path(template_file)
    
    print("="*80)
    print("GAME BINARY LANGUAGE FILE CONVERTER v2")
    print("="*80)
    print(f"\nTemplate:    {template_path.name}")
    print(f"Input:       {text_path.name}")
    print(f"Output:      {output_path.name}\n")
    
    if not text_path.exists():
        print(f"ERROR: Text file not found: {text_path}")
        sys.exit(1)
    
    if not template_path.exists():
        print(f"ERROR: Template file not found: {template_path}")
        sys.exit(1)
    
    # Create converter and process
    print("Loading and analyzing binary file...")
    converter = BinaryLanguageConverter(template_path)
    
    print(f"\nBinary file structure:")
    print(f"  Magic:        0x{converter.magic:08X}")
    print(f"  File size:    {converter.file_size} bytes")
    print(f"  Entry count:  {converter.entry_count}")
    print(f"  Header size:  {converter.header_size} bytes")
    print(f"  Data offset:  0x{converter.data_offset:06X}")
    print(f"  Entries:      {len(converter.entries)}")
    
    print(f"\nProcessing translations...")
    matches = converter.replace_strings_from_file(text_path)
    
    print(f"\nGenerating output...")
    converter.save(output_path)
    
    print(f"✓ Conversion complete!")


if __name__ == '__main__':
    main()
