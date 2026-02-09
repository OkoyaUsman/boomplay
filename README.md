# Boomplay Music Downloader

A Python command-line tool to download music from Boomplay. This script extracts song information from Boomplay URLs, communicates with the Boomplay API using encrypted requests, and downloads the audio files to your local machine.

## Features

- 🎵 Download music from Boomplay by providing a song URL
- 🔐 Automatic encryption/decryption of API requests using AES-128-CBC
- 📁 Automatic file organization (saves to `downloads/` directory)
- ✅ URL validation to ensure only valid Boomplay song URLs are processed
- 🎯 Simple command-line interface

## Requirements

- Python 3.7 or higher
- Internet connection

## Installation

1. Clone this repository or download the source code:
   ```bash
   git clone https://github.com/OkoyaUsman/boomplay.git
   cd boomplay
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Basic Usage

Run the script with a Boomplay song URL:

```bash
python main.py <boomplay_song_url>
```

### Example

```bash
python main.py https://www.boomplay.com/songs/12345678
```

The script will:
1. Validate the URL
2. Extract the song ID
3. Request the music resource from Boomplay's API
4. Download the audio file
5. Save it to the `downloads/` directory with the song ID as the filename

### Output

Downloaded files are saved in the `downloads/` directory with the format:
```
downloads/<song_id>.<extension>
```

For example, if the song ID is `12345678` and the file is an MP3, it will be saved as:
```
downloads/12345678.mp3
```

## How It Works

1. **URL Validation**: The script validates that the provided URL is a valid Boomplay song URL (must be from `boomplay.com` and contain a `/songs/` path with a numeric song ID).

2. **Song ID Extraction**: Extracts the numeric song ID from the URL path (e.g., `12345678` from `https://www.boomplay.com/songs/12345678`).

3. **API Request Encryption**: 
   - Creates a JSON payload with the song ID and item type
   - Encrypts the payload using AES-128-CBC encryption with a predefined key and IV
   - Base64 encodes the encrypted data

4. **Resource Retrieval**: 
   - Sends the encrypted request to `https://www.boomplay.com/getResourceAddr`
   - Receives an encrypted response containing the actual music file URL
   - Decrypts the response to get the music URL

5. **File Download**: 
   - Downloads the audio file from the decrypted URL
   - Determines the file extension from the URL
   - Saves the file to the `downloads/` directory

## Project Structure

```
boomplay/
├── main.py              # Main script file
├── requirements.txt     # Python dependencies
├── README.md           # This file
└── downloads/          # Directory where downloaded files are saved (created automatically)
```

## Functions

### `main()`
Main entry point that orchestrates the download process.

### `boomplay_url(value: str) -> str`
Validates that the provided URL is a valid Boomplay URL. Raises `ArgumentTypeError` if validation fails.

### `extract_boomplay_song_id(url: str) -> str | None`
Extracts the numeric song ID from a Boomplay song URL. Returns `None` if the URL format is invalid.

### `encrypt(plaintext: str) -> str`
Encrypts a plaintext string using AES-128-CBC encryption and returns a base64-encoded string.

### `decrypt(base64_ciphertext: str) -> str`
Decrypts a base64-encoded ciphertext string using AES-128-CBC decryption and returns the plaintext.

## Error Handling

The script includes error handling for:
- Invalid URLs
- Network errors
- API response errors
- File I/O errors

If an error occurs, the script will print an error message and exit gracefully.

## Notes

- The script uses hardcoded AES encryption keys that are specific to Boomplay's API
- The `downloads/` directory is created automatically if it doesn't exist
- The script preserves the original file extension from the music URL
- This tool is for educational purposes only. Please respect copyright laws and terms of service

## Troubleshooting

### Common Issues

1. **ModuleNotFoundError**: Make sure you've installed all dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. **Invalid URL Error**: Ensure the URL follows the format:
   ```
   https://www.boomplay.com/songs/<numeric_id>
   ```

3. **Download Fails**: 
   - Check your internet connection
   - Verify the song URL is still valid
   - The Boomplay API may have changed, open an issue

## License

See the LICENSE file for details.

## Disclaimer

This tool is provided for educational purposes only. Users are responsible for ensuring their use complies with Boomplay's Terms of Service and applicable copyright laws. The authors are not responsible for any misuse of this software.