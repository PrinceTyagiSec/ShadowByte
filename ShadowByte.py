"""
MIT License

Copyright (c) 2025 Prince Tyagi

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, subject to the conditions in the LICENSE file.

See the LICENSE file for full details.
"""

import time
from PIL import Image
import argparse
import base64
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
import hashlib
import chardet
import os
import threading
import logging
from stegano import lsb
from cryptography.fernet import Fernet
import json

#  Configure logging
logging.basicConfig(
    filename='stegano.log',
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

class Stegano:
    def __init__(self):
        self.stop_event = threading.Event()

    def ensure_png(self, image_path):
        """Checks if the image is PNG. If JPG/JPEG, informs the user to convert it manually."""
        if not image_path.lower().endswith((".png")):
            print("[!] This tool only works with PNG images. Please convert your image to PNG first.")
            return False
        return True  # Returns original if it's already PNG

    def generate_key(self, user_key=None):
        try:
            if user_key:
                key = hashlib.sha256(user_key.encode()).digest()
                key = base64.urlsafe_b64encode(key)
                logging.info("Generated encryption key from user input.")
                return key
            else:
                key = Fernet.generate_key()
                logging.info("Generated random encryption key.")
                return key
        except Exception as e:
            logging.error(f"Error generating key: {e}")
            return None

    def encrypt(self, data, key):
        try:
            f = Fernet(key)
            encrypted_data = f.encrypt(data)
            logging.info("Data successfully encrypted.")
            return encrypted_data
        except Exception as e:
            logging.error(f"Error encrypting data: {e}")
            return None

    def detect_encoding(self, file_path):
        """Detects the encoding of a file."""
        with open(file_path, "rb") as f:
            raw_data = f.read(100000)  # Read first 100KB for detection
        result = chardet.detect(raw_data)
        return result["encoding"] or "latin-1"  # Default to latin-1 if detection fails

    def decrypt(self, encrypted_data, key):

        try:
            f = Fernet(key)
            decrypted_data = f.decrypt(encrypted_data)
            logging.info("Data successfully decrypted.")
            return decrypted_data
        except Exception as e:
            logging.error(f"Error decrypting data: {e}")
            return None

    def encode(self, image_path, input_data, output_path, user_key=None):
        if not self.ensure_png(image_path):
            return  # Exit if image format is not PNG

        key = self.generate_key(user_key)
        if not key:
            logging.error("Invalid key. Please provide a valid key.")
            return

        logging.info(f"Generated Key for Encoding: {key.decode()}")

        if os.path.isfile(input_data):
            # Save the original filename and content
            original_filename = os.path.basename(input_data)
            try:
                with open(input_data, "rb") as file:
                    file_data = file.read()
            except Exception as e:
                logging.error(f"Error reading input file: {e}")
                return

        else:
            original_filename = "message.txt"  # Default filename for text input
            file_data = input_data.encode()

        encrypted_data = self.encrypt(file_data, key)

        # Store the filename and encrypted data as a JSON object
        metadata = json.dumps({"filename": original_filename}).encode()

        # Encode both metadata and file data
        try:
            image = Image.open(image_path)
        except Exception as e:
            logging.error(f"Error opening image file: {e}")
            return

        # Check if the message is too large for the image
        max_message_size = image.width * image.height * 3 // 8  # max size of the message
        message_size = len(encrypted_data) + len(metadata)

        if message_size > max_message_size:
            print(f"Error: The message is too large to be hidden in the image.\n"
                    f"Message size: {message_size} bytes\n"
                    f"Maximum image capacity: {max_message_size} bytes\n"
                    f"Consider using a smaller message or a larger image.")
            return

        else:
            print(f"Message size: {message_size} bytes")

        try:
            separator = b'\x00\x00\x00'
            encoded_data = base64.b64encode(encrypted_data)
            secret_image = lsb.hide(image_path, (encoded_data + separator + metadata).decode())

            secret_image.save(output_path)
            print("Image encoded successfully!")
            print(f"Encryption Key: {key.decode()} (Save this to decode!)")

        except Exception as e:
            logging.error(f"Error encoding data into the image: {e}")

    def decode(self, image_path, user_key,suppress_output=False , output_file=None, from_bruteforce = False):

        if not self.ensure_png(image_path):
            return  # Exit if image format is not PNG

        key = self.generate_key(user_key)
        if not key:
            print("Invalid key. Please provide a valid key.")
            return

        try:
            encrypted_message = lsb.reveal(image_path)

            if encrypted_message:
                separator = b'\x00\x00\x00'  # Ensure it matches the encoding step
                parts = encrypted_message.encode().split(separator)
                if len(parts) < 2:
                    print("Decoding failed: Corrupted message format.")
                    return None
                encrypted_data, metadata = parts

                encrypted_data = base64.b64decode(encrypted_data)
                decrypted_data = self.decrypt(encrypted_data, key)

                # Retrieve the original filename from metadata
                metadata = json.loads(metadata)
                original_filename = metadata.get("filename", "decoded_file")

                # If the original filename was "message.txt", print it instead of saving
                if original_filename == "message.txt":
                    if not suppress_output:
                        print(f"Decoded Message: {decrypted_data.decode()}")
                    return decrypted_data.decode()

                else:
                    # Save to file if it was originally a file
                    output_filename = output_file or original_filename
                    with open(output_filename, "wb") as f:
                        f.write(decrypted_data)

                    if not from_bruteforce:
                        print(f"Decoded data saved to {output_filename}")

                    return output_filename

            else:
                print("No hidden message found!")
        except Exception as e:
            logging.error(f"Decoding failed: {str(e)}")

    def wordlist_generator(self, filepath):
        encoding = self.detect_encoding(filepath)
        try:
            with open(filepath, "r", encoding=encoding) as f:
                for line in f:
                    yield line.strip()  # Generates words one-by-one
        except Exception as e:
            logging.error(f"Error reading wordlist: {e}")

    def bruteforce(self, image_path, wordlist_path, max_threads=None):
        if not self.ensure_png(image_path):
            return

        executor = None
        pbar = None

        try:
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"Image file not found: {image_path}")
            if not os.path.exists(wordlist_path):
                raise FileNotFoundError(f"Wordlist file not found: {wordlist_path}")

            encodings = ['latin-1', 'iso-8859-1', 'cp1252', 'utf-8']

            def read_wordlist():
                """ Generator to yield words one by one instead of loading all at once. """
                for encoding in encodings:
                    try:
                        with open(wordlist_path, "r", encoding=encoding) as file:
                            for line in file:
                                yield line.strip()
                        break
                    except UnicodeDecodeError:
                        continue

            total_words = sum(1 for _ in open(wordlist_path, "r", encoding="latin-1"))
            print(f"Loaded {total_words} words from wordlist.")

            def try_key(word):
                """ Try to decode the image using the given word. """
                if self.stop_event.is_set():
                    return None
                try:
                    message = self.decode(image_path, word, suppress_output=True, from_bruteforce=True)
                    if message:
                        return word, message
                except Exception:
                    pass
                return None

            max_threads = max_threads or max(2, int(os.cpu_count()* 0.70))

            pbar = tqdm(total=total_words, desc="Bruteforcing", unit=" attempts", dynamic_ncols=True, bar_format=('{l_bar}{bar}| Duration: {elapsed} | Speed: {rate_fmt}'))
            executor = ThreadPoolExecutor(max_threads)

            words = read_wordlist()

            futures = {}
            for _ in range(max_threads):
                try:
                    word = next(words)  # ✅ Explicitly assign word first
                    futures[executor.submit(try_key, word)] = word
                except StopIteration:
                    break

            while futures:
                completed = [future for future in futures if future.done()]

                for future in completed:
                    result = future.result()
                    pbar.update(1)
                    if result:
                        key, decoded_message = result
                        pbar.close()
                        if isinstance(decoded_message, str):
                            if os.path.isfile(decoded_message):
                                print(f"Success! Found key: '{key}'")
                                self.decode(image_path, key, suppress_output=False)

                            else:
                                print(f"Success! Found key: '{key}'")
                                print(f"Decoded Message: {decoded_message}")

                        executor.shutdown(wait=False, cancel_futures=True)
                        return decoded_message

                    del futures[future]

                    try:
                        word = next(words)  # ✅ Fetch next word before using
                        new_future = executor.submit(try_key, word)
                        futures[new_future] = word
                    except StopIteration:
                        pass

                time.sleep(0.001)  # 🔥 Reduce CPU spikes

            print("\nBrute force completed: No valid message found.")
            return None

        except KeyboardInterrupt:
            self.stop_event.set()
            if pbar:
                pbar.close()
            print("Brute force interrupted by user. Exiting...")
        finally:
            if executor:
                executor.shutdown(wait=False, cancel_futures=True)
            if pbar:
                pbar.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Advanced Steganography Tool")
    subparsers = parser.add_subparsers(dest="command", required=True)

    stegano = Stegano()

    # Encode subcommand
    encode_parser = subparsers.add_parser("encode", help="Encode a message or file into an image")
    encode_parser.add_argument("--key", help="Custom encryption key (optional for encoding, required for decoding)")
    encode_parser.add_argument("--data", help="Message or file to encode (required for encoding)")
    encode_parser.add_argument("--output", help="Output path for the encoded image (required for encoding)")
    encode_parser.add_argument("image_path", help="Path to the image file")
    encode_parser.set_defaults(func=lambda args: Stegano().encode(args.image_path, args.data, args.output, args.key))

    #  Decode subcommand
    decode_parser = subparsers.add_parser("decode", help="Extract hidden data from an image")
    decode_parser.add_argument("image_path", help="Path to the encoded image")
    decode_parser.add_argument("--key", help="Decryption key (if required)")
    decode_parser.set_defaults(func=lambda args: Stegano().decode(args.image_path, args.key))


    # Bruteforce subcommand
    bruteforce_parser = subparsers.add_parser("bruteforce", help="Try to recover key using a wordlist")
    bruteforce_parser.add_argument("image_path", help="Path to the encoded image")
    bruteforce_parser.add_argument("--wordlist", required=True, help="Path to the wordlist file")
    bruteforce_parser.set_defaults(func=lambda args: Stegano().bruteforce(args.image_path, args.wordlist))

    # Parse Arguments
    args = parser.parse_args()

    # Execute the command
    if hasattr(args, "func"):
        args.func(args)