class Ingridient:
    def __init__(self, name, category, unit=None):
        self.name = name
        self.category = category
        self.unit = unit if unit is not "" else None

    def __repr__(self):
        to_return = self.name
        if self.unit:
            to_return += f" {self.unit}"
        return to_return
