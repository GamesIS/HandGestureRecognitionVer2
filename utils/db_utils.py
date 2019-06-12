import json

import cyrtranslit

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

def sorting_poses(poses):
    latin_poses = []
    for pose in poses:
        latin_poses.append(cyrtranslit.to_latin(pose, 'ru'))
    latin_poses.sort()

    new_poses = []
    for l_pose in latin_poses:
        for pose in poses:
            if(cyrtranslit.to_latin(pose, 'ru') == l_pose):
                new_poses.append(pose)
    return new_poses


def load_json_poses():
    with open(POSES_JSON, 'r', encoding='utf-8') as readFile:
        json_poses = json.load(readFile)
        poses = Poses(json_poses['gestures'], json_poses['group'], json_poses['gestures_group'])
        poses.gestures = sorting_poses(poses.gestures)
        return poses

def get_used_group(groups, gesture_group, poses):
    result = []
    index = 0
    for name in poses:
        group = groups[gesture_group[index]]
        if group not in result:
            result.append(group)
        index += 1
    return result

def get_new_gest_group(groups, unicues_groups, poses, gesture_group):
    index = 0
    for name in poses:
        t = gesture_group[index]
        d = groups[t]
        gesture_group[index] = unicues_groups.index(d)
        index += 1
    return gesture_group

def save_json_poses(object):
    with open("poses_new.json", 'w', encoding='utf-8') as json_file:
        data = json.dumps(object.__dict__, ensure_ascii=False)
        json_file.write(data)


class Poses:
    def __init__(self, gestures, group, gestures_group):
        self.gestures = gestures
        self.group = group
        self.unicues_gesture = get_used_group(group, gestures_group, gestures)
        self.gestures_group = get_new_gest_group(group, self.unicues_gesture, gestures, gestures_group)
        self.group = self.unicues_gesture
