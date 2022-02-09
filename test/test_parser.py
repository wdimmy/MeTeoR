from meteor_reasoner.utils.parser import *


def test_literal():
    raw_literal = "Boxminus[1,2]ASince[1,2]Diamondminus[3,4]Boxminus[5,6]B(X)"
    literal = parse_literal(raw_literal)
    assert str(literal) == raw_literal

    raw_literal = "ASince[1,2]Diamondminus[3,4]Boxminus[5,6]B(X)"
    literal = parse_literal(raw_literal)
    assert str(literal) == raw_literal


def test_rule():
    raw_rule = "Boxplus[1,3]Boxminus[1,2]A:-Diamondminus[1,2]B(X),Boxminus[1,2]Diamondminus[2,3]C(X)"
    rule = parse_rule(raw_rule)
    print(str(rule))
    assert raw_rule == str(rule)

