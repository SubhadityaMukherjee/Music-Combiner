# Music Combiner

- Combine multiple tracks into a single one while preserving metadata
- I use it to combine multiple tracks from an OST into a single one :)

## Installation

- You need [uv](https://docs.astral.sh/uv/getting-started/installation/)
- You need `ffmpeg`

## Running

- `uv run combiner.py -f <folder path>`
- Folder structure should be like this
  - Main folder
    - Album 1 
      - Song 1.mp3
      - Song 2.mp3
      - ...
    - Album 2
      - Song 1.m4a
      - Song 2.mp3
      - ...
- Files will be saved as Album 1.m4a

