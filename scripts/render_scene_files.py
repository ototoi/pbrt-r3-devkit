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


def execute_commands(task_dir, scenes, quick, quick_full_resolution):
    for scene in scenes:
        parent = os.path.basename(os.path.dirname(scene))
        dir = os.path.join(task_dir, parent)
        command_file = os.path.splitext(os.path.basename(scene))[0] + "_command.txt"
        with open(os.path.join(dir, command_file), "r") as f:
            line = f.readlines()
            (cmd, input, working_dir, log_file, time_file) = line[0].strip().split(",")
            cmd = os.path.abspath(cmd)
            input = os.path.abspath(input)
            working_dir = os.path.abspath(working_dir)
            output = os.path.join(
                working_dir, os.path.splitext(os.path.basename(input))[0] + ".exr"
            )
            # print(cmd)
            # print(input)
            # print(working_dir)
            # command = command[:2]
            command = [
                "time",
                cmd,
                input,
                "--outfile",
                output,
            ]
            if quick:
                if quick_full_resolution:
                    command.append("--quick-full-resolution")
                else:
                    command.append("--quick")
            if cmd.find("pbrt-r3") >= 0:
                print("pbrt-r3 --no-profile")
                command.append("--no-profile")
            print(f"cd {working_dir}")
            print(" ".join(command))
            print("")
            if os.path.exists(output):
                continue

            # ret = subprocess.run(
            #   command, encoding="utf8", cwd=working_dir
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


def cat_commands(task_dir, scenes):
    for scene in scenes:
        parent = os.path.basename(os.path.dirname(scene))
        dir = os.path.join(task_dir, parent)
        command_file = os.path.splitext(os.path.basename(scene))[0] + "_command.txt"
        with open(os.path.join(dir, command_file), "r") as f:
            line = f.readlines()
            (cmd, input, working_dir, log_file, time_file) = line[0].strip().split(",")
            cmd = os.path.abspath(cmd)
            input = os.path.abspath(input)
            working_dir = os.path.abspath(working_dir)
            output = os.path.join(
                working_dir, os.path.splitext(os.path.basename(input))[0] + ".exr"
            )
            # print(cmd)
            # print(input)
            # print(working_dir)
            # command = command[:2]
            command = ["time", cmd, input, "--cat"]

            ret = subprocess.run(command, encoding="utf8", cwd=working_dir)


def process(args):
    scenes_dir = args.scenes_dir
    input_scenes = args.input_scenes
    work_dir = args.work_dir
    v3_cmd = args.v3_cmd
    r3_cmd = args.r3_cmd
    task_id = args.task_id
    render_target = args.render_target
    quick = args.quick
    quick_full_resolution = args.quick_full_resolution
    if quick_full_resolution:
        quick = True
    is_cat = args.cat

    is_render = {
        "v3": False,
        "r3": False,
    }
    if render_target == "all":
        is_render["v3"] = True
        is_render["r3"] = True
    elif render_target == "v3":
        is_render["v3"] = True
    elif render_target == "r3":
        is_render["r3"] = True

    scenes = get_scenes(scenes_dir, input_scenes)
    # print(scenes)

    if task_id is None:
        task_id = create_task_id()
    id_dir = os.path.join(work_dir, task_id)
    os.makedirs(id_dir, exist_ok=True)

    if is_render["v3"]:
        create_commands(os.path.join(id_dir, "v3"), scenes, v3_cmd)
    if is_render["r3"]:
        create_commands(os.path.join(id_dir, "r3"), scenes, r3_cmd)

    if is_cat:
        if is_render["v3"]:
            cat_commands(os.path.join(id_dir, "v3"), scenes)
        if is_render["r3"]:
            cat_commands(os.path.join(id_dir, "r3"), scenes)
    else:
        if is_render["v3"]:
            execute_commands(os.path.join(id_dir, "v3"), scenes)
        if is_render["r3"]:
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
    parser.add_argument(
        "-t",
        "--render_target",
        default="all",
        choices=["all", "v3", "r3"],
        help="Render target",
    )
    parser.add_argument("-q", "--quick", action="store_true", help="Quick render")
    parser.add_argument(
        "--quick-full-resolution",
        action="store_true",
        help="Quick render with full resolution",
    )
    parser.add_argument("--cat", action="store_true", help="Concatenate output")

    args = parser.parse_args()
    return process(args)


if __name__ == "__main__":
    exit(main())
