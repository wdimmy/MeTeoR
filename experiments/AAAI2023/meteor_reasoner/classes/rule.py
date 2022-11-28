class Rule:
    """
    A rule instance consists of two part: a head (an Atom instance) and
    a body (a list of  Literal or BinarayLiteral Instances)
    """
    def __init__(self, head, body, negative_body=[]):
        """

        Args:
            head (an Atom instance):
            body (a list of Literal or BinaryLiteral instances):
        """
        self.head = head
        self.body = body  # a list of literal
        self.negative_body = negative_body # a list of literals

    def __str__(self):
        if len(self.negative_body) == 0:
            return str(self.head) + ":-" + ",".join([str(literal) for literal in self.body])
        else:
            return str(self.head) + ":-" + ",".join([str(literal) for literal in self.body])\
                   + "||" + ",".join([str(literal) for literal in self.negative_body_atoms])