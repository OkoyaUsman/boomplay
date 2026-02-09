import os
import json
import base64
import argparse
import curl_cffi
import urllib.parse
from pathlib import Path
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

AES_KEY = b"boomplayVr3xopAM"
IV_KEY = b"boomplay8xIsKTn9"

def main():
    output_dir = Path("downloads")
    output_dir.mkdir(parents=True, exist_ok=True)
    parser = argparse.ArgumentParser("Download music from Boomplay")
    parser.add_argument("url", type=boomplay_url, help="The URL of the music to download")
    args = parser.parse_args()
    song = extract_boomplay_song_id(args.url)
    if not song:
        print(f"Invalid music URL: {args.url}")
        return
    try:
        encrypted = encrypt(json.dumps({"itemID": song, "itemType": "MUSIC"}))
        music_response = curl_cffi.post("https://www.boomplay.com/getResourceAddr", data={"param": encrypted}).json()
        music_url = decrypt(music_response["source"])
        audio_response = curl_cffi.get(music_url, headers={"x-boomplay-ref": "Boomplay_WEBV1"}).content
        extension = os.path.splitext(urllib.parse.urlparse(music_url).path)[1]
        filename = song + extension
        output_file = output_dir / filename
        with open(output_file, "wb") as f:
            f.write(audio_response)
        print(f"Downloaded music to {output_file}")
    except Exception as e:
        print(f"Error occured: {e}")

def boomplay_url(value: str) -> str:
    parsed = urllib.parse.urlparse(value)
    if parsed.scheme not in {"http", "https"}:
        raise argparse.ArgumentTypeError("URL must start with http:// or https://")
    if not parsed.netloc:
        raise argparse.ArgumentTypeError("Invalid URL")
    domain = parsed.netloc.lower()
    if domain.startswith("www."):
        domain = domain[4:]
    if domain != "boomplay.com":
        raise argparse.ArgumentTypeError("URL must be from boomplay.com")
    if not parsed.path or parsed.path == "/":
        raise argparse.ArgumentTypeError("Boomplay URL must contain a path")
    return value

def extract_boomplay_song_id(url: str) -> str | None:
    path_parts = urllib.parse.urlparse(url).path.strip("/").split("/")
    if len(path_parts) >= 2 and path_parts[0] == "songs":
        song_id = path_parts[1]
        if song_id.isdigit():
            return song_id
    return None

def encrypt(plaintext: str) -> str:
    plaintext_bytes = plaintext.encode('utf-8')
    padded = pad(plaintext_bytes, AES.block_size)
    cipher = AES.new(AES_KEY, AES.MODE_CBC, iv=IV_KEY)
    ciphertext = cipher.encrypt(padded)
    return base64.b64encode(ciphertext).decode('utf-8')

def decrypt(base64_ciphertext: str) -> str:
    ciphertext = base64.b64decode(base64_ciphertext)
    cipher = AES.new(AES_KEY, AES.MODE_CBC, iv=IV_KEY)
    padded_plaintext = cipher.decrypt(ciphertext)
    plaintext_bytes = unpad(padded_plaintext, AES.block_size)
    return plaintext_bytes.decode('utf-8')

if __name__ == "__main__":
    main()