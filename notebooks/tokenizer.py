#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# @created: 20.09.2024
# @author: Aleksey Komissarov
# @contact: ad3002@gmail.com

import json
import sys
from tqdm import tqdm

def generate_bytes_char_mapping():
    """
    Generates byte-to-character and character-to-byte mappings consistent with the Rust encoder.

    Returns:
        byte_to_char (dict): Maps each byte (0-255) to a unique Unicode character.
        char_to_byte (dict): Reverse mapping from Unicode characters to bytes.
    """
    # Step 1: Define the initial bytes (188 bytes)
    initial_bytes = list(range(0x21, 0x7F))  # 0x21 (!) to 0x7E (~)
    initial_bytes += list(range(0xA1, 0xAD))  # 0xA1 to 0xAC
    initial_bytes += list(range(0xAE, 0x100))  # 0xAE to 0xFF

    # Step 2: Identify missing bytes (68 bytes)
    all_bytes = set(range(256))
    present_bytes = set(initial_bytes)
    missing_bytes = sorted(all_bytes - present_bytes)

    # Step 3: Create mappings
    byte_to_char = {}
    char_to_byte = {}

    # Map initial bytes to their direct Unicode equivalents
    for byte in initial_bytes:
        char = chr(byte)
        byte_to_char[byte] = char
        char_to_byte[char] = byte

    # Map missing bytes to unique Unicode characters starting from U+0100
    start_code_point = 0x0100  # U+0100 (Ā)
    for i, byte in enumerate(missing_bytes):
        char = chr(start_code_point + i)
        byte_to_char[byte] = char
        char_to_byte[char] = byte

    return byte_to_char, char_to_byte

# Generate the mappings
byte_to_char, char_to_byte = generate_bytes_char_mapping()


def byte_level_decode(encoded_string, char_to_byte, encoding='utf-8'):
    """
    Decodes a ByteLevel encoded string back to the original string using the provided mapping.

    Parameters:
        encoded_string (str): The ByteLevel encoded string.
        char_to_byte (dict): Mapping from Unicode characters to byte values.
        encoding (str): The encoding to use for the output string (default: 'utf-8').

    Returns:
        str: The decoded original string.
    """
    decoded_bytes = bytearray()
    for char in encoded_string:
        if char in char_to_byte:
            decoded_bytes.append(char_to_byte[char])
        else:
            raise ValueError(f"Unknown character in encoded string: {char}")
            # Alternatively, use a placeholder:
            # decoded_bytes.append(ord('?'))

    try:
        return decoded_bytes.decode(encoding)
    except UnicodeDecodeError as e:
        raise UnicodeDecodeError(f"Failed to decode byte sequence: {e}")

