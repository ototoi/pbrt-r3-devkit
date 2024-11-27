import os
import argparse
import glob
from functools import cmp_to_key
import re


def caontains_film(pbrt):
    with open(pbrt, "r") as f:
        lines = f.readlines()
        for line in lines:
            if "Film " in line:
                return True
    return False


def cmp(a, b):
    return (a > b) - (a < b)


def cmp_num(a: str, b: str):
    pat_a = re.search(r"\d+", a)
    pat_b = re.search(r"\d+", b)
    if pat_a and pat_b:
        pre_a = a[: pat_a.start()]
        pre_b = b[: pat_b.start()]
        if pre_a != pre_b:
            return cmp(pre_a, pre_b)
        num_a = int(a[pat_a.start() : pat_a.end()])
        num_b = int(b[pat_b.start() : pat_b.end()])
        if num_a == num_b:
            return cmp_num(a[pat_a.end() :], b[pat_b.end() :])
        return cmp(num_a, num_b)
    return cmp(a, b)


def cmp_path(a: str, b: str):
    dir_a, file_a = os.path.split(a)
    dir_b, file_b = os.path.split(b)
    if dir_a != dir_b:
        return cmp(dir_a, dir_b)
    else:
        return cmp_num(file_a, file_b)


def gather_scenes(scenes_dir):
    scenes_dir = os.path.abspath(scenes_dir)
    images_dir = os.path.join(scenes_dir, "images")

    if not os.path.exists(images_dir):
        return []

    dirs = set()
    paths = glob.glob(os.path.join(images_dir, "*", "*.exr"))
    paths = [path.replace("/images", "") for path in paths]
    for path in paths:
        dirs.add(os.path.split(path)[0])

    paths = []
    for dir in dirs:
        pbrts = glob.glob(os.path.join(dir, "*.pbrt"))
        for pbrt in pbrts:
            if caontains_film(pbrt):
                paths.append(pbrt)

    paths = [os.path.relpath(path, scenes_dir) for path in paths]
    paths = sorted(paths, key=cmp_to_key(cmp_path))

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
        default="./results/scenes.txt",
        help="Output scenes file",
    )
    args = parser.parse_args()
    return process(args)


if __name__ == "__main__":
    exit(main())
