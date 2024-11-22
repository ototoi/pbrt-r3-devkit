import os
import argparse
import glob
import subprocess

def process(args):
    input_dir = args.input_dir
    force = args.force
    png_files = glob.glob(os.path.join(input_dir, "**", "*.png"))
    png_files = sorted(png_files)
    print(png_files)
    for png_file in png_files:
        jpg_file = png_file.replace(".png", ".jpg")
        if force or not os.path.exists(jpg_file):
            command = ["magick", png_file, jpg_file]
            print(" ".join(command))
            ret = subprocess.run(command, encoding="utf8")
            if ret.returncode != 0:
                print(f"Error: {ret.returncode}")
                return ret.returncode
    return 0

def main():
    parser = argparse.ArgumentParser(description="Convert PNG files to JPG files")
    parser.add_argument("-i", "--input_dir", help="Input directory containing EXR files")
    parser.add_argument("-f", "--force", action="store_true", help="Force conversion even if PNG file exists")
    args = parser.parse_args()
    return process(args)

if __name__ == "__main__":
    exit(main())