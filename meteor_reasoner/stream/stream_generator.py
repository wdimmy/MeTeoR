from meteor_reasoner.stream.utils import *
import time


class Stream_Generator:
    def __init__(self, time_points, Data):
        self.time_points = time_points
        self.streams_data = defaultdict(list)
        for time_point in time_points:
            for predicate in Data:
                for entity, intervals in Data[predicate].items():
                    for interval in intervals:
                        if interval.left_value == time_point:
                            self.streams_data[time_point].append(Atom(predicate, entity))
                            break

    def generator(self, delay=0.001):
        for t in self.time_points:
            yield self.streams_data[t], t

