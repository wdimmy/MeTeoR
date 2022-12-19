from meteor_reasoner.classes.literal import *
from meteor_reasoner.classes.atom import *
from meteor_reasoner.classes.rule import *
import copy


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


def construct_pair(rules):
    pairs = set()
    for rule in rules:
        head = rule.head
        if isinstance(head, Atom):
            origin = [0, 0]
        else:
            origin = [0, 0]
            for operator in head.operators:
                if operator.name == "Boxplus":
                    origin[0] = origin[0] + operator.interval.left_value
                    origin[1] = origin[1] + operator.interval.right_value
                else:
                    origin[0] = origin[0] - operator.interval.left_value
                    origin[1] = origin[1] - operator.interval.right_value

        for literal in rule.body:
            tmp_origin = copy.deepcopy(origin)
            if not isinstance(literal, Atom):
                for operator in literal.operators:
                    if operator.name == "Diamondminus":
                        tmp_origin[0] = tmp_origin[0] + operator.interval.left_value
                        tmp_origin[1] = tmp_origin[1] + operator.interval.right_value
                    if operator.name == "Diamondplus":
                        tmp_origin[0] = tmp_origin[0] - operator.interval.left_value
                        tmp_origin[1] = tmp_origin[1] - operator.interval.right_value
            else:
                tmp_origin[0] = tmp_origin[0] + 0
                tmp_origin[1] = tmp_origin[1] + 0


            pairs.add((literal.get_predicate(), head.get_predicate(), tmp_origin[0], tmp_origin[1]))

    return pairs





