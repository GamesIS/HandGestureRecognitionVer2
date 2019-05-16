def load_poses_names(path_file):
    poses = []
    _file = open(path_file, "r")
    lines = _file.readlines()
    for line in lines:
        line = line.strip()
        if line != "":
            print(line)
            poses.append(line)

    return poses
