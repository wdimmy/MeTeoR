from meteor_reasoner.classes.atom import Atom
from meteor_reasoner.classes.literal import Literal, BinaryLiteral


def check_propagation(program):
    forward = True
    backward = True
    for rule in program:
        head = rule.head
        if isinstance(head, Literal):
            for operator in head.operators:
                if operator.name in ["Boxplus"]:
                    backward = False
                elif operator.name in ["Boxminus"]:
                    forward = False
        if not forward and not backward:
            return 0 # neither forwarding or backwarding

        for literal in rule.body:
            if isinstance(literal, Literal):
                for operator in literal.operators:
                    if operator.name in ["Boxminus", "Diamondminus"]:
                        backward = False
                    elif operator.name in ["Boxplus", "Diamondminus"]:
                        forward = False
            elif isinstance(literal, BinaryLiteral):
                if literal.operator.name in ["Boxminus", "Diamondminus"]:
                    backward = False
                elif literal.operator.name in ["Boxplus", "Diamondminus"]:
                    forward = False
                left_literal = literal.left_literal
                if not isinstance(left_literal, Atom):
                    for operator in left_literal.operators:
                        if operator.name in ["Boxminus", "Diamondminus"]:
                            backward = False
                        elif operator.name in ["Boxplus", "Diamondminus"]:
                            forward = False
                right_literal = literal.right_literal
                if not isinstance(right_literal, Atom):
                    for operator in right_literal.operators:
                        if operator.name in ["Boxminus", "Diamondminus"]:
                            backward = False
                        elif operator.name in ["Boxplus", "Diamondminus"]:
                            forward = False

        if not forward and not backward:
            return 0  # neither forwarding or backwarding
    if forward:
        return 1 # forwarding
    elif backward:
        return 2 # backwarding
    else:
        return 0  # mix






