class Atom:
    """
    An atom class consists of a predicate, a tuple of terms (constants or variables) and a temporal interval,
    e.g., A(X, mike)@[1,2] or A(X, mike)
    """
    def __init__(self, predicate, entity=None, interval=None):
        self.predicate = predicate
        self.entity = entity
        self.interval = interval

    def __eq__(self, other):
        if isinstance(other, Atom):
            if other.interval is None and self.interval is None:
                return other.predicate == self.predicate and other.entity == self.entity
            elif other.interval is not None and self.interval is not None:
                return other.predicate == self.predicate and other.entity == self.entity and str(other.interval) == str(self.interval)
            else:
                return False
        else:
            return False

    def get_predicate(self):
        return self.predicate

    def get_entity(self):
        return self.entity

    def set_entity(self, entity):
        self.entity = entity

    def __str__(self):
        if self.interval:
            if len(self.entity) > 1 or  self.entity[0].name != "nan":
                return self.predicate + "(" + ",".join([str(item) for item in self.entity]) + ")@" + str(self.interval)
            else:
                return self.predicate + "@" + str(self.interval)

        else:
            if self.entity:
                if len(self.entity) == 1 and self.entity[0].name == "nan":
                    return self.predicate

                return self.predicate + "(" + ",".join([str(item) for item in self.entity]) + ")"
            else:
                return self.predicate

    def __hash__(self):
        if self.entity:
            if len(self.entity) == 1 and self.entity[0].name == "nan":
                return hash("Atom" + str(self.predicate) + str(self.interval))

            return hash("Atom" + str(self.predicate) + ",".join([str(item) for item in self.entity])
                        + str(self.interval))
        else:
            return hash("Atom" + str(self.predicate) + str(self.interval))

