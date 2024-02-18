import sys
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

import objects


def get_attribute(item: str, attribute_name, attribute_dict: dict[int]):
    """
    Prompts the user to select an attribute value for the given item.

    Args:
        item (str): The name of the item.
        attribute_name: The name of the attribute.
        attribute_dict (dict[int]): A dictionary mapping attribute values to their corresponding names.

    Returns:
        The selected attribute value from the attribute_dict.

    """
    while True:
        pp_attribute = {key: value.name for key, value in attribute_dict.items()}
        attribute_value = int(input(f"{item} {attribute_name} {pp_attribute}: "))
        if attribute_value in attribute_dict:
            return attribute_dict[attribute_value]
        else:
            print(f"Not a valid {attribute_name} Option! Please try again.")


def ask(prompt: str, yes: str = "Y", no: str = "N"):
    """
    Prompts the user with a yes/no question and returns True if the user responds with 'yes', False otherwise.

    Args:
        prompt (str): The question prompt to display to the user.
        yes (str, optional): The string representing 'yes'. Defaults to "Y".
        no (str, optional): The string representing 'no'. Defaults to "N".

    Returns:
        bool: True if the user responds with 'yes', False otherwise.
    """
    response = "Not Set"
    while response.upper() not in (yes.upper(), no.upper()):
        response = input(f"{prompt} ({yes}/{no}): ")
    return response.upper() == yes.upper()