def byte_level_decode_custom(encoded_string, char_to_byte, encoding='utf-8'):
    """
    Decodes a ByteLevel encoded string back to the original string using the provided mapping.
    Handles invalid UTF-8 sequences by replacing them with � and incomplete bytes at the end with <0xXX>.

    Parameters:
        encoded_string (str): The ByteLevel encoded string.
        char_to_byte (dict): Mapping from Unicode characters to byte values.
        encoding (str): The encoding to use for the output string (default: 'utf-8').

    Returns:
        str: The decoded original string with � for invalid sequences and <0xXX> for incomplete bytes.
    """
    # Step 1: Convert encoded characters back to bytes
    byte_seq = bytearray()
    for char in encoded_string:
        if char in char_to_byte:
            byte_seq.append(char_to_byte[char])
        else:
            # Handle unknown characters by replacing with � (0xFF)
            byte_seq.append(0xFF)  # You can choose a different placeholder if needed

    # Step 2: Iterate through the byte sequence to decode UTF-8 characters
    decoded_chars = []
    i = 0
    n = len(byte_seq)

    while i < n:
        byte = byte_seq[i]
        # Single-byte (ASCII)
        if byte <= 0x7F:
            decoded_chars.append(chr(byte))
            i += 1
        # Two-byte sequence
        elif 0xC0 <= byte <= 0xDF:
            if i + 1 < n:
                next_byte = byte_seq[i + 1]
                if 0x80 <= next_byte <= 0xBF:
                    try:
                        char = bytes(byte_seq[i:i+2]).decode(encoding)
                        decoded_chars.append(char)
                        i += 2
                        continue
                    except UnicodeDecodeError:
                        pass
            # Invalid continuation byte
            decoded_chars.append('�')
            i += 1
        # Three-byte sequence
        elif 0xE0 <= byte <= 0xEF:
            if i + 2 < n:
                next1 = byte_seq[i + 1]
                next2 = byte_seq[i + 2]
                if 0x80 <= next1 <= 0xBF and 0x80 <= next2 <= 0xBF:
                    try:
                        char = bytes(byte_seq[i:i+3]).decode(encoding)
                        decoded_chars.append(char)
                        i += 3
                        continue
                    except UnicodeDecodeError:
                        pass
            # Invalid continuation bytes
            decoded_chars.append('�')
            i += 1
        # Four-byte sequence
        elif 0xF0 <= byte <= 0xF7:
            if i + 3 < n:
                next1 = byte_seq[i + 1]
                next2 = byte_seq[i + 2]
                next3 = byte_seq[i + 3]
                if 0x80 <= next1 <= 0xBF and 0x80 <= next2 <= 0xBF and 0x80 <= next3 <= 0xBF:
                    try:
                        char = bytes(byte_seq[i:i+4]).decode(encoding)
                        decoded_chars.append(char)
                        i += 4
                        continue
                    except UnicodeDecodeError:
                        pass
            # Invalid continuation bytes
            decoded_chars.append('�')
            i += 1
        else:
            # Invalid start byte
            decoded_chars.append('�')
            i += 1

    # Step 3: Check for incomplete bytes at the end
    # In this implementation, incomplete bytes are already handled by replacing with �
    # If you want to represent incomplete bytes specifically, additional logic is needed

    return ''.join(decoded_chars)



def load_vocab(tokenizer_file):

    vocab = {}

    try:
        with open(tokenizer_file, "r") as fr:
            tokenizer = json.load(fr)
    except json.decoder.JSONDecodeError:
        print(f"Bad tokenizer file: {tokenizer_file}")
        print("Please provide a valid tokenizer file.")
        print("Here are the first few lines of the file:")
        with open(tokenizer_file, "r") as fr:
            for i, line in enumerate(fr):
                print(line)
                if i > 10:
                    break
        sys.exit(1)
    if not "model" in tokenizer:
        if "vocab" in tokenizer:
            tokenizer["model"] = {"vocab": tokenizer["vocab"]}
        if "mama" in tokenizer:
            tokenizer["model"] = {
                "vocab": tokenizer
            }
        with open(tokenizer_file, "w") as fw:
            json.dump(tokenizer, fw, indent=2)

    ### rare case with negative ranks
    if "model" in tokenizer and "vocab" in tokenizer["model"]:
        if isinstance(tokenizer["model"]["vocab"], list):
            print("Bad format for vocab")
            sys.exit(1)
    if not "model" in tokenizer or not "vocab" in tokenizer["model"]:
        print("Bad format for vocab")
        sys.exit(1)
    
    with open(tokenizer_file) as fh:
        text_data = fh.read()

    replacers = [
         ( text_data.count("▁"), "▁"),
         ( text_data.count("Ġ"), "Ġ"),
         ( text_data.count("\u0120"), "\u0120"),
         ( text_data.count("\t"), "\t"),
         ( text_data.count("\u2581"), "\u2581"),
    ]
    replacers.sort()
    replace = replacers[-1][1]
    if replace == "Ġ":
        replace = None
       
        
    should_be_fixed = "ма" not in text_data
    for raw_token, rid, in tokenizer["model"]["vocab"].items():
        
        rr = raw_token
        if replace and raw_token.startswith(replace) and len(raw_token) > 1:
          if should_be_fixed:
            raw_token = "Ġ" + replace.join(raw_token.split(replace)[1:])
          else:
            raw_token = " " + replace.join(raw_token.split(replace)[1:])
            
        if raw_token.lower().startswith("<0x"):
          token = byte_to_char[eval(raw_token[1:-1])]
          vocab[token] = rid
          continue
    
        if should_be_fixed:
          token =  byte_level_decode_custom(raw_token, char_to_byte)
          if [1 for x in token if ord(x) == 65533]:
            token = f"<0y{raw_token}>"
        else:
          if raw_token in char_to_byte:
            token = str(hex(char_to_byte[raw_token])).upper()
          else:
            token = raw_token
        try:
          assert token not in vocab
        except:
          print(f"ERROR-{rid}-{token}-|-{raw_token}-{rr}-{len(raw_token)}")
          print([ord(x) for x in token])
          input("?")

        vocab[token] = rid

    if "added_tokens" in tokenizer:
      for d in tokenizer["added_tokens"]:
        raw_token = d["content"]
        rid = d["id"]
        if not raw_token in vocab:
          vocab[raw_token] = rid

    return vocab

