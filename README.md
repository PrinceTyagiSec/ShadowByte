# ShadowByte - Advanced Steganography Tool 🕵️‍♂️🔐  

ShadowByte is an advanced Python-based steganography tool designed for securely embedding and extracting encrypted data within PNG images. It is optimized for cybersecurity professionals, forensic analysts, and privacy-conscious users who need secure data hiding techniques.  

## ✨ Features  
✅ **Multi-Layer Steganography** – Securely hide text and files inside PNG images.  
✅ **AES Encryption (Fernet)** – Ensures strong data protection.  
✅ **Brute-Force Attack Module** – Recover encrypted messages using a wordlist attack.  
✅ **Metadata Storage** – Stores filenames inside images for structured recovery.  
✅ **Multi-Threaded Processing** – Speeds up brute-force recovery.  
✅ **Logging & Error Handling** – Provides detailed logs for debugging.  

## 🚀 Installation  

### Clone the Repository  
```bash
git clone  https://github.com/PrinceTyagiSec/ShadowByte.git
cd ShadowByte  
```

### Install Dependencies  
Ensure Python 3.8+ is installed, then install the required dependencies:  
```bash
pip install -r requirements.txt
```

## 🎯 Usage  

### 📌 Command-Line Help  

Run the following command to see available options:  
```bash
python ShadowByte.py -h
```
```
PS C:\Users\Zero\Desktop\Python Projects\Red Team Projects\ShadowByte> python .\ShadowByte.py -h
usage: ShadowByte.py [-h] {encode,decode,bruteforce} ...

Advanced Steganography Tool

positional arguments:
  {encode,decode,bruteforce}
    encode              Encode a message or file into an image
    decode              Extract hidden data from an image
    bruteforce          Try to recover key using a wordlist

options:
  -h, --help            show this help message and exit
```

### 🔹 Encode (Hide Data)  
```bash
python ShadowByte.py encode -h
```
```
PS C:\Users\Zero\Desktop\Python Projects\Red Team Projects\ShadowByte> python .\ShadowByte.py encode -h
usage: ShadowByte.py encode [-h] [--key KEY] [--data DATA] [--output OUTPUT] image_path

positional arguments:
  image_path       Path to the image file

options:
  -h, --help       show this help message and exit
  --key KEY        Custom encryption key (optional for encoding, required for decoding)
  --data DATA      Message or file to encode (required for encoding)
  --output OUTPUT  Output path for the encoded image (required for encoding)
```
Example Usage:
```bash
python ShadowByte.py encode --key "my_secure_key" --data "secret.txt" --output "hidden.png" image.png
```
This encrypts `secret.txt` and embeds it in `image.png`, saving the output as `hidden.png`.  

---

### 🔹 Decode (Extract Data)  
```bash
python ShadowByte.py decode -h
```
```
PS C:\Users\Zero\Desktop\Python Projects\Red Team Projects\ShadowByte> python .\ShadowByte.py decode -h
usage: ShadowByte.py decode [-h] [--key KEY] image_path

positional arguments:
  image_path  Path to the encoded image

options:
  -h, --help  show this help message and exit
  --key KEY   Decryption key (if required)
```
Example Usage:
```bash
python ShadowByte.py decode hidden.png --key "my_secure_key"
```
This extracts and decrypts the hidden file if the correct key is provided.  

---

### 🔹 Brute-Force Attack (Recover Forgotten Keys)  
```bash
python ShadowByte.py bruteforce -h
```
```
PS C:\Users\Zero\Desktop\Python Projects\Red Team Projects\ShadowByte> python .\ShadowByte.py bruteforce -h
usage: ShadowByte.py bruteforce [-h] --wordlist WORDLIST image_path

positional arguments:
  image_path           Path to the encoded image

options:
  -h, --help           show this help message and exit
  --wordlist WORDLIST  Path to the wordlist file
```
Example Usage:
```bash
python ShadowByte.py bruteforce hidden.png --wordlist passwords.txt
```
This tries multiple passwords from `passwords.txt` to recover the hidden data.  

---

## ⏳ Brute-Force Speed Test Results  

We tested brute force using the 100-worst-passwords wordlist. The results show that brute force works fine, but when hiding .png, .mp3, or .mp4 files, the process is significantly slower.

| Hidden Data Type | Time Taken |  
|-----------------|------------|  
| **String**      | **00:05 seconds** |  
| **.txt File**   | **00:05 seconds** |  
| **.mp3 File**   | **14:25 minutes** |  
| **.mp4 File**   | **24:31 minutes** |  
| **.png File**   | **23:18 minutes** |  

📝 **Note:** Brute-force time depends on system specs, wordlist size, and hidden file size. Larger files significantly increase cracking time.  

---

## 🛠️ Requirements  
- Python 3.x  
- `cryptography`
- `Pillow`
- `argparse`
- `base64`
- `concurrent.futures`
- `tqdm`
- `hashlib`
- `chardet`
- `os`
- `threading`
- `logging`
- `stegano`
- `json`

Install dependencies using:  
```bash
pip install -r requirements.txt
```

## ⚠️ Disclaimer  
**ShadowByte** is intended for **educational and ethical** purposes only. Do not use it for illegal activities.  

📜 **License**: MIT License © 2025 **Prince Tyagi**  
👤 **Creator**: [GitHub](https://github.com/PrinceTyagiSec) | [LinkedIn](https://www.linkedin.com/in/prince-tyagi1/)  
