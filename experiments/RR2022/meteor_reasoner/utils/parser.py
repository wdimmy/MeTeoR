import re, copy, random
from datetime import datetime
from meteor_reasoner.classes.atom import *
from meteor_reasoner.classes.term import *
from meteor_reasoner.classes.literal import *
from meteor_reasoner.classes.interval import *
from meteor_reasoner.classes.rule import *
from decimal import Decimal
ATOM_PATTERN = "(.*)\((.*)\)"
FACT_WITH_ENTITY_PATTERN = "(.*)\((.*)\)@(.*)"
FACT_WITHOUT_ENTITY_PATTERN = "(.*)@(.*)"
INTERVAL_TWO_POINTS_PATTERN = "(^[\(,\[])(-?\d+\.?\d*|-inf),(-?\d+\.?\d*|\+?inf)([\),\]])$"
INTERVAL_ONE_POINT_PATTERN =  "(^[\(,\[])(-?\d+\.?\d*|\+?inf)([\),\]])$"
OPERATOR_TWO_POINTS_PATTERN = "(.*)([\(,\[])(-?\d+\.?\d*|-inf),(-?\d+\.?\d*|\+?inf)([\),\]])$"
OPERATOR_ONE_POINT_PATTERN =  "(.*)([\(,\[])(-?\d+\.?\d*|-inf)([\),\]])$"


def random_return_name():
    strname = "_TMP_" + datetime.now().strftime("%H%M%S") + str(random.choice([1,2,4,5,6]))
    return strname


def parse_rule(line):
    """
    Parse a string-formed rule.
    Args:
        rule (str):

    Returns:
        A  list of rule instance(s).
    """
    line = line.strip()
    line = line.replace(" ", "")
    head, body = line.strip().split(":-")
    if "||" in body:
       body, negative_body = body.split("||")
    else:
        negative_body = []
    try:
        head_atom = parse_literal(head)
    except:
        raise Exception("{} has an incorrect syntax!".format(head))

    literals = []
    for literal_str in parse_body(body):
        try:
           literal = parse_literal(literal_str)
        except:
            raise Exception("{} has an incorrect syntax!".format(literal_str))
        literals.append(literal)

    negative_body = []
    if len(negative_body) != 0:
        for literal_str in parse_body(negative_body):
            try:
               literal = parse_literal(literal_str)

            except:
                raise Exception("{} has an incorrect syntax!".format(literal_str))
            negative_body.append(literal)

    ordered_literals = []
    for literal in literals:
        if isinstance(literal, BinaryLiteral):
            ordered_literals.append(literal)
            literals.remove(literal)
    literals = sorted(literals, key=lambda item: len(item.get_entity()), reverse=True)
    ordered_literals = ordered_literals + literals
    rule = Rule(head_atom, ordered_literals, negative_body=negative_body)
    return rule


