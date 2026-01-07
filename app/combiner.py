import os
import subprocess
from concurrent.futures import ProcessPoolExecutor, as_completed
from tqdm import tqdm
import argparse


AUDIO_EXTS = (".mp3", ".wav", ".flac", ".m4a", ".ogg")


def process_album(args):
    """
    Runs ffmpeg to combine the songs, given a folder structure and audio extensions
    """
    folder_path, output_path, folder_name = args

    files = sorted(f for f in os.listdir(folder_path) if f.lower().endswith(AUDIO_EXTS))

    if not files:
        return f"Skipped: {folder_name} (No audio files)"

    # Use first track as metadata + cover-art source
    first_track = os.path.join(folder_path, files[0])

    list_file_path = os.path.join(folder_path, f"list_{folder_name}.txt")
    with open(list_file_path, "w") as f:
        for file in files:
            safe_name = file.replace("'", "'\\''")
            f.write(f"file '{safe_name}'\n")

    cmd = [
        "ffmpeg",
        "-y",
        # Metadata + cover art source
        "-i",
        first_track,
        # Concatenated audio
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        list_file_path,
        # Map audio from concat input
        "-map",
        "1:a",
        # Map cover art if present
        "-map",
        "0:v?",
        # Copy metadata from first track
        "-map_metadata",
        "0",
        # Audio encoding
        "-c:a",
        "aac",
        "-b:a",
        "256k",
        # Preserve cover art
        "-c:v",
        "copy",
        "-disposition:v:0",
        "attached_pic",
        output_path,
    ]

    try:
        subprocess.run(
            cmd,
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT,
        )
        status = "Success"
    except subprocess.CalledProcessError:
        status = "Error"
    finally:
        if os.path.exists(list_file_path):
            os.remove(list_file_path)

    return f"{status}: {folder_name}"


def main(parent_folder):
    """
    Main function to process all the albums
    """
    output_dir = os.path.join(parent_folder, "merged_tracks")
    os.makedirs(output_dir, exist_ok=True)

    tasks = []
    for folder_name in os.listdir(parent_folder):
        folder_path = os.path.join(parent_folder, folder_name)
        if os.path.isdir(folder_path) and folder_name != "merged_tracks":
            output_path = os.path.join(output_dir, f"{folder_name}.m4a")
            tasks.append((folder_path, output_path, folder_name))

    with ProcessPoolExecutor() as executor:
        futures = [executor.submit(process_album, t) for t in tasks]
        for _ in tqdm(
            as_completed(futures),
            total=len(futures),
            desc="Merging Albums",
            unit="album",
        ):
            pass

    print("\nProcessing complete!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-f",
        "--folder",
        default="/Users/smukherjee/Music/HOYO-Instrumental",
        help="Parent music folder",
    )
    args = parser.parse_args()
    main(args.folder)
