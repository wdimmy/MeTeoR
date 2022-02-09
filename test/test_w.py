from meteor_reasoner.demo.dataset import CASES
from meteor_reasoner.utils.loader import load_program
from meteor_reasoner.canonical.calculate_w import get_w


def test_w():
    case = CASES["case_1"]
    program = case[1]
    truth_w = case[2][0]

    Program = load_program(program)
    w = get_w(rules=Program)
    print("w:",w)
    print("truth_w:",truth_w)
    assert 2 * w == truth_w

    case = CASES["case_2"]
    program = case[1]
    truth_w = case[2][0]

    Program = load_program(program)
    w = get_w(rules=Program)
    print("w:", w)
    print("truth_w:", truth_w)
    assert 2 * w == truth_w

    case = CASES["case_3"]
    program = case[1]
    truth_w = case[2][0]

    Program = load_program(program)
    w = get_w(rules=Program)
    print("w:", w)
    print("truth_w:", truth_w)
    assert 2 * w == truth_w

    case = CASES["case_4"]
    program = case[1]
    truth_w = case[2][0]

    Program = load_program(program)
    w = get_w(rules=Program)
    print("w:", w)
    print("truth_w:", truth_w)
    assert 2 * w == truth_w

    case = CASES["case_5"]
    program = case[1]
    truth_w = case[2][0]

    Program = load_program(program)
    w = get_w(rules=Program)
    print("w:", w)
    print("truth_w:", truth_w)
    assert 2 * w == truth_w

    case = CASES["case_6"]
    program = case[1]
    truth_w = case[2][0]

    Program = load_program(program)
    w = get_w(rules=Program)
    print("w:", w)
    print("truth_w:", truth_w)
    assert 2 * w == truth_w

    case = CASES["case_7"]
    program = case[1]
    truth_w = case[2][0]

    Program = load_program(program)
    w = get_w(rules=Program)
    print("w:", w)
    print("truth_w:", truth_w)
    assert 2 * w == truth_w

    case = CASES["case_8"]
    program = case[1]
    truth_w = case[2][0]

    Program = load_program(program)
    w = get_w(rules=Program)
    print("w:", w)
    print("truth_w:", truth_w)
    assert 2 * w == truth_w

test_w()



