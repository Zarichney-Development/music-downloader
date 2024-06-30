# Music Downloader

This project is a command-line tool for downloading music albums and tracks from YouTube. It uses the MusicBrainz API to fetch album information and YouTube to source the audio.

## Disclaimer

This tool is for educational purposes only. Please respect copyright laws and only download content you have the right to access. The developers of this tool are not responsible for any misuse or legal issues arising from its use.

## Features

- Download individual tracks or entire albums
- Fetch accurate track listings from MusicBrainz
- Search and download high-quality audio from YouTube
- Automatically tag downloaded mp3 files with correct metadata

## Prerequisites

- Python 3.7+
- ffmpeg (for audio conversion)

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/Zarichney-Development/music-downloader.git
   cd music-downloader
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

4. Set up your environment variables:
   Create a `.env` file in the project root and add your API keys:
   ```
   YOUTUBE_API_KEY=your_youtube_api_key
   OPENAI_API_KEY=your_openai_api_key
   ```

## Usage

To interactively download songs:
```
python main.py
````

To download a single song:
```
python main.py -s "Song Title"
```

To download an entire album:
```
python main.py -a "Album Name" --artist "Artist Name"
```

For more options:
```
python main.py --help
```

## Configuration

You can configure default settings in the `config.py` file, including:
- Default download directory
- Maximum retries for API calls
- Concurrent download limit

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
