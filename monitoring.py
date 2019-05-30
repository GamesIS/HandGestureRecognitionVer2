# from multiprocessing import Queue
import time
from queue import Queue


class Monitor:
    def __init__(self, general, enable_gesture, queue_size):
        self.general = general
        self.enable_gesture = enable_gesture
        self.gesture_q = Queue(maxsize=queue_size)
        self.gesture_l = []
        self.last_start_time = -1

        self.gesture_general = []
        self.group_general = []

        self.general_gesture_mon = None

    def monitoring(self, predictions, threshold, names, main):
        if self.general:
            self.last_start_time = -1
            if self.general_gesture_mon is None:
                self.general_gesture_mon = gestures(names, main.Gestures.group, main.Gestures.gestures_group)
            elif main.reset_gesture_mon:
                self.general_gesture_mon.reset()
                main.reset_gesture_mon = False
        m_pred = self.get_max_predictions(predictions, names)
        if m_pred.prediction > threshold:
            if self.gesture_q.full():
                self.gesture_l.remove(self.gesture_q.get())
            self.gesture_q.put(m_pred)
            self.gesture_l.append(m_pred)
        else:
            return self.last_start_time

        if self.gesture_q.full():
            self.calculate_monit(names, main)

        return self.last_start_time

    def get_max_predictions(self, predictions, names):
        nb_classes = len(predictions)
        max_prediction = pred_gest(names[0], predictions[0])
        for i in range(nb_classes):
            if max_prediction.prediction < predictions[i]:
                max_prediction = pred_gest(names[i], predictions[i])
        return max_prediction

    def calculate_monit(self, names, main):
        count_names = self.create_cnt_names(names)
        for cnt_name in count_names:
            for gesture in self.gesture_l:
                if cnt_name.name == gesture.name:
                    cnt_name.count = cnt_name.count + 1
                    cnt_name.sum_pred = cnt_name.sum_pred + gesture.prediction

        length_list = len(self.gesture_l)

        finish_gesture = None

        for cnt_name in count_names:
            cnt_name.calc_abs_ver(length_list)
            if cnt_name.abs_ver > 0.7:  # and last_pred.name == cnt_name.name:
                finish_gesture = cnt_name

        if self.general:
            if finish_gesture != None:
                self.general_gesture_mon.addGesture(finish_gesture.name)
                self.general_gesture_mon.fill_tables(main, finish_gesture)
                self.gesture_q.queue.clear()
                self.gesture_l.clear()
                self.last_start_time = 0
            # if main.monitor != None:
            #     main.monitor.fill_table(count_names, finish_gesture)
        else:
            if finish_gesture != None and finish_gesture.name == self.enable_gesture:
                self.gesture_q.queue.clear()
                self.gesture_l.clear()
                self.last_start_time = int(time.time())

    def create_cnt_names(self, names):
        count_names = []
        for name in names:
            count_names.append(cnt_names(name))
        return count_names


class pred_gest:
    def __init__(self, name, prediction):
        self.name = name
        self.prediction = prediction


class gestures:
    def __init__(self, names, groups, gesture_group):
        self.names = names
        self.count_names = [0] * len(names)
        self.groups = groups
        self.count_groups = [0] * len(groups)
        self.gesture_group = gesture_group

        self.all_gesture = 0

    def reset(self):
        self.count_names = [0] * len(self.names)
        self.count_groups = [0] * len(self.groups)
        self.all_gesture = 0

    def addGesture(self, gesture_name):
        for name in self.names:
            if name == gesture_name:
                index = self.names.index(name)
                self.count_names[index] += 1
                self.count_groups[self.gesture_group[index]] += 1
                self.all_gesture += 1
                break
    def fill_tables(self, main, finish_gesture):
        if main.monitor != None:
            main.monitor.fill_general_table(self.names, self.count_names, self.all_gesture, finish_gesture)
            try:
                main.monitor.fill_group_table(self.groups, self.count_groups, self.all_gesture, self.find_group_by_gesture(finish_gesture))
            except Exception as e:
                print(e)

    def find_group_by_gesture(self, gesture):
        index = 0
        for name in self.names:
            if gesture.name == name:
                print(self.groups[self.gesture_group[index]], " self.gesture_group[index] ", self.gesture_group[index], " index ", index)
                return self.groups[self.gesture_group[index]]
            index += 1

class cnt_names:
    def __init__(self, name):
        self.abs_ver = 0
        self.name = name
        self.count = 0
        self.sum_pred = 0

    def calc_abs_ver(self, length):
        self.abs_ver = self.count / length
