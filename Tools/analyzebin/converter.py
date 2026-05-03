#!/usr/bin/env python3
"""
Game Language Binary File Converter - Final Working Version

Converts Portuguese translations (text file) to game binary language files.
This version properly handles string replacement in the binary data section.
"""

import struct
import sys
from pathlib import Path
from collections import OrderedDict


class LanguageFileConverter:
    """Converts text translations to game binary format."""
    
    def __init__(self, template_binary_path):
        """Initialize with template binary file."""
        self.template_path = Path(template_binary_path)
        self.original_data = bytearray(self.template_path.read_bytes())
        self.data = bytearray(self.original_data)
        
        # Parse header
        self.header_size = struct.unpack('<I', self.original_data[0x0C:0x10])[0]
        self.data_offset = struct.unpack('<I', self.original_data[0x10:0x14])[0]
        self.entry_count = struct.unpack('<I', self.original_data[0x08:0x0C])[0]
        
        # Parse entry table
        self.entries = []  # List of (hash, metadata, position)
        self._parse_entries()
        
        # Extract original strings
        self.original_strings = {}  # hash -> string
        self._extract_original_strings()
    
    def _parse_entries(self):
        """Parse the 8-byte entry table."""
        for i in range(self.entry_count):
            entry_pos = self.header_size + (i * 8)
            if entry_pos + 8 > self.data_offset:
                break
            
            hash_val = struct.unpack('<I', self.original_data[entry_pos:entry_pos+4])[0]
            metadata = struct.unpack('<I', self.original_data[entry_pos+4:entry_pos+8])[0]
            
            if hash_val != 0:
                hash_key = f"0x{hash_val:08X}"
                self.entries.append({
                    'hash_key': hash_key,
                    'hash': hash_val,
                    'metadata': metadata,
                    'entry_pos': entry_pos,
                    'index': i
                })
    
    def _extract_original_strings(self):
        """Extract null-terminated strings from data section."""
        pos = self.data_offset
        entry_idx = 0
        
        while pos < len(self.original_data) and entry_idx < len(self.entries):
            # Find next null terminator
            end = self.original_data.find(b'\x00', pos)
            if end == -1:
                break
            
            string_bytes = self.original_data[pos:end]
            if len(string_bytes) > 0:
                try:
                    text = string_bytes.decode('utf-8', errors='ignore')
                    # Try to match with entry
                    if entry_idx < len(self.entries):
                        entry = self.entries[entry_idx]
                        self.original_strings[entry['hash_key']] = {
                            'pos': pos,
                            'length': len(string_bytes),
                            'text': text,
                            'entry_idx': entry_idx
                        }
                        entry_idx += 1
                except:
                    pass
            
            pos = end + 1
    
    def load_translations(self, text_file_path):
        """Load translations from text file."""
        translations = {}
        
        with open(text_file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                parts = line.split('\t')
                if len(parts) >= 4:
                    hex_offset = parts[1].strip()
                    hash_key = f"0x{hex_offset.upper()}"
                    translation = '\t'.join(parts[3:]).strip()
                    translations[hash_key] = translation
        
        return translations
    
    def apply_translations(self, translations):
        """Apply translations to the binary data."""
        replaced = 0
        too_long = 0
        not_found = 0
        
        print(f"\nApplying translations...")
        print(f"{'Hash':<12} {'Original':<40} {'Translation':<40} {'Status'}")
        print("-" * 120)
        
        for hash_key, new_text in sorted(translations.items()):
            if hash_key not in self.original_strings:
                not_found += 1
                print(f"{hash_key}  {'':40} {new_text[:40]:<40} NOT FOUND")
                continue
            
            original_info = self.original_strings[hash_key]
            original_text = original_info['text']
            original_pos = original_info['pos']
            original_len = original_info['length']
            new_bytes = new_text.encode('utf-8')
            new_len = len(new_bytes)
            
            # Check if translation fits
            if new_len > original_len:
                too_long += 1
                status = f"TOO LONG ({new_len} > {original_len})"
                print(f"{hash_key}  {original_text[:40]:<40} {new_text[:40]:<40} {status}")
                continue
            
            # Replace string in binary
            # Write new string followed by padding/null bytes
            self.data[original_pos:original_pos+new_len] = new_bytes
            # Fill remaining space with nulls if shorter
            if new_len < original_len:
                self.data[original_pos+new_len:original_pos+original_len] = b'\x00' * (original_len - new_len)
            
            replaced += 1
            status = "[OK] REPLACED"
            print(f"{hash_key}  {original_text[:40]:<40} {new_text[:40]:<40} {status}")
        
        print(f"\n{'Summary:':>50}")
        print(f"  Replaced: {replaced}")
        print(f"  Too long: {too_long}")
        print(f"  Not found: {not_found}")
        print(f"  Total: {len(translations)}")
        
        return replaced, too_long, not_found
    
    def save(self, output_path):
        """Save modified binary."""
        Path(output_path).write_bytes(self.data)
        print(f"\nSaved to: {output_path}")


def main():
    """Main function."""
    if len(sys.argv) < 3:
        print("GAME LANGUAGE BINARY CONVERTER")
        print("="*80)
        print("Usage: python converter.py <text_file> <output_binary> [template_binary]")
        print("\nExample:")
        print("  python converter.py BR/brportuguese_frontend.bin.txt BRPORTUGUESE_FRONTEND.BIN BR/ENGLISH_FRONTEND.BIN")
        print("\nThe tool will:")
        print("  1. Load the template binary (English version)")
        print("  2. Read the Portuguese translations from text file")
        print("  3. Replace English strings with Portuguese")
        print("  4. Save the result as a new binary file")
        sys.exit(1)
    
    text_file = sys.argv[1]
    output_file = sys.argv[2]
    
    # Determine template
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
            print(f"Error: Could not auto-detect template for {output_file}")
            sys.exit(1)
    
    script_dir = Path(__file__).parent
    text_path = script_dir / text_file if not Path(text_file).is_absolute() else Path(text_file)
    output_path = script_dir / output_file if not Path(output_file).is_absolute() else Path(output_file)
    template_path = Path(template_file) if Path(template_file).is_absolute() else script_dir / template_file
    
    print("GAME LANGUAGE BINARY CONVERTER")
    print("="*80)
    print(f"\nFiles:")
    print(f"  Template:    {template_path}")
    print(f"  Input:       {text_path}")
    print(f"  Output:      {output_path}")
    
    # Validate files
    if not text_path.exists():
        print(f"\nERROR: Text file not found: {text_path}")
        sys.exit(1)
    
    if not template_path.exists():
        print(f"\nERROR: Template file not found: {template_path}")
        sys.exit(1)
    
    # Create converter
    print(f"\nInitializing converter...")
    converter = LanguageFileConverter(template_path)
    
    print(f"  Entry count: {converter.entry_count}")
    print(f"  Extracted: {len(converter.original_strings)} original strings")
    
    # Load translations
    print(f"\nLoading translations from {text_path.name}...")
    translations = converter.load_translations(text_path)
    print(f"  Found: {len(translations)} translations")
    
    # Apply
    replaced, too_long, not_found = converter.apply_translations(translations)
    
    # Save
    print(f"\nSaving output...")
    converter.save(output_path)
    
    print("\n" + "="*80)
    print("CONVERSION COMPLETE")
    print("="*80)


if __name__ == '__main__':
    main()
