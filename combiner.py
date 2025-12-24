import os
import subprocess
from concurrent.futures import ProcessPoolExecutor, as_completed
from tqdm import tqdm
import argparse


def process_album(args):
    """Worker function to process a single folder"""
    folder_path, output_path, folder_name = args

    audio_extensions = (".mp3", ".wav", ".flac", ".m4a", ".ogg")
    files = sorted(
        [f for f in os.listdir(folder_path) if f.lower().endswith(audio_extensions)]
    )

    if not files:
        return f"Skipped: {folder_name} (No files)"

    list_file_path = os.path.join(folder_path, f"list_{folder_name}.txt")
    with open(list_file_path, "w") as f:
        for file in files:
            safe_name = file.replace("'", "'\\''")
            f.write(f"file '{safe_name}'\n")

    cmd = [
        "ffmpeg",
        "-y",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        list_file_path,
        "-c:a",
        "aac",
        "-b:a",
        "256k",
        "-map_metadata",
        "0",
        output_path,
    ]

    try:
        # We suppress output so it doesn't break the progress bar layout
        subprocess.run(
            cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT
        )
        status = "Success"
    except subprocess.CalledProcessError:
        status = "Error"
    finally:
        if os.path.exists(list_file_path):
            os.remove(list_file_path)

    return f"{status}: {folder_name}"


def main(parent_folder):
    output_dir = os.path.join(parent_folder, "merged_tracks")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    tasks = []
    for folder_name in os.listdir(parent_folder):
        folder_path = os.path.join(parent_folder, folder_name)
        if os.path.isdir(folder_path) and folder_name != "merged_tracks":
            output_path = os.path.join(output_dir, f"{folder_name}.m4a")
            tasks.append((folder_path, output_path, folder_name))

    # tqdm creates the visual bar
    # total=len(tasks) tells it how many items to expect
    with ProcessPoolExecutor() as executor:
        futures = [executor.submit(process_album, task) for task in tasks]

        # as_completed yields a future as soon as it's done
        for _ in tqdm(
            as_completed(futures), total=len(tasks), desc="Merging Albums", unit="album"
        ):
            pass

    print("\nProcessing complete!")


if __name__ == "__main__":
    ags = argparse.ArgumentParser()
    ags.add_argument("-f", help="Folder", default="/Users/smukherjee/Music/HOYO/")
    args = ags.parse_args()
    main(args.f)
