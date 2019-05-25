import json

POSES_JSON = "poses.json"


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


def load_json_poses():
    with open(POSES_JSON, 'r', encoding='utf-8') as readFile:
        json_poses = json.load(readFile)
        poses = Poses(json_poses['gestures'], json_poses['group'], json_poses['gestures_group'])
        return poses

def save_json_poses(object):
    with open(POSES_JSON, 'w', encoding='utf-8') as json_file:
        data = json.dumps(object.__dict__, ensure_ascii=False)
        json_file.write(data)


class Poses:
    def __init__(self, gestures, group, gestures_group):
        self.gestures = gestures
        self.group = group
        self.gestures_group = gestures_group
