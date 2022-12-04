class Term:
    def __init__(self, name, type="constant"):
        """
        Args:
            value (string):
            type (str): ``constant '' or ``variable''
        """
        self.name = name
        self.type = type

    @classmethod
    def new_term(cls, name, type="constant"):
        return cls(name, type)

    def __hash__(self):
        return hash(self.type + str(self.name))

    def __str__(self):
        return self.name

    def __eq__(self, other):
        if isinstance(other, Term):
            return self.type == other.type and self.name == other.name

        return False
