from collections import deque
from meteor_reasoner.classes.atom import  Atom
from meteor_reasoner.classes.rule import *
from meteor_reasoner.classes.literal import *
import copy

prefix_ = "Build_"


def helper(i, operators, literal, build_dict, cnt, new_P):
    if i == -1:
        return literal

    else:
        if operators[i].name not in ["Diamondminus", "Diamondplus"]:
           body = copy.deepcopy(literal)
           body.operators = deque([operators[i]])

           if body in build_dict:
               tmp_head = build_dict[body]

           else:
               tmp_head = Atom(prefix_ + str(cnt[0]), literal.atom.entity)
               build_dict[body] = tmp_head
               cnt[0] = cnt[0] + 1

           if i == 0:
               return helper(i-1, operators, body)

           else:
               new_rule = Rule(tmp_head, [body])
               new_P.append(new_rule)

               literal.atom = tmp_head
               literal.operators = deque(list(literal.operators)[:i])
               return helper(i-1, operators, literal)

        else:

            body = copy.deepcopy(literal)
            body.operators = deque([operators[i]])

            if i == 0:
                top_atom = Atom("Top", ())
                left_literal = top_atom
                right_literal = body.atom

                if operators[i].name == "Diamondminus":
                    binary_literal = BinaryLiteral(left_literal, right_literal, Operator("Since", operators[i].interval))
                else:
                    binary_literal = BinaryLiteral(left_literal, right_literal, Operator("Until", operators[i].interval))

                return helper(i - 1, operators, binary_literal, build_dict, cnt, new_P)

            else:
                if body in build_dict:
                    tmp_head = build_dict[body]

                else:
                    tmp_head = Atom(prefix_ + str(cnt[0]), literal.atom.entity)
                    build_dict[body] = tmp_head
                    cnt[0] = cnt[0] + 1

                top_atom = Atom("Top", ())
                left_literal = top_atom
                right_literal = body.atom

                if operators[i].name == "Diamondminus":
                    binary_literal = BinaryLiteral(left_literal, right_literal, Operator("Since", operators[i].interval))
                else:
                    binary_literal = BinaryLiteral(left_literal, right_literal, Operator("Until", operators[i].interval))

                new_rule = Rule(tmp_head, [binary_literal])
                new_P.append(new_rule)
                literal.atom = tmp_head
                literal.operators = deque(list(literal.operators)[:i])
                return helper(i - 1, operators, literal, build_dict, cnt)


def normalize(P):
    """
    This function normalize each rule in P into four normal forms, Since, Until, Boxminus, Boxplus.
    Args:
        P (list of Rule instances):

    Returns:
        list of Rule instances

    """
    cnt = [0]
    build_dict = {}
    new_P = []

    for rule in P:
        head = rule.head
        body = rule.body
        new_body = []
        for literal in body:

            if isinstance(literal, BinaryLiteral):
                new_body.append(literal)
            elif isinstance(literal, Atom):
                new_body.append(literal)
            else:
                normal_flag = False
                for operator in literal.operators:
                    if operator.name in ["Diamondminus", "Diamondplus"]:
                        normal_flag = True
                        break
                if not normal_flag:
                    new_body.append(literal)

                else:
                    operators = literal.operators
                    new_literal = helper(len(operators)-1, operators, literal, build_dict, cnt, new_P)
                    new_body.append(new_literal)

        rule = Rule(head, new_body)
        new_P.append(rule)

    return new_P





