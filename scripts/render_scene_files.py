import os
import argparse
import datetime

def get_scenes(scenes_dir, input_scenes):
    with open(input_scenes, "r") as f:
        scenes = f.readlines()
        scenes = [scene.strip() for scene in scenes]
        scenes = [os.path.join(scenes_dir, scene) for scene in scenes]
        return scenes
    
def get_v3_cmd(v3_cmd, scene):
    return [v3_cmd, '"{}"'.format(scene)]

def get_r3_cmd(r3_cmd, scene):
    return [r3_cmd, "-i", '"{}"'.format(scene)]

def get_output_dirname():
    now = datetime.datetime.now()
    d = now.strftime("%Y%m%d%H%M")
    return d


def process(args):
    scenes_dir = args.scenes_dir
    input_scenes = args.input_scenes
    work_dir = args.work_dir
    v3_cmd = args.v3_cmd
    r3_cmd = args.r3_cmd

    scenes = get_scenes(scenes_dir, input_scenes)
    #print(scenes)

    v3_cmds = [get_v3_cmd(v3_cmd, scene) for scene in scenes]
    #print(v3_cmds)

    id = get_output_dirname()
    id_dir = os.path.join(work_dir, id)

    os.makedirs(id_dir, exist_ok=True)

    


    
    return 0

def main():
    parser = argparse.ArgumentParser(description="Render scene files")
    parser.add_argument(
        "--scenes_dir", default="./pbrt-v3-scenes", help="Scnes directory"
    )
    parser.add_argument(
        "--input_scenes", default="./results/scenes.txt", help="Input scenes file"
    )
    parser.add_argument("--v3-cmd", default="./pbrt-v3/build/pbrt", help="pbrt-v3 command")
    parser.add_argument("--r3-cmd", default="./pbrt-r3/target/release/pbrt_r3", help="pbrt-r3 command")

    parser.add_argument(
        "--work_dir", default="./work", help="Working directory"
    )

    args = parser.parse_args()
    return process(args)


if __name__ == "__main__":
    exit(main())
