from collections import namedtuple
from ingridient import Ingridient


# instances of meals will be namedtuples
Meal = namedtuple("Meal", ["name", "type", "category", "ingridients",
                           "quantity"])


def list_to_text(ingridients_list):
    """
    Recieves a list with lists
    [ingridient_instance, quantity] and returns a
    text with the data
    """
    to_return = "List\n"
    for (ingridient, quantity) in ingridients_list:
        to_return = f"{to_return}{ingridient.name} {quantity}\n"
    return to_return


def load_ingridients(path):
    """
    Reads csv file from path and return instances of Ingridient
    """
    with open(file=path, encoding="utf-8-sig", mode="r") as file:
        ingridients = {}  # ingridient_name: ingridient_instance
        header = [x.strip() for x in file.readline().strip().split(";")]
        lines = file.readlines()
        for line in lines:
            line = line.strip().split(";")
            # strings are converte to apropiate type
            data = map(lambda x: int(x) if x.isdigit() else x, line)
            arguments = dict(zip(header, data))
            instance = Ingridient(**arguments)
            ingridients[instance.name] = instance
        print(ingridients)
        return ingridients


def load_meals(path, ingridients):
    """
    Reads csv file from path and return namedtuples that contains the info
    and the instances from ingridients
    """
    with open(file=path, encoding="utf-8-sig", mode="r") as file:
        meals = {}  # meal_name: Meal_namedtuple
        header = [x.strip() for x in file.readline().strip().split(";")]
        lines = file.readlines()
        for line in lines:
            line = line.strip().split(";")
            # strings are converte to apropiate type
            data = map(lambda x: [int(y.strip()) if y.strip().isdigit()
                                  else y.strip() for y in x.strip().split(",")]
                       if "," in x else int(x) if x.isdigit() else x.strip(),
                       line)
            arguments = dict(zip(header, data))
            # name of ingridients are replaces with their instances
            arguments["ingridients"] = [ingridients[ingridient] for ingridient
                                        in arguments["ingridients"]]
            meal = Meal(**arguments)
            meals[meal.name] = meal
        print(meals)
        return meals
