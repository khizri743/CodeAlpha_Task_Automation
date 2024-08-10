import os
import json
import shutil
from subprocess import PIPE, run
import sys

GAME_DIR_PATTERN = "game"
GAME_CODE_EXTENSION = ".go"
GAME_COMPILE_COMMAND = ["go", "build"]

#Find all directory paths that contain the "game" pattern.
def find_all_game_paths(source_dir):
    game_paths = []
    for root, dirs, _ in os.walk(source_dir):
        for directory in dirs:
            if GAME_DIR_PATTERN in directory.lower():
                game_paths.append(os.path.join(root, directory))
        break
    return game_paths

#Extract the directory names from the given paths, removing the specified pattern.
def get_names_from_paths(paths, strip_pattern):
    return [os.path.split(path)[1].replace(strip_pattern, "") for path in paths]

#Create a directory at the given path if it doesn't already exist.
def create_directory(path):
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)


#Copy the source directory to the destination, overwriting the existing content.
def copy_and_overwrite(source, destination):
    if os.path.exists(destination):
        shutil.rmtree(destination)
    shutil.copytree(source, destination)


#Create a JSON metadata file with the provided game names and the number of games.
def make_json_metadata_file(path, game_names):
    data = {
        "gameNames": game_names,
        "numberOfGames": len(game_names)
    }
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

#Compile the Go code in the given directory.
def compile_game_code(path):
    for root, _, files in os.walk(path):
        for file in files:
            if file.endswith(GAME_CODE_EXTENSION):
                command = GAME_COMPILE_COMMAND + [file]
                run_command(command, root)
                return
    print(f"No {GAME_CODE_EXTENSION} file found in {path}")

#Run the specified command in the given directory.
def run_command(command, path):
    cwd = os.getcwd()
    os.chdir(path)
    result = run(command, stdout=PIPE, stdin=PIPE, universal_newlines=True)
    print("Command result:", result)
    os.chdir(cwd)

#Main function that orchestrates the entire process.
def main(source_dir, target_dir):
    source_dir = os.path.abspath(source_dir)
    target_dir = os.path.abspath(target_dir)

    game_paths = find_all_game_paths(source_dir)
    new_game_names = get_names_from_paths(game_paths, "_game")

    create_directory(target_dir)

    for src, dest in zip(game_paths, new_game_names):
        dest_path = os.path.join(target_dir, dest)
        copy_and_overwrite(src, dest_path)
        compile_game_code(dest_path)

    metadata_path = os.path.join(target_dir, "metadata.json")
    make_json_metadata_file(metadata_path, new_game_names)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python script.py <source_dir> <target_dir>")
        sys.exit(1)

    source_dir, target_dir = sys.argv[1:]
    main(source_dir, target_dir)