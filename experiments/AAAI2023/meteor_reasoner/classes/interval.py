import decimal


def coalescing(old_intervals):
    if len(old_intervals) == 0:
        return old_intervals
    new_intervals = []
    old_intervals = sorted(old_intervals, key=lambda t: (t.left_value, t.left_open))
    i = 1
    mover = old_intervals[0]
    while i <= len(old_intervals)-1:
        tmp_interval = Interval.union(mover, old_intervals[i])
        if tmp_interval is None:
            # no intersection
            new_intervals.append(mover)
            mover = old_intervals[i]
        else:
            mover = tmp_interval
        i += 1
    new_intervals.append(mover)
    return new_intervals

class Interval:
    def __init__(self, left_value, right_value, left_open, right_open):
        """
        An interval consists of four parts.

        Args:
            left_value (Decimal):
            right_value (Decimal):
            left_open (boolean):  True denotes open and vice versa.
            right_open (boolean): True denotes open and vice versa.
        """
        if left_value == right_value and (left_open is False or right_open is False):
            self.left_open, self.right_open = False, False
        else:
            self.left_open = left_open
            self.right_open = right_open
        self.left_value = left_value
        self.right_value = right_value

    @staticmethod
    def list_union(intervals1, intervals2):
        intervals1.sort(key=lambda k: k.left_value)
        intervals2.sort(key=lambda k: k.left_value)
        new_interval_list = []
        if intervals1[0].left_value < intervals2[0].left_value:
            for interval1 in intervals1:
                for interval2 in intervals2:
                    if interval2.left_value > interval1.right_value:
                        break
                    tmp_interval = Interval.intersection(interval1, interval2)
                    if tmp_interval is not None:
                        new_interval_list.append(tmp_interval)
        else:
            for interval1 in intervals2:
                for interval2 in intervals1:
                    if interval2.left_value > interval1.right_value:
                        break
                    tmp_interval = Interval.intersection(interval1, interval2)
                    if tmp_interval is not None:
                        new_interval_list.append(tmp_interval)
        return new_interval_list

    @staticmethod
    def list_inclusion(intervals1, intervals2):
        """
        Judege whether the list of intervals(intervals1) is included by the list of intervals (intervals2)
        Args:
            intervals1: the list of intervals
            intervals2: the list of intervals

        Returns: boolean

        """
        for interval1 in intervals1:
            for interval2 in intervals2:
               if not Interval.inclusion(interval1, interval2):
                    continue
               else:
                   break
            else:
                return False

        return True

    @staticmethod
    def compare(intervals1, intervals2):
        """
        Compare two interval lists to see whether they are equal
        Args:
            intervals1 (list of Interval instances):
            intervals2 (list of Intervals instances):

        Returns:
            True or False
        """
        intervals1.sort(key=lambda item: item.left_value)
        intervals2.sort(key=lambda item: item.left_value)
        if len(intervals1) != len(intervals2):
            return False
        else:
            for v1, v2 in zip(intervals1, intervals2):
                if v1 != v2:
                    return False
            else:
                return True

    @staticmethod
    def diff(interval_src, interval_list):
        res = []
        for interval in interval_list:
            if Interval.inclusion(interval_src, interval):
                # [3,4], [[3,5],[7,10]]
                return res
            elif Interval.inclusion(interval, interval_src):
                if interval_src == interval:
                    return res

                # [2,10], [[3,5],[6,8],[9.5,10]
                if interval_src.left_value < interval.left_value:
                    res.append(Interval(interval_src.left_value, interval.left_value,
                                        interval_src.left_open, not interval.left_open))
                elif interval_src.left_value == interval.left_value and not interval_src.left_open \
                        and interval.left_open:
                    res.append(Interval(interval_src.left_value, interval.left_value,
                                        False, False))
                if interval_src.right_value == interval.right_value:
                    if interval_src.right_open == interval.right_open:
                         return res
                    elif not interval_src.right_open and interval.right_open:
                         interval_src = Interval(interval_src.right_value, interval_src.right_value,
                                                 interval_src.right_open, interval.right_open)
                    else:
                         return res
                else:
                    interval_src = Interval(interval.right_value, interval_src.right_value,
                                                not interval.right_open, interval_src.right_open)

            elif not Interval.intersection(interval, interval_src) and \
                    interval_src.right_value <= interval.left_value:
                    # [1,2], [[3,5], [7,10]
                    res.append(interval_src)
                    return res

            elif Interval.intersection(interval, interval_src):
                 # [3,5], [[4, 8]]
                 intersection_part = Interval.intersection(interval_src, interval)

                 if interval_src.right_value >= interval.right_value:
                     interval_src = Interval(intersection_part.right_value, interval_src.right_value,
                                             not intersection_part.right_open, interval_src.right_open)

                 else:
                     res.append(Interval(interval_src.left_value, intersection_part.left_value,
                                         interval_src.left_open, not intersection_part.left_open))
                     return res

        res.append(interval_src)
        return res

    @staticmethod
    def diff_list(t1_list, t2_list):
        """
        Return the different part of two interval lists
        Args:
            t1_list: a list of Intervals
            t2_list: a list of Intervals

        Returns: a list of Intervals

        """
        t1_list = coalescing(t1_list)
        t2_list = coalescing(t2_list)
        if len(t2_list) == 0:
            return t1_list

        res = []
        for interval1 in t1_list:
            mover = interval1
            for interval2 in t2_list:
                if mover.left_value == interval2.left_value and mover.left_open is False and interval2.left_open:
                    res.append(Interval(mover.left_value, mover.left_value, False, False))
                elif mover.left_value < interval2.left_value:
                    if mover.right_value < interval2.left_value:
                        res.append(Interval(mover.left_value, mover.right_value, mover.left_open, mover.right_open))
                        break
                    else:
                        res.append(Interval(mover.left_value, interval2.left_value, mover.left_open, not interval2.left_open))
                if Interval.inclusion(mover, interval2):
                    mover = None
                    break
                elif Interval.intersection(mover, interval2) is None:
                    continue
                else:
                    intersect = Interval.intersection(mover, interval2)
                    if intersect.right_value == mover.right_value and mover.right_open:
                        mover = None
                    else:
                        mover = Interval(intersect.right_value, mover.right_value, not intersect.right_open, mover.right_open)

            if mover is not None:
                  res.append(mover)
        res = coalescing(res)
        return res


    @staticmethod
    def union(v1, v2):
        """
        Return the union of v1 and v2 if v1 and v2 have an intersection part, else return None.
        Args:
            v1 (an Interval instance):
            v2 (an Interval instance):

        Returns:
            None or a newly-created interval instance
        """
        if v1.left_value > v2.left_value:
            v1, v2 = v2, v1

        if v1.left_value == v2.left_value:
            left_value = v1.left_value
            if v1.left_open != v2.left_open:
                left_open = False
            else:
                left_open = v1.left_open

            right_value = max(v1.right_value, v2.right_value)
            if v1.right_value == v2.right_value and v1.right_open != v2.right_open:
                right_open = False
            else:
                if v1.right_value == right_value:
                    right_open = v1.right_open
                else:
                    right_open = v2.right_open

            return Interval(left_value, right_value, left_open, right_open)

        elif v2.left_value == v1.right_value and v2.left_open and v1.right_open:
            return None

        else:
            if v2.left_value <= v1.right_value:
                left_value = v1.left_value
                left_open = v1.left_open
                right_value = max(v1.right_value, v2.right_value)
                if v1.right_value == v2.right_value and v1.right_open != v2.right_open:
                    right_open = False
                else:
                    if v1.right_value == right_value:
                        right_open = v1.right_open
                    else:
                        right_open = v2.right_open

                return Interval(left_value, right_value, left_open, right_open)
            else:
                return None

    @staticmethod
    def inclusion(v1, v2):
        if v1.left_value < v2.left_value or v1.right_value > v2.right_value:
            return False
        else:
            if v1.left_value == v2.left_value and v2.left_open and not v1.left_open:
                return False
            elif v1.right_value == v2.right_value and v2.right_open and not v1.right_open:
                return False
            else:
                return True

    @staticmethod
    def intersection(v1, v2):
        """
        Return the intersection of v1 and v2
        Args:
            v1 (an Interval instance):
            v2 (an Interval instance):

        Returns:
            None or a newly-created interval instance
        """
        if v1.left_value > v2.left_value:
            left_value = v1.left_value
            left_open = v1.left_open

        elif v1.left_value < v2.left_value:
            left_value = v2.left_value
            left_open = v2.left_open
        else:
            left_value = v2.left_value
            if v1.left_open != v2.left_open:
                left_open = True
            else:
                left_open = v2.left_open

        if v1.right_value < v2.right_value:
            right_value = v1.right_value
            right_open = v1.right_open
        elif v1.right_value > v2.right_value:
            right_value = v2.right_value
            right_open = v2.right_open
        else:
            right_value = v2.right_value
            if v1.right_open != v2.right_open:
                right_open =True
            else:
                right_open = v2.right_open

        if not Interval.is_valid_interval(left_value, right_value, left_open, right_open):
            return None
        else:
            return Interval(left_value, right_value, left_open, right_open)

    @staticmethod
    def is_valid_interval(left_value, right_value, left_open, right_open):
        """
        Check whether the given four values can form a valid Interval.
        Args:
            left_value (float):
            right_value (float):
            left_open (boolean):
            right_open (boolean):

        Returns:
            boolean
        """
        if left_value == right_value and left_open and right_open:
            return False
        elif left_value > right_value:
            return False
        elif left_value in [decimal.Decimal("-inf"), decimal.Decimal("inf")] and not left_open:
            return False
        elif right_value in [decimal.Decimal("-inf"), decimal.Decimal("inf")] and not right_open:
            return False
        elif left_value == right_value and left_open != right_open:
            return False

        return True

    def __str__(self):
        str_output = ""
        if self.left_open:
            str_output += "("
        else:
            str_output += "["
        if self.left_value in [decimal.Decimal("-inf")]:
            str_output += "-inf"
        elif self.left_value in [decimal.Decimal("inf")]:
            str_output += "+inf"
        else:
            str_output += str(self.left_value)

        str_output += ","

        if self.right_value in [decimal.Decimal("-inf")]:
            str_output += "-inf"
        elif self.right_value in [decimal.Decimal("inf")]:
            str_output += "+inf"
        else:
            str_output += str(self.right_value)

        if self.right_open:
            str_output += ")"
        else:
            str_output += "]"

        return str_output

    def __hash__(self):
        return hash(str(self.left_open) + str(self.left_value) + ":" + str(self.right_value) + str(self.right_open))

    def __eq__(self, other):
        if isinstance(other, Interval):
            return self.left_value == other.left_value and self.right_value == other.right_value \
                   and self.left_open == other.left_open and self.right_open == other.right_open

    @staticmethod
    def sub(v1, v2):
        """
        Implement v1- sub v2+, and v1+ sub v2-, where v- represents the left value of the Interval instance and v+
        denotes the right value of the Interval instance.
        Args:
            v1 (an Interval instance):
            v2 (an Interval instance):

        Returns:
            a newly-created Interval instance
        """
        if v1.left_value in [decimal.Decimal("-inf"), decimal.Decimal("inf")]:
            left_value = v1.left_value
        else:
            left_value = v1.left_value - v2.right_value
        if v1.right_value in [decimal.Decimal("-inf"), decimal.Decimal("inf")]:
            right_value = v1.right_value
        else:
            right_value = v1.right_value - v2.left_value

        left_open, right_open = False, False

        if left_value == decimal.Decimal("-inf") or (v1.left_open or v2.right_open):
            left_open = True

        if right_value == decimal.Decimal("inf") or (v1.right_open or v2.left_open):
            right_open = True

        return Interval(left_value, right_value, left_open, right_open)

    @staticmethod
    def circle_sub(v1, v2):
        """
        Implement v1- sub v2-, and v1+ sub v2+, where v- represents the left value of the Interval instance and v+
        denotes the right value of the Interval instance.
        Args:
           v1 (an Interval instance):
           v2 (an Interval instance):

        Returns:
           a newly-created Interval instance
        """
        if v1.left_value in [decimal.Decimal("-inf"), decimal.Decimal("inf")]:
            left_value = v1.left_value
        else:
            left_value = v1.left_value - v2.left_value
        if v1.right_value in [decimal.Decimal("-inf"), decimal.Decimal("inf")]:
            right_value = v1.right_value
        else:
            right_value = v1.right_value - v2.right_value

        left_open, right_open = False, False

        if left_value == decimal.Decimal("-inf") or (v1.left_open and not v2.left_open):
            left_open = True

        if right_value == decimal.Decimal("inf") or (v1.right_open and not v2.right_open):
            right_open = True

        return Interval(left_value, right_value, left_open, right_open)

    @staticmethod
    def add(v1, v2):
        """
        Implement v1- add v2-, and v1+ add v2+, where v- represents the left value of the Interval instance and v+
        denotes the right value of the Interval instance.
        Args:
           v1 (an Interval instance):
           v2 (an Interval instance):

        Returns:
           a newly-created Interval instance
        """
        if v1.left_value in [decimal.Decimal("-inf"), decimal.Decimal("inf")]:
            left_value = v1.left_value
        else:
            left_value = v1.left_value + v2.left_value
        if v1.right_value in [decimal.Decimal("-inf"), decimal.Decimal("inf")]:
            right_value = v1.right_value
        else:
            right_value = v1.right_value + v2.right_value

        left_open, right_open = False, False

        if left_value == decimal.Decimal("-inf") or (v1.left_open or v2.left_open):
            left_open = True

        if right_value == decimal.Decimal("inf") or (v1.right_open or v2.right_open):
            right_open = True

        return Interval(left_value, right_value, left_open, right_open)

    @staticmethod
    def circle_add(v1, v2):
        """
        Implement v1- add v2+, and v1+ add v2-, where v- represents the left value of the Interval instance and v+
        denotes the right value of the Interval instance.
        Args:
           v1 (an Interval instance):
           v2 (an Interval instance):

        Returns:
           a newly-created Interval instance
        """
        if v1.left_value in [decimal.Decimal("-inf"), decimal.Decimal("inf")]:
            left_value = v1.left_value
        else:
            left_value = v1.left_value + v2.right_value
        if v1.right_value in [decimal.Decimal("-inf"), decimal.Decimal("inf")]:
            right_value = v1.right_value
        else:
            right_value = v1.right_value + v2.left_value
        left_open, right_open = False, False

        if left_value == decimal.Decimal("-inf") or (v1.left_open and not v2.right_open):
            left_open = True

        if right_value == decimal.Decimal("inf") or (v1.right_open and not v2.left_open):
            right_open = True

        return Interval(left_value, right_value, left_open, right_open)


if __name__ == "__main__":

    # a1 = Interval(1.5, 2.5, True, False)
    # a2 = Interval(2.5, 4, True, False)
    # print(Interval.intersection(a1, a2))
    # exit()

    # D: ['[16.0,220.0)', '(220.0,221.0)']
    # new: ['(221.0,222.0)', '[17.0,221.0)']

    a = [Interval(221.0, 222, True, True), Interval(17, 221, False, True)]
    b = [Interval(16, 220, False, True), Interval(220, 221, True, True)]
    c = [Interval(0.0, 0.0, False, False), Interval(2.0, 3.0, False, False)]
    d = Interval.diff_list(a, b)
    print([str(item) for item in d])

    exit()

    c = Interval.diff_list(b, a)
    # ['[2.5,4.0]']
    c = [Interval(0, 12,   False, False), Interval(21, 64, False, False)]

    print([str(item) for item in Interval.diff(b, a)])
    print([str(item) for item in Interval.list_union(c, a)])
    print(Interval.list_inclusion(a, c))
