import os
import argparse
import glob
import shutil


def gather_scenes(scenes_dir):
    scenes_dir = os.path.abspath(scenes_dir)
    images_dir = os.path.join(scenes_dir, "images")

    if not os.path.exists(images_dir):
        return []
    paths = glob.glob(os.path.join(images_dir, "*", "*.exr"))
    paths = [path.replace("/images", "") for path in paths]
    paths = [path.replace(".exr", ".pbrt") for path in paths]
    paths = [os.path.relpath(path, scenes_dir) for path in paths]
        
    paths = sorted(paths)

    return paths

def write_scenes(scenes, output_scenes):
    os.makedirs(os.path.dirname(output_scenes), exist_ok=True)
    with open(output_scenes, "w") as f:
        for scene in scenes:
            f.write(scene + "\n")


def process(args):
    scenes_dir = args.scenes_dir
    output_scenes = args.output_scenes

    scenes = gather_scenes(scenes_dir)
    print("Found {} scenes".format(len(scenes)))
    write_scenes(scenes, output_scenes)

    return 0


def main():
    print("Gathering scene files...")
    parser = argparse.ArgumentParser(description="Gather scene files")
    parser.add_argument(
        "--scenes_dir", default="./pbrt-v3-scenes", help="Scnes directory"
    )
    parser.add_argument(
        "-o",
        "--output_scenes",
        default="./work/scenes.txt",
        help="Output scenes file",
    )
    args = parser.parse_args()
    return process(args)


if __name__ == "__main__":
    exit(main())
