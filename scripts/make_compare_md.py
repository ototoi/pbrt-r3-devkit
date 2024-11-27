import os
import glob
import argparse

def make_md_files(output_dir, dirs):
    keys = sorted(list(dirs.keys()))
    for dirname in keys:
        md_file = os.path.join(output_dir, f"{dirname}.md")
        with open(md_file, "w") as f:
            f.write(f"# {dirname}\n")
            paths = dirs[dirname]
            for path in paths:
                basename = os.path.basename(path)
                basename_no_ext = os.path.splitext(basename)[0]
                f.write(f"## {basename_no_ext}\n")
                f.write("|pbrt-v3|pbrt-r3|" + "\n")
                f.write("|---|---|" + "\n")
                f.write(f"|![{basename}](../v3/{dirname}/{basename})|![{basename}](../r3/{dirname}/{basename})|" + "\n")
    index_md_file = os.path.join(output_dir, "index.md")
    with open(index_md_file, "w") as f:
        f.write("# pbrt-v3 / pbrt-r3\n")
        for dirname in keys:
            f.write(f"- [{dirname}](./{dirname}.md)\n")
    gallery_md_file = os.path.join(output_dir, "gallery.md")
    with open(gallery_md_file, "w") as f:
        f.write("# Gallery\n")
        for dirname in keys:
            f.write(f"## {dirname}\n")
            paths = dirs[dirname]
            for path in paths:
                basename = os.path.basename(path)
                basename_no_ext = os.path.splitext(basename)[0]
                f.write(f"### {basename_no_ext}\n")
                f.write("|pbrt-v3|pbrt-r3|" + "\n")
                f.write("|---|---|" + "\n")
                f.write(f"|![{basename}](../v3/{dirname}/{basename})|![{basename}](../r3/{dirname}/{basename})|" + "\n")

    return 0

def process(args):
    input_dir = args.input_dir
    output_dir = args.output_dir
    scenes_txt = args.scenes
    with open(scenes_txt, "r") as f:
        scenes = f.readlines()
    files = [os.path.join(input_dir, "v3", scene.replace(".pbrt", ".jpg").strip()) for scene in scenes]
    dirs = {}
    for path in files:
        dirname = os.path.split(os.path.dirname(path))[1]
        if dirname not in dirs:
            dirs[dirname] = []
        dirs[dirname].append(path)
    return make_md_files(output_dir, dirs)

def main():
    parser = argparse.ArgumentParser(description="Create markdown files for comparing pbrt-v3 and pbrt-r3")
    parser.add_argument("-s", "--scenes", default="./results/scenes.txt", help="Scenes file")
    parser.add_argument("-i", "--input_dir", default="./results/", help="Input directory containing Jpeg files")
    parser.add_argument("-o", "--output_dir", default="./results/md", help="Output directory for markdown files")
    args = parser.parse_args()
    return process(args)

if __name__ == "__main__":
    exit(main())