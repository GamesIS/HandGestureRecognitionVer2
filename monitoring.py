# from multiprocessing import Queue
from queue import Queue

gesture_q = Queue(maxsize=30)
gesture_l = []

def monitoring(predictions, threshold, names, main):
    m_pred = get_max_predictions(predictions, names)
    if m_pred.prediction > threshold:
        if gesture_q.full():
            gesture_l.remove(gesture_q.get())
        gesture_q.put(m_pred)
        gesture_l.append(m_pred)
    else:
        return

    if gesture_q.full():
        calculate_monit(names, main)


def get_max_predictions(predictions, names):
    nb_classes = len(predictions)
    max_prediction = pred_gest(names[0], predictions[0])
    for i in range(nb_classes):
        if max_prediction.prediction < predictions[i]:
            max_prediction = pred_gest(names[i], predictions[i])
    return max_prediction


def calculate_monit(names, main):
    count_names = create_cnt_names(names)
    for cnt_name in count_names:
        for gesture in gesture_l:
            if cnt_name.name == gesture.name:
                cnt_name.count = cnt_name.count + 1
                cnt_name.sum_pred = cnt_name.sum_pred + gesture.prediction

    length_list = len(gesture_l)


    finish_gesture = None

    for cnt_name in count_names:
        cnt_name.calc_avg_prediction()
        cnt_name.calc_abs_ver(length_list)
        if cnt_name.abs_ver > 0.7: #and last_pred.name == cnt_name.name:
            finish_gesture = cnt_name

    if finish_gesture != None:
         gesture_q.queue.clear()
         gesture_l.clear()
    if main.monitor != None:
        main.monitor.fill_table(count_names, finish_gesture)
def create_cnt_names(names):
    count_names = []
    for name in names:
        count_names.append(cnt_names(name))
    return count_names


class pred_gest:
    def __init__(self, name, prediction):
        self.name = name
        self.prediction = prediction


class cnt_names:
    def __init__(self, name):
        self.abs_ver = 0
        self.avg_pred = 0
        self.name = name
        self.count = 0
        self.sum_pred = 0

    def calc_avg_prediction(self):
        if self.count != 0:
            self.avg_pred = self.sum_pred / self.count

    def calc_abs_ver(self, length):
        self.abs_ver = self.count / length