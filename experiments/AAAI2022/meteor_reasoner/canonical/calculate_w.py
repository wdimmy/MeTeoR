from meteor_reasoner.classes.literal import *
from meteor_reasoner.classes.atom import *
from meteor_reasoner.classes.interval import *
from meteor_reasoner.classes.rule import Rule
import copy
from decimal import Decimal


def strengthening_transformation(literal):
    new_operators = []
    if isinstance(literal, BinaryLiteral):
        operator = literal.operator
        if operator.name == "Since":
            operator.name = "Diamondminus"
        else:
            operator.name = "Diamondplus"

        if isinstance(literal.right_literal, Atom):
             literal = Literal(literal.right_literal, [operator])
        else:
            literal = literal.right_literal
            literal.operators.insert(0, operator)

    if isinstance(literal, Atom):
        return literal

    for operator in literal.operators:
        if operator.name == "Boxplus":
            operator.name = "Diamondplus"
            new_operators.append(operator)
        elif operator.name == "Boxminus":
            operator.name = "Diamondminus"
            new_operators.append(operator)
        else:
            new_operators.append(operator)

    literal.operators = new_operators[:]
    return literal


def transformation(rules):
    new_rules = []

    for rule in rules:
        head = rule.head
        new_body = []
        for literal in rule.body:
            literal = strengthening_transformation(literal)
            new_body.append(literal)
        rule = Rule(head, new_body)
        new_rules.append(rule)
    return new_rules


def get_w(rules):
    new_rules = transformation(rules[:])
    max_w = 0
    for rule in new_rules:
        head = rule.head
        w_interval = Interval(0, 0, False, False)
        if not isinstance(head, Atom):
            for operator in head.operators:
                if operator.name == "Boxminus":
                    # need to be imporved
                    if operator.interval.right_value !=  Decimal("inf"):
                        w_interval = Interval.circle_sub(operator.interval, w_interval)
                else:
                    if operator.interval.right_value != Decimal("inf"):
                         w_interval = Interval.add(operator.interval, w_interval)

        for literal in rule.body:
            tmp_w_interval = copy.deepcopy(w_interval)
            if not isinstance(literal, Atom):
                for operator in literal.operators:
                    if operator.name == "Diamondminus":
                        if operator.interval.right_value !=  Decimal("inf"):
                              tmp_w_interval = Interval.add(operator.interval, tmp_w_interval)
                    else:
                        if operator.interval.right_value != Decimal("inf"):
                              tmp_w_interval = Interval.circle_sub(operator.interval, tmp_w_interval)
            max_w = max(abs(tmp_w_interval.right_value), max_w)
    return max_w



