#!/usr/bin/env python3
import os
import struct
import re

def compile_po_to_mo(po_file, mo_file):
    """Simple po to mo compiler"""
    
    # Read po file
    with open(po_file, 'r', encoding='utf-8') as f:
        po_content = f.read()
    
    # Parse msgid and msgstr pairs
    messages = {}
    msgid_pattern = r'msgid\s+"([^"]*)"'
    msgstr_pattern = r'msgstr\s+"([^"]*)"'
    
    lines = po_content.split('\n')
    current_msgid = None
    
    for line in lines:
        line = line.strip()
        if line.startswith('msgid'):
            match = re.search(r'msgid\s+"([^"]*)"', line)
            if match:
                current_msgid = match.group(1)
        elif line.startswith('msgstr') and current_msgid is not None:
            match = re.search(r'msgstr\s+"([^"]*)"', line)
            if match:
                msgstr = match.group(1)
                if current_msgid and msgstr:  # Only add non-empty translations
                    messages[current_msgid] = msgstr
                current_msgid = None
    
    # Create mo file
    keys = list(messages.keys())
    values = list(messages.values())
    
    # Encode strings
    kencoded = [k.encode('utf-8') for k in keys]
    vencoded = [v.encode('utf-8') for v in values]
    
    # Calculate offsets
    keyoffsets = []
    valueoffsets = []
    
    # Magic number for little-endian mo files
    magic = 0xde120495
    
    # Header
    numkeys = len(keys)
    
    # Key and value tables start after header
    keystart = 7 * 4
    valuestart = keystart + numkeys * 8
    
    # Calculate string positions
    keydata = b''
    valuedata = b''
    
    for k in kencoded:
        keyoffsets.append((len(k), len(keydata)))
        keydata += k
    
    for v in vencoded:
        valueoffsets.append((len(v), len(valuedata)))
        valuedata += v
    
    # Adjust offsets to absolute positions
    keystart_abs = valuestart + numkeys * 8
    valuestart_abs = keystart_abs + len(keydata)
    
    # Build mo file
    output = struct.pack('<I', magic)  # Magic
    output += struct.pack('<I', 0)     # Version
    output += struct.pack('<I', numkeys)  # Number of strings
    output += struct.pack('<I', keystart)  # Offset of key table
    output += struct.pack('<I', valuestart)  # Offset of value table
    output += struct.pack('<I', 0)     # Hash table size
    output += struct.pack('<I', 0)     # Offset of hash table
    
    # Key table
    for length, offset in keyoffsets:
        output += struct.pack('<I', length)
        output += struct.pack('<I', keystart_abs + offset)
    
    # Value table
    for length, offset in valueoffsets:
        output += struct.pack('<I', length)
        output += struct.pack('<I', valuestart_abs + offset)
    
    # String data
    output += keydata
    output += valuedata
    
    # Write mo file
    with open(mo_file, 'wb') as f:
        f.write(output)
    
    print(f"Compiled {po_file} to {mo_file} with {numkeys} translations")

if __name__ == '__main__':
    po_path = r'netbox_maintenance_device\locale\pt_BR\LC_MESSAGES\django.po'
    mo_path = r'netbox_maintenance_device\locale\pt_BR\LC_MESSAGES\django.mo'
    
    compile_po_to_mo(po_path, mo_path)
