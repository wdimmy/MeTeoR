from meteor_reasoner.classes.interval import *


class AutomataWindow:
    def __init__(self, ruler_intervals, ruler_intervals_literals, left_pattern, right_pattern):
        """
        Construct a Window consists of a list of Interval instances and Literal and Atom instances at each Interval instance.
        Args:
            ruler_intervals (list of Interval instances):
            ruler_intervals_literals (dictionary object): the key is the Interval and the value is the set of Literal and Atom instances
            left_pattern:
            right_pattern:
        """
        self.left_pattern = left_pattern
        self.right_pattern = right_pattern
        self.ruler_intervals = ruler_intervals
        self.ruler_intervals_literals = ruler_intervals_literals

    def __eq__(self, other):
        if isinstance(other, AutomataWindow):
            self_interval_len = [str(item.right_value - item.left_value) for item in self.ruler_intervals]
            other_interval_len = [str(item.right_value - item.left_value) for item in other.ruler_intervals]

            if self_interval_len != other_interval_len:
                return False

            self_interval_literal_str = []
            for i, ruler_interval in enumerate(self.ruler_intervals):
                tmp = []
                for literal in self.ruler_intervals_literals[ruler_interval]:
                    tmp.append(str(i) + str(literal))
                tmp.sort()
                self_interval_literal_str.append("#".join(tmp))

            other_interval_literal_str = []
            for i, ruler_interval in enumerate(other.ruler_intervals):
                tmp = []
                for literal in other.ruler_intervals_literals[ruler_interval]:
                    tmp.append(str(i) + str(literal))
                tmp.sort()
                other_interval_literal_str.append("#".join(tmp))

            if "$".join(self_interval_literal_str) == "$".join(other_interval_literal_str):
                return True
            else:
                return False

        return False

    def __str__(self):
       interval_len = [str(item.right_value - item.left_value) for item in self.ruler_intervals]
       interval_literal_str = []
       for i, ruler_interval in enumerate(self.ruler_intervals):
          tmp = []
          for literal in self.ruler_intervals_literals[ruler_interval]:
             tmp.append(str(i) + str(literal))
          tmp.sort()
          interval_literal_str.append("#".join(tmp))
       return "#".join(interval_len) + "$".join(interval_literal_str)

    def __hash__(self):
       interval_len = [str(item.right_value - item.left_value) for item in self.ruler_intervals]
       interval_literal_str = []
       for i, ruler_interval in enumerate(self.ruler_intervals):
          tmp = []
          for literal in self.ruler_intervals_literals[ruler_interval]:
             tmp.append(str(i) + str(literal))
          tmp.sort()
          interval_literal_str.append("#".join(tmp))
       return hash("#".join(interval_len) + "$".join(interval_literal_str))


    def remove_the_most_right_ruler_interval(self):
       the_most_right_ruler_interval = self.ruler_intervals[-1]
       del self.ruler_intervals_literals[the_most_right_ruler_interval]
       del self.ruler_intervals[-1]


    def remove_the_most_left_ruler_interval(self):
       the_most_left_ruler_interval = self.ruler_intervals[0]
       del self.ruler_intervals_literals[the_most_left_ruler_interval]
       del self.ruler_intervals[0]

    def move_left(self, subset_literal=[]):
       try:
          the_most_left_ruler_interval = self.ruler_intervals[0]
       except:
           print("debug")
       if the_most_left_ruler_interval.left_open:
          new_ruler_interval = Interval(the_most_left_ruler_interval.left_value, the_most_left_ruler_interval.left_value, False, False)
          self.ruler_intervals.insert(0, new_ruler_interval)
          self.ruler_intervals_literals[new_ruler_interval] = subset_literal
          self.remove_the_most_right_ruler_interval()

       else:
         # count the non-punctual ruler interval
         cnt = 0
         ruler_interval_len = []
         for i in range(len(self.ruler_intervals)):
            if self.ruler_intervals[i].left_open:
               ruler_interval_len.append(str(abs(self.ruler_intervals[i].right_value - self.ruler_intervals[i].left_value)))
               cnt += 1
            if cnt >= len(self.left_pattern):
               break

         while True:
            tmp_pattern = "#".join(ruler_interval_len)
            if tmp_pattern in self.left_pattern:
               next_ruler_interval_len = self.left_pattern[tmp_pattern]
               current_the_most_left_ruler_interval = self.ruler_intervals[0]
               new_ruler_interval = (Interval(current_the_most_left_ruler_interval.left_value - next_ruler_interval_len, current_the_most_left_ruler_interval.right_value, True, True))
               self.ruler_intervals.insert(0, new_ruler_interval)
               self.ruler_intervals_literals[new_ruler_interval] = subset_literal
               self.remove_the_most_right_ruler_interval()
               break
            del ruler_interval_len[-1]

    def move_right(self, subset_literal=[]):
      the_most_right_ruler_interval = self.ruler_intervals[-1]
      if the_most_right_ruler_interval.right_open:
         new_ruler_interval = Interval(the_most_right_ruler_interval.right_value, the_most_right_ruler_interval.right_value, False, False)
         self.ruler_intervals.append(new_ruler_interval)
         self.ruler_intervals_literals[new_ruler_interval] = subset_literal
         self.remove_the_most_left_ruler_interval()

      else:
         cnt = 0
         ruler_interval_len = []
         for i in range(len(self.ruler_intervals)):
            if self.ruler_intervals[i].left_open:
               ruler_interval_len.append(str(abs(self.ruler_intervals[i].right_value - self.ruler_intervals[i].left_value)))
               cnt += 1
            if cnt >= len(self.right_pattern):
               break

         while True:
            tmp_pattern = "#".join(ruler_interval_len)
            if tmp_pattern in self.right_pattern:
               next_ruler_interval_len = self.right_pattern[tmp_pattern]
               current_the_most_right_ruler_interval = self.ruler_intervals[-1]
               new_ruler_interval = Interval(current_the_most_right_ruler_interval.left_value, current_the_most_right_ruler_interval.left_value + next_ruler_interval_len, True, True)
               self.ruler_intervals.append(new_ruler_interval)
               self.ruler_intervals_literals[new_ruler_interval] = subset_literal
               self.remove_the_most_left_ruler_interval()
               break

            del ruler_interval_len[0]