def parse_str_fact(line):
    result = re.search(FACT_WITH_ENTITY_PATTERN, line)
    if result:
        predicate = result.group(1)
        entity = tuple([Term(item) for item in result.group(2).split(",")])
        span = result.group(3)
        b = re.search(INTERVAL_TWO_POINTS_PATTERN, span)
        if b is None:  # contain one point
            try:
                Decimal(span)
                return predicate, entity, Interval(Decimal(span), Decimal(span), False, False)
            except ValueError:
                b = re.search(INTERVAL_ONE_POINT_PATTERN, span)
                if b is None:
                    raise ValueError("The interval can not be parsed correctly!")

                left_value = Decimal(b.group(2))
                right_value = Decimal(b.group(2))
                left_open, right_open = False, False

                if b.group(1) == "(":
                    left_open = True

                if b.group(3) == ")":
                    right_open = True

                if not Interval.is_valid_interval(left_value, right_value, left_open, right_open):
                    raise ValueError("{} contain an invalid interval!".format(line))

                return predicate, entity, Interval(left_value, right_value, left_open, right_open)

        else:
            left_value = Decimal(b.group(2))
            right_value = Decimal(b.group(3))
            left_open, right_open = False, False

            if b.group(1) == "(":
                left_open = True

            if b.group(4) == ")":
                right_open = True

            if not Interval.is_valid_interval(left_value, right_value, left_open, right_open):
                raise ValueError("{} contain an invalid interval!".format(line))

            return predicate, entity, Interval(left_value, right_value, left_open, right_open)

    else:
        result = re.search(FACT_WITHOUT_ENTITY_PATTERN, line)
        if result:
            predicate = result.group(1)
            entity = tuple([Term("nan")])
            span = result.group(2)
            b = re.search(INTERVAL_TWO_POINTS_PATTERN, span)
            if b is None:  # contain one point
                try:
                    Decimal(span)
                    return predicate, entity, Interval(Decimal(span), Decimal(span), False, False)
                except ValueError:
                    b = re.search(INTERVAL_ONE_POINT_PATTERN, span)
                    if b is None:
                        raise ValueError("The interval({}) can not be parsed correctly!".format(span))

                    left_value = Decimal(b.group(2))
                    right_value = Decimal(b.group(2))
                    left_open, right_open = False, False

                    if b.group(1) == "(":
                        left_open = True

                    if b.group(3) == ")":
                        right_open = True

                    if not Interval.is_valid_interval(left_value, right_value, left_open, right_open):
                        raise ValueError("{} contain an invalid interval!".format(line))

                    return predicate, entity, Interval(left_value, right_value, left_open, right_open)

            else:
                left_value = Decimal(b.group(2))
                right_value = Decimal(b.group(3))
                left_open, right_open = False, False

                if b.group(1) == "(":
                    left_open = True

                if b.group(4) == ")":
                    right_open = True

                if not Interval.is_valid_interval(left_value, right_value, left_open, right_open):
                    raise ValueError("{} contain an invalid interval!".format(line))

                return predicate, entity, Interval(left_value, right_value, left_open, right_open)
        else:
            raise ValueError("{} is an invalid fact!".format(line))


def parse_atom(atom_str):
    """
    Parse a string-form atom into an atom instance.
    Args:
        atom_str (str): a string-form atom, e.g.  A(X,y). In particular, we specify that
        a variable starts with the first letter capitalized.

    Returns:
        an atom instance.
    """

    head_result = re.search(ATOM_PATTERN, atom_str)
    if head_result is not None:
        head_predicate = head_result.group(1)
        head_entity = head_result.group(2).split(",")
        entity_list = []
        for item in head_entity:
            if item[0].isupper():  # is a variable
                entity_list.append(Term(item, "variable"))
            else:
                entity_list.append(Term(item, "constant"))

        atom = Atom(head_predicate, tuple(entity_list))
    else:
        atom = Atom(atom_str, tuple([Term("nan")]))

    return atom


def parse_body(body):
    """
    Split literals separated by comma in the body into a list.

    Args:
        body (str): a string consisting of one or multiple literals separated by comma

    Returns:
        a list of strings, each of which represents one literal

    """
    literals = []
    left = False
    current_str = ""
    for item in body:
        if item in ["(", "["]:
            left = True

        if item != ",":
            if item in ["(", "["]:
                left = True
            if item in [")", "]"]:
                left = False
            current_str += item
        else:
            if not left:
                literals.append(current_str)
                current_str = ""
            else:
                current_str += item
    literals.append(current_str)
    return literals


