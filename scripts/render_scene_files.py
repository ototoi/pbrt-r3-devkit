import os
import sys
import time
import argparse
import datetime
import subprocess


def get_scenes(scenes_dir, input_scenes):
    with open(input_scenes, "r") as f:
        scenes = f.readlines()
        scenes = [scene.strip() for scene in scenes]
        scenes = [os.path.join(scenes_dir, scene) for scene in scenes]
        return scenes


def get_v3_cmd(v3_cmd, input, output):
    return [v3_cmd, input, output]


def get_r3_cmd(r3_cmd, scene):
    return [r3_cmd, "-i", '"{}"'.format(scene)]


def create_task_id():
    now = datetime.datetime.now()
    d = now.strftime("%Y%m%d%H%M")
    return d


def write_command(command, path):
    with open(path, "w") as f:
        f.write(",".join(command) + "\n")


def create_commands(task_dir, scenes, cmd):
    commands = []
    for scene in scenes:
        parent = os.path.basename(os.path.dirname(scene))
        dir = os.path.join(task_dir, parent)
        os.makedirs(dir, exist_ok=True)

        basename = os.path.splitext(os.path.basename(scene))[0]
        comman_file = basename + "_command.txt"
        log_file = basename + "_log.txt"
        time_file = basename + "_time.txt"

        command = [cmd, scene, dir, log_file, time_file]
        
        write_command(command, os.path.join(dir, comman_file))
        commands.append(command)
    return commands


def get_lines(cmd, dir):
    proc = subprocess.Popen(
        cmd,
        encoding="utf8",
        cwd=dir,
        shell=True,
        stdout=subprocess.PIPE,
    )

    while True:
        line = proc.stdout.readline()
        if line:
            yield line

        if not line and proc.poll() is not None:
            break


def execute_commands(task_dir, scenes):
    for scene in scenes:
        parent = os.path.basename(os.path.dirname(scene))
        dir = os.path.join(task_dir, parent)
        comman_file = os.path.splitext(os.path.basename(scene))[0] + "_command.txt"
        with open(os.path.join(dir, comman_file), "r") as f:
            line = f.readlines()
            (cmd, input, working_dir, log_file, time_file) = line[0].strip().split(",")
            cmd = os.path.abspath(cmd)
            input = os.path.abspath(input)
            working_dir = os.path.abspath(working_dir)
            # print(cmd)
            # print(input)
            # print(working_dir)
            # command = command[:2]
            command = [
                "time",
                cmd,
                input,
            ]
            print(f"cd {working_dir}")
            print(" ".join(command))
            print("")
            # ret = subprocess.run(
            #    command, encoding="utf8", cwd=working_dir
            # )
            start = time.time()
            with open(os.path.join(working_dir, log_file), "w") as f:
                for line in get_lines(" ".join(command), working_dir):
                    sys.stdout.write(line)
                    f.write(line)
            end = time.time()
            with open(os.path.join(working_dir, time_file), "w") as f:
                s = str(end - start) + "\n"
                sys.stdout.write("Elapsed:" + s)
                f.write(s)

def process(args):
    scenes_dir = args.scenes_dir
    input_scenes = args.input_scenes
    work_dir = args.work_dir
    v3_cmd = args.v3_cmd
    r3_cmd = args.r3_cmd
    task_id = args.task_id

    scenes = get_scenes(scenes_dir, input_scenes)
    # print(scenes)

    if task_id is None:
        task_id = create_task_id()
    id_dir = os.path.join(work_dir, task_id)
    os.makedirs(id_dir, exist_ok=True)

    create_commands(os.path.join(id_dir, "v3"), scenes, v3_cmd)
    create_commands(os.path.join(id_dir, "r3"), scenes, r3_cmd)

    execute_commands(os.path.join(id_dir, "v3"), scenes)
    execute_commands(os.path.join(id_dir, "r3"), scenes)

    return 0


def main():
    parser = argparse.ArgumentParser(description="Render scene files")
    parser.add_argument(
        "--scenes_dir", default="./pbrt-v3-scenes", help="Scnes directory"
    )
    parser.add_argument(
        "--input_scenes", default="./results/scenes.txt", help="Input scenes file"
    )
    parser.add_argument(
        "--v3-cmd", default="./pbrt-v3/build/pbrt", help="pbrt-v3 command"
    )
    parser.add_argument(
        "--r3-cmd", default="./pbrt-r3/target/release/pbrt-r3", help="pbrt-r3 command"
    )
    parser.add_argument("--work_dir", default="./work", help="Working directory")
    parser.add_argument("--task-id", default=None, help="Task ID")

    args = parser.parse_args()
    return process(args)


if __name__ == "__main__":
    exit(main())
