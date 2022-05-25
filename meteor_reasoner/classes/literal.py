class Operator:
    """
    The operator class is designed for storing six MTL operators, e.g., Boxminus[1,2],
    Boxplus(1,2), Diamondplus[3,4], Diamondminus[1,2], Since[1,2], Until[2,3]
    """
    def __init__(self, name, interval):
        """
        Args:
            name (str): Boxminus, Boxplus, Diamondplus, Diamondminus, Since, Until
            interval (Interval class):
        """
        if name not in ["Boxminus", "Boxplus", "Diamondplus", "Diamondminus", "Since", "Until"]:
            raise ValueError("Only support one of six operators (Boxminus, Boxplus, Diamondplus, "
                             "Diamondminus, Since, Until)!")

        self.name = name
        self.interval = interval

    def __eq__(self, other):
        if isinstance(other, Operator) and self.name == other.name and self.interval == other.interval:
            return True

        return False

    def __str__(self):
        return self.name + str(self.interval)


class Literal:
    """
    Literal class is for storing a literal consisting of one atom with one or multiple MTL operators,
    e.g., Boxminus[1,2]Professor(X)
    """
    def __init__(self, atom, operators=[]):
        """

        Args:
            atom (Atom class):
            operators (A list of Operator class):
        """
        self.atom = atom
        self.operators = operators

    def get_predicate(self):
        return self.atom.predicate

    def get_entity(self):
        return self.atom.entity

    def get_op_name(self): # always return the name of the first operator
        if len(self.operators) != 0:
            return self.operators[0].name
        else:
            return None

    def set_entity(self, entity):
        self.atom.entity = entity

    def __eq__(self, other):
        if isinstance(other, Literal):
            if self.atom == other.atom and self.operators == other.operators:
                return True
        return False

    def __str__(self):
        return "".join([str(operator) for operator in self.operators]) + str(self.atom)

    def __hash__(self):
        hash_value = hash("Literal" + str(self.atom) + "".join([str(operator) for operator in self.operators]))
        return  hash_value


class BinaryLiteral:
    """
    The BinaryLiteral class is used to store binary literal, in which there are two literal separated by
    Until or Since Operator, e.g. A(X)Since[1,2]B(X,Y)
    """
    def __init__(self, left_literal, right_literal, operator):
        """

        Args:
            left_atom (Atom class):
            right_atom (Atom class):
            operator (Operator class):
        """
        self.left_literal = left_literal
        self.right_literal = right_literal
        self.operator = operator

    def get_op_name(self):
        return self.operator.name

    def set_entity(self, entities):
        if self.left_literal.get_predicate() == "Top":
            self.left_literal.set_entity(entities[0])
        elif self.right_literal.get_predicate() == "Top":
            self.right_literal.set_entity(entities[0])
        else:
            self.left_literal.set_entity(entities[0])
            self.right_literal.set_entity(entities[1])

    def __eq__(self, other):
        if isinstance(other, BinaryLiteral):
            return self.left_literal == other.left_literal and self.right_literal == other.right_literal and \
                   self.operator == other.operator
        return False

    def __str__(self):
        return str(self.left_literal) + str(self.operator) + str(self.right_literal)

    def __hash__(self):
        return hash("BiLiteral:" + str(self.left_literal) + str(self.operator) + str(self.right_literal))







