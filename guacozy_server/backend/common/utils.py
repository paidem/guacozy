def model_choices_from_dictionary(dict):
    return tuple((i, dict[i]["name"]) for i in dict)