def parse_operator(operator_str):
    """
    Parse a string-form operator into a operator instance.

    Args:
        operator_str (str): a string-form operator, e.g. Boxminus[2,3]

    Returns:
       Operator instance.
    """
    b = re.search(OPERATOR_TWO_POINTS_PATTERN, operator_str)
    if b is None:
        b = re.search(OPERATOR_ONE_POINT_PATTERN, operator_str)
        if b is None:
            raise ValueError("The interval can not be parsed correctly!")

        left_value = Decimal(b.group(3))
        right_value = Decimal(b.group(3))
        left_open, right_open = False, False

        if b.group(2) == "(":
            left_open = True

        if b.group(4) == ")":
            right_open = True

        if b.group(1) == "SOMETIME" and left_value >= 0:
            return Operator("Diamondplus", Interval(left_value, right_value, left_open, right_open))
        elif b.group(1) == "SOMETIME" and left_value < 0:
            return Operator("Diamondminus", Interval(-right_value, -left_value, right_open, left_open))
        elif b.group(1) == "ALWAYS" and left_value >= 0:
            return Operator("Boxplus", Interval(left_value, right_value, left_open, right_open))
        elif b.group(1) == "ALWAYS" and left_value <= 0:
            return Operator("Boxminus", Interval(-right_value, -left_value, right_open, left_open))
        elif b.group(1) == "UNTIL" and left_value < 0:
            return Operator("Since", Interval(-right_value, -left_value, right_open, left_open))
        elif b.group(1) == "UNTIL" and left_value >=0:
            return Operator("Until", Interval(left_value, right_value, left_open, right_open))
        else:
            return Operator(b.group(1), Interval(left_value, right_value, left_open, right_open))

    left_value = Decimal(b.group(3))
    right_value = Decimal(b.group(4))
    left_open, right_open = False, False

    if b.group(2) == "(":
        left_open = True

    if b.group(5) == ")":
        right_open = True

    if b.group(1) == "SOMETIME" and left_value>=0:
        return Operator("Diamondplus", Interval(left_value, right_value, left_open, right_open))
    elif b.group(1) == "SOMETIME" and left_value<0:
        return Operator("Diamondminus", Interval(-right_value,-left_value, right_open, left_open))
    elif b.group(1) == "ALWAYS" and left_value>=0:
        return Operator("Boxplus", Interval(left_value, right_value, left_open, right_open))
    elif b.group(1) == "ALWAYS" and left_value < 0:
        return Operator("Boxminus", Interval(-right_value, -left_value, right_open, left_open))
    elif b.group(1) == "UNTIL" and left_value < 0:
        return Operator("Since", Interval(-right_value, -left_value, right_open, left_open))
    elif b.group(1) == "UNTIL" and left_value >= 0:
        return Operator("Until", Interval(left_value, right_value, left_open, right_open))
    else:
       return Operator(b.group(1), Interval(left_value, right_value, left_open, right_open))