def load_vocab(tokenizer_file):

    vocab = {}

    try:
        with open(tokenizer_file, "r") as fr:
            tokenizer = json.load(fr)
    except json.decoder.JSONDecodeError:
        print(f"Bad tokenizer file: {tokenizer_file}")
        print("Please provide a valid tokenizer file.")
        print("Here are the first few lines of the file:")
        with open(tokenizer_file, "r") as fr:
            for i, line in enumerate(fr):
                print(line)
                if i > 10:
                    break
        sys.exit(1)
    if not "model" in tokenizer:
        if "vocab" in tokenizer:
            tokenizer["model"] = {"vocab": tokenizer["vocab"]}
        if "mama" in tokenizer:
            tokenizer["model"] = {
                "vocab": tokenizer
            }
        with open(tokenizer_file, "w") as fw:
            json.dump(tokenizer, fw, indent=2)

    ### rare case with negative ranks
    if "model" in tokenizer and "vocab" in tokenizer["model"]:
        if isinstance(tokenizer["model"]["vocab"], list):
            print("Bad format for vocab")
            sys.exit(1)
    if not "model" in tokenizer or not "vocab" in tokenizer["model"]:
        print("Bad format for vocab")
        sys.exit(1)
    
    with open(tokenizer_file) as fh:
        text_data = fh.read()

    replacers = [
         ( text_data.count("▁"), "▁"),
         ( text_data.count("Ġ"), "Ġ"),
         ( text_data.count("\u0120"), "\u0120"),
         ( text_data.count("\t"), "\t"),
         ( text_data.count("\u2581"), "\u2581"),
    ]
    replacers.sort()
    replace = replacers[-1][1]
    if replace == "Ġ":
        replace = None
       
        
    should_be_fixed = "ма" not in text_data
    for raw_token, rid, in tqdm(tokenizer["model"]["vocab"].items()):
        
        rr = raw_token
        if replace and raw_token.startswith(replace) and len(raw_token) > 1:
          if should_be_fixed:
            raw_token = "Ġ" + replace.join(raw_token.split(replace)[1:])
          else:
            raw_token = " " + replace.join(raw_token.split(replace)[1:])
            
        if raw_token.lower().startswith("<0x"):
          token = byte_to_char[eval(raw_token[1:-1])]
          vocab[token] = rid
          continue
    
        if should_be_fixed:
          token =  byte_level_decode_custom(raw_token, char_to_byte)
          if [1 for x in token if ord(x) == 65533]:
            token = f"<0y{raw_token}>"
        else:
          if raw_token in char_to_byte:
            token = str(hex(char_to_byte[raw_token])).upper()
          else:
            token = raw_token
        try:
          assert token not in vocab
        except:
          print(f"ERROR-{rid}-{token}-|-{raw_token}-{rr}-{len(raw_token)}")
          print([ord(x) for x in token])
          input("?")

        vocab[token] = rid

    if "added_tokens" in tokenizer:
      for d in tokenizer["added_tokens"]:
        raw_token = d["content"]
        rid = d["id"]
        if not raw_token in vocab:
          vocab[raw_token] = rid

    return vocab