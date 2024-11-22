import os
import argparse
import glob
import subprocess

def process(args):
    input_dir = args.input_dir
    exr_files = glob.glob(os.path.join(input_dir, "**", "*.exr"))
    exr_files = sorted(exr_files)
    print(exr_files)
    for exr_file in exr_files:
        png_file = exr_file.replace(".exr", ".png")
        if not os.path.exists(png_file):
            command = ["convert", exr_file, png_file]
            print(" ".join(command))
            ret = subprocess.run(command, encoding="utf8")
            if ret.returncode != 0:
                print(f"Error: {ret.returncode}")
                return ret.returncode
    return 0

def main():
    parser = argparse.ArgumentParser(description="Convert EXR files to PNG files")
    parser.add_argument("-i", "--input_dir", help="Input directory containing EXR files")
    args = parser.parse_args()
    return process(args)

if __name__ == "__main__":
    exit(main())