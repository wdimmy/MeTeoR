from meteor_reasoner.classes.literal import *
from meteor_reasoner.classes.rule import *
from meteor_reasoner.classes.atom import Atom
from meteor_reasoner.classes.interval import Interval
from meteor_reasoner.classes.term import Term

def euqal_conversion(f):
    """
    This function is to convert the fact entailment program to the consistency checking problem by adding
    a new fact and a new rule.
    Args:
        PI (list of Rule instances):
        D (dictionary of dictionary): store all facts
        f (a query):

    Returns:
        newly-createdly Literal instance

    """
    t1, t2 = f.interval.left_value, f.interval.right_value
    head = Atom("Bottom", tuple([Term("nan")]))
    literal1 = Atom("New", f.entity)
    literal2 = Literal(Atom(f.predicate, f.entity))
    operator1 = Operator("Boxplus", Interval(0, t2-t1, False, f.interval.right_open))
    literal2.operators.append(operator1)
    rule = Rule(head, [literal1, literal2])
    fact = Atom("New", f.entity, Interval(t1, t1, False, False))
    return rule, fact, literal2
