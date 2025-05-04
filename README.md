# MP3TagEncodeFixer

![Python Version](https://img.shields.io/badge/python-3.12%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

This fixer will help to massively convert latin1 tags that erroneously store strings in local encodings, such as 1251, to the correct version - utf8 or utf16.

## Features

- 🔄 **Batch Processing** - Fix multiple MP3 files at once
- 🛠 **Encoding Detection** - Automatic detection of text encodings
- 📁 **Folder Support** - Process entire directories recursively
- ✅ **ID3v2 Support** - Works with both ID3v2.3 and ID3v2.4 tags
- 🖥 **GUI Interface** - Choose your folder

## Download

Get the latest version from [Releases page](https://github.com/yourusername/MP3TagEncodeFixer/releases)

## Installation

### For End Users (macOS)
1. Download `MP3TagEncodeFixer.dmg` from Releases
2. Open the downloaded file
3. Double click on MP3TagEncodeFixer
4. You will see Apple Warning!
5. Go to  → **System Settings** → **Privacy & Security**
6. Scroll down to "Security" section
7. Click **Open Anyway** next to the warning about MP3TagEncodeFixer

### For Developers
#### Apple still has a broken version of tk in python, so you need to download the latest from https://www.python.org
```bash
# Install requirements
python3 -m pip install mutagen

# Run from source
python3 MP3TagEncodeFixer.py
