from meteor_reasoner.classes.interval import Interval


def test_interval():
    # test the add, sub, cicle_add, cicle_sub
    interval1 = Interval(7, 10, False, False)
    interval2 = Interval(2, 4, False, False)

    truth_interval = Interval(9, 14, False, False)
    # usually used from diamondminus
    interval = Interval.add(interval1, interval2)
    assert truth_interval == interval

    truth_interval = Interval(11, 12, False, False)
    # usually used from boxminus
    interval = Interval.circle_add(interval1, interval2)
    assert truth_interval == interval

    truth_interval = Interval(5, 6, False, False)
    # usually used from boxplus
    interval = Interval.circle_sub(interval1, interval2)
    assert truth_interval == interval

    truth_interval = Interval(3, 8, False, False)
    # usually used from diamondplus
    interval = Interval.sub(interval1, interval2)
    assert truth_interval == interval


def test_static():
    interval1 = Interval(3, 4,False, False)
    interval2 = Interval(3, 4, False, False)
    print(Interval.inclusion(interval1, interval2))

    interval1 = Interval(3, 4, False, False)
    interval2 = Interval(3.5, 3.8, False, False)
    results = Interval.diff(interval1, [interval2])
    print([str(res) for res in results])


test_static()