from collections import namedtuple


# instances of meals will be namedtuples
Meal = namedtuple("Meal", ["name", "type", "category", "ingridients"])


def list_to_text(ingridients_list):
    """
    Recieves a list with tuples (ingridient_name, quantity) and returns
    a text with the data
    """
    to_return = ""
    for (ingridient, quantity) in ingridients_list:
        to_return = f"{to_return}{ingridient} {quantity}\n"
    return to_return
