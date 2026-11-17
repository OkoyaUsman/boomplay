# Boomplay Music Downloader

A Python tool to download music from Boomplay. It resolves a Boomplay song URL through Boomplay's encrypted API, fetches the AES-128 key protecting the HLS stream, and uses ffmpeg to decrypt and save the audio as MP3.

## Features

- 🎵 Download music from Boomplay song page URLs (e.g. `https://www.boomplay.com/songs/<slug>`)
- 🔐 Replicates Boomplay's request encryption (AES-128-CBC + Base64 `param` payloads)
- 🔑 Fetches the HLS AES-128 key from the `getKey` endpoint with a properly generated `param` (`requestWay: "hlsAesKey"`)
- 📼 Handles Boomplay's AES-128 encrypted HLS (`.m3u8`) streams via ffmpeg
- 🚀 Lossless output — audio stream is copied untouched (`-c:a copy`), no re-encoding
- 📁 Automatic file organization (saves to `downloads/` directory)

## Requirements

- Python 3.10 or higher
- **ffmpeg** installed and available on `PATH` (with HTTPS support; any recent build works)
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
3. Make sure ffmpeg is installed:
   ```bash
    brew install ffmpeg   # macOS
   ```

## Usage

1. Edit the two constants at the top of `main.py`:
   ```python
    SONG_URL = "https://www.boomplay.com/songs/EQsDqYsdYKIHOAC2EfaGOCHr"  # song page URL
    SONG_ID = "275891736"  # numeric song id (see below)
   ```
   - `SONG_URL` — the Boomplay song page URL. The slug at the end is used to request the stream URL.
   - `SONG_ID` — the **numeric** song ID, required for the key request. The slug cannot be converted to it offline (it is an opaque server-side token), so grab it from the song page HTML: open the page and look for the `data-cid` attribute of the `#songsDetails` div (e.g. via DevTools). The page is behind Cloudflare, which is why the script doesn't scrape it automatically.
2. Run:
   ```bash
    python main.py
   ```
3. The song is saved as `downloads/<slug>.mp3`.

## How It Works

1. **Stream URL request** — the slug from `SONG_URL` is placed in a JSON payload `{"itemID": <slug>, "itemType": "MUSIC"}`, encrypted (AES-128-CBC, PKCS7, Base64) and POSTed as `param` to `https://android.boomplaymusic.com/BoomPlayer/content/resource/encrypt/getResourceAddrV2`. The encrypted `source` field in the response is decrypted to get the `.m3u8` URL (with a `boomplay_token` query signature).
2. **Key request** — the playlist references its key with a relative URI (`/resource/encrypt/getKey`), which actually lives on the API host. A second payload is built from Boomplay's "common params" plus the track:
   ```json
    {
      "channel": "WEB",
      "systemVersionCode": 0,
      "curClientVersionCode": 650,
      "imei": "<generated device id>",
      "isH5": "T",
      "ua": "<browser user agent>",
      "itemID": "<numeric SONG_ID>",
      "itemType": "MUSIC",
      "requestWay": "hlsAesKey"
    }
   ```

    encrypted the same way and sent as `GET /BoomPlayer/resource/encrypt/getKey?param=...&channel=WEB`. The response is the raw 16-byte AES key. The `imei` device ID is generated with the same algorithm the web player uses (`"<n>_" + base36(timestamp) + "_" + base36(random)`, 16 chars); the server accepts any value.
3. **Playlist rewrite** — ffmpeg can't attach custom logic to the key request, so the script downloads the playlist itself, rewrites the key URI to a local `key.bin`, and rewrites the relative `.ts` segment URIs to absolute URLs (`localize_playlist`).
4. **Localhost serving** — ffmpeg refuses `-headers`/custom handling on `file://` playlists, so the rewritten playlist and key are served on an ephemeral `127.0.0.1` port (`serve_dir`).
5. **ffmpeg** — runs with `-c:a copy`: it fetches and decrypts the segments (`crypto+https`) and writes the MP3 without re-encoding (Boomplay's segments already contain MP3 audio).

## Project Structure

```
boomplay/
├── main.py              # Main downloader (song URL -> MP3)
├── requirements.txt     # Python dependencies
├── README.md            # This file
└── downloads/           # Downloaded files (created automatically)
```

## Functions (`main.py`)

### `main()`

Entry point: resolves the stream URL, builds the key request, and runs the playlist/ffmpeg pipeline.

### `extract_boomplay_url_id(url: str) -> str | None`

Extracts the song slug from a Boomplay song URL path.

### `encrypt(plaintext: str) -> str` / `decrypt(base64_ciphertext: str) -> str`

AES-128-CBC (PKCS7) + Base64 helpers matching Boomplay's API scheme. Key: `boomplayVr3xopAM`, IV: `boomplay8xIsKTn9` (both extracted from Boomplay's web bundle).

### `localize_playlist(playlist_url, key_url, tmp, session) -> Path`

Downloads the playlist and the 16-byte key, rewrites the key URI to the local key file and segment URIs to absolute URLs, and writes a local `.m3u8`.

### `serve_dir(directory: Path) -> ThreadingHTTPServer`

Serves a directory on an ephemeral localhost port in a daemon thread (request logging silenced via `QuietHandler`).

### `gen_imei() -> str`

Generates a Boomplay-style device ID (`<digit>_<base36-ms-timestamp>_<base36-random>`, truncated to 16 chars).

## Background: what we learned from Boomplay's web app

- All encrypted API calls follow `param = base64(AES-128-CBC(JSON.stringify(payload)))`; the key/IV are obfuscated in the JS bundle (string array + RC4) but static.
- The `getKey` payload is the player's common params object plus `itemID`, `itemType` and `requestWay: "hlsAesKey"`; the response is the raw 16-byte key, not wrapped/encrypted.
- `.ts` segments on the CDN do **not** require the `boomplay_token` query — only the `.m3u8` does.
- Song slugs (e.g. `EQu_V1RT9H-kxqiUiF4e-UUb`) are opaque: base64url of `0x110b || 16-byte-token` (the constant header is why all song slugs start with `EQ`). The token shows encryption-grade avalanche, so slug → numeric ID conversion is only possible server-side; scrape `data-cid` from the song page instead.

## Troubleshooting

1. **ModuleNotFoundError** — `pip install -r requirements.txt`
2. `ffmpeg: command not found` **/ weird** `cannot execute binary file` **errors** — install ffmpeg (`brew install ffmpeg`) and make sure a real binary is first on `PATH`. (A stale Finder alias at `/usr/local/bin/ffmpeg` can shadow the real one; delete it.)
3. **403 fetching the song page** — expected: Cloudflare protects the HTML pages, which is why `SONG_ID` is hardcoded instead of scraped.
4. **Empty/garbage MP3** — the `boomplay_token` in the stream URL may have expired, or `SONG_ID` doesn't match `SONG_URL`. Get a fresh pair.

## Notes

- The script uses hardcoded AES keys extracted from Boomplay's shipped web code.
- If a track's segments are AAC instead of MP3, change `-c:a copy` in `main.py` to re-encode (e.g. `-c:a libmp3lame -q:a 2`).
- This tool is for educational purposes only. Please respect copyright laws and terms of service.

## License

See the LICENSE file for details.

## Disclaimer

This tool is provided for educational purposes only. Users are responsible for ensuring their use complies with Boomplay's Terms of Service and applicable copyright laws. The authors are not responsible for any misuse of this software.