def parse_literal(literal):
    """
    We write different regex expressions to parse the string-form literal
    Args:
        literal (str):

    Returns:
        BinaryLiteral instance or Literal instance.

    """

    pattern1 = "Boxminus[\[,\(]-?\d+\.?\d*[\),\]]"
    pattern2 = "Boxplus[\[,\(]-?\d+\.?\d*[\),\]]"
    pattern3 = "Diamondminus[\[,\(]-?\d+\.?\d*[\),\]]"
    pattern4 = "Diamondplus[\[,\(]-?\d+\.?\d*[\),\]]"
    pattern4_1 = "SOMETIME[\[,\(]-?\d+\.?\d*[\),\]]"
    pattern4_2 = "ALWAYS[\[,\(]-?\d+\.?\d*[\),\]]"



    pattern5 = "Boxminus[\[,\(]-?\d+\.?\d*,-?\d+\.?\d*[\),\]]"
    pattern6 = "Boxplus[\[,\(]-?\d+\.?\d*,-?\d+\.?\d*[\),\]]"
    pattern7 = "Diamondminus[\[,\(]-?\d+\.?\d*,-?\d+\.?\d*[\),\]]"
    pattern8 = "Diamondplus[\[,\(]-?\d+\.?\d*,-?\d+\.?\d*[\),\]]"
    pattern8_1 = "SOMETIME[\[,\(]-?\d+\.?\d*,-?\d+\.?\d*[\),\]]"
    pattern8_2 = "ALWAYS[\[,\(]-?\d+\.?\d*,-?\d+\.?\d*[\),\]]"

    pattern9 =  "Boxminus[\[,\(]-?\d+\.?\d*,\+?inf[\),\]]"
    pattern10 = "Boxplus[\[,\(]-?\d+\.?\d*,\+?inf[\),\]]"
    pattern11 = "Diamondminus[\[,\(]-?\d+\.?\d*,\+?inf[\),\]]"
    pattern12 = "Diamondplus[\[,\(]-?\d+\.?\d*,\+?inf[\),\]]"
    pattern12_1 = "SOMETIME[\[,\(]-?\d+\.?\d*,\+?inf[\),\]]"
    pattern12_2 = "ALWAYS[\[,\(]-?\d+\.?\d*,\+?inf[\),\]]"


    pattern13 = "Boxminus[\[,\(]-inf,-?\d+\.?\d*[\),\]]"
    pattern14 = "Boxplus[\[,\(]-inf,-?\d+\.?\d*[\),\]]"
    pattern15 = "Diamondminus[\[,\(]-inf,-?\d+\.?\d*[\),\]]"
    pattern16 = "Diamondplus[\[,\(]-inf,-?\d+\.?\d*[\),\]]"
    pattern16_1 = "SOMETIME[\[,\(]-inf,-?\d+\.?\d*[\),\]]"
    pattern16_2 = "ALWAYS[\[,\(]-inf,-?\d+\.?\d*[\),\]]"

    since_pattern1 = "Since[\[,\(]-?\d+\.?\d*,-?\d+\.?\d*[\),\]]"
    since_pattern3 = "Since[\[,\(]-?\d+\.?\d*[\),\]]"
    until_pattern2 = "Until[\[,\(]-?\d+\.?\d*,-?\d+\.?\d*[\),\]]"
    unitl_pattern4 = "Until[\[,\(]-?\d+\.?\d*[\),\]]"
    UNTIL_pattern5 = "UNTIL[\[,\(]-?\d+\.?\d*,-?\d+\.?\d*[\),\]]"
    UNTIL_pattern6 = "UNTIL[\[,\(]-?\d+\.?\d*[\),\]]"

    since_pattern00 = "Since[\[,\(]-?\d+\.?\d*,\+?inf[\),\]]"
    since_pattern01 = "Since[\[,\(]-inf,-?\d+\.?\d*[\),\]]"
    UNTIL_pattern02 = "UNTIL[\[,\(]-?\d+\.?\d*,\+?inf[\),\]]"
    UNTIL_pattern03 = "UNTIL[\[,\(]-inf,-?\d+\.?\d*[\),\]]"

    until_pattern11 = "Until[\[,\(]-?\d+\.?\d*,\+?inf[\),\]]"
    until_pattern12 = "Until[\[,\(]-inf,-?\d+\.?\d*[\),\]]"
    UNTIL_pattern13 = "UNTIL[\[,\(]-?\d+\.?\d*,\+?inf[\),\]]"
    UNTIL_pattern14 = "UNTIL[\[,\(]-inf,-?\d+\.?\d*[\),\]]"


    # check whether it is a since or a until literal
    result = re.findall("|".join([since_pattern00, since_pattern01, until_pattern11, until_pattern12, UNTIL_pattern02, UNTIL_pattern03,
                                  UNTIL_pattern13, UNTIL_pattern14, since_pattern1,
                                  since_pattern3, until_pattern2, unitl_pattern4, UNTIL_pattern5, UNTIL_pattern6]), literal)

    if len(result) != 0:
        begin_index = literal.index(result[0])
        left_literal = literal[:begin_index]
        right_literal = literal[begin_index + len(result[0]):]
        left_literal = parse_literal(left_literal)
        right_literal = parse_literal(right_literal)

        op = parse_operator(result[0])
        b_literal = BinaryLiteral(left_literal, right_literal, op)

        return b_literal

    else:
        # check whether it is a literal with temporal operator(s)
        #result = re.findall("|".join([pattern12_2]), literal)
        result = re.findall("|".join([pattern9, pattern10, pattern11, pattern12, pattern12_1, pattern12_2, pattern13, pattern14,
                                      pattern15, pattern16, pattern16_1, pattern16_2, pattern5, pattern6, pattern7, pattern8,  pattern8_1, pattern8_2, pattern1,
                                      pattern2, pattern3, pattern4, pattern4_1, pattern4_2]), literal)
        if len(result) != 0:
            operators = []
            for operator_str in result:
                operator_ins = parse_operator(operator_str)
                operators.append(operator_ins)

            atom_str = literal[len("".join(result)):]
            atom = parse_atom(atom_str)
            literal = Literal(atom, operators)
            return literal

        else:
            # literal without any temporal operators
            atom = parse_atom(literal)
            t_literal = Literal(atom, [])
            return t_literal


if __name__ == "__main__":
    operator_str = "ALWAYS[-1,-3]A"
    lit = parse_literal(operator_str)
    print(lit)
