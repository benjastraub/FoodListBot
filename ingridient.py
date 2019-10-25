class Ingridient:
    def __init__(self, name, category, unit=None):
        self.name = name
        self.category = category
        self.unit = unit

    def __repr__(self):
        return self.name
