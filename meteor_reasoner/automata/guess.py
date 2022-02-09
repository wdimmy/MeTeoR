from collections import deque


def generate_guess_points(w, binary_literals, ruler_intervals, z, gcd):
    to_guess_points = set()
    for interval in ruler_intervals:
        to_guess_points.add(interval.left_value)
        to_guess_points.add(interval.right_value)

    left_z = z
    right_z = z

    left_len_list = deque(
        [str(abs(interval.left_value - interval.right_value)) for interval in ruler_intervals if
         interval.left_value - interval.right_value != 0])
    right_len_list = deque(
        [str(abs(interval.left_value - interval.right_value)) for interval in ruler_intervals if
         interval.left_value - interval.right_value != 0])

    while left_z > 0:
        last_endpoint = ruler_intervals[0].left_value
        while True:
            pattern = "#".join(left_len_list)
            if pattern in w.left_pattern:
                next_len = w.left_pattern[pattern]
                if next_len <= left_z:
                    last_endpoint = last_endpoint - next_len
                    to_guess_points.add(last_endpoint)
                    left_len_list.appendleft(str(next_len))
                    left_z -= next_len
                    break

            del left_len_list[-1]

    while right_z > 0:
        last_endpoint = ruler_intervals[-1].right_value
        while True:
            pattern = "#".join(right_len_list)
            if pattern in w.left_pattern:
                next_len = w.left_pattern[pattern]
                if next_len <= right_z:
                    last_endpoint = last_endpoint + next_len
                    to_guess_points.add(last_endpoint)
                    right_len_list.appendleft(str(next_len))
                    right_z -= next_len
                    break

            del right_len_list[0]

    to_guess_points = sorted(list(to_guess_points))
    the_left_most_z = to_guess_points[0]
    the_right_most_z = to_guess_points[-1]

    left_right_literals = list()
    for item in binary_literals:
        if item.left_atom.get_predicate() not in ["Bottom", "Top"] and item.left_atom not in left_right_literals:
            left_right_literals.append(item.left_atom)
        if item.right_atom.get_predicate() not in ["Bottom", "Top"] and item.right_atom not in left_right_literals:
            left_right_literals.append(item.right_atom)

    for i in range(1, len(left_right_literals) + 1):
        to_guess_points.insert(0, the_left_most_z - gcd * i)
        to_guess_points.insert(-1, the_right_most_z + gcd * i)

    return to_guess_points, left_right_literals
