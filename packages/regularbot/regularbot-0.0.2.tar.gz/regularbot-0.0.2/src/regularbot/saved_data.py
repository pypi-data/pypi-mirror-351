import json


def load_saved_data() -> dict[str, str]:
    """
    Load the saved data from the last execution.

    Returns:
        dict[str, str]: A dictionary containing the saved data.
    """
    with open("/saved_data.json", "r") as file:
        return json.load(file)


def save_data(data: dict[str, str]):
    """
    Save data for the next execution. Given data must be a dictionary of strings to strings. If
    the data is not a dictionary of strings to strings, a ValueError is raised.

    Args:
        data (dict[str, str]): The data to save.
    """
    if not isinstance(data, dict):
        raise ValueError(
            "Regularbot package: Data must be a dictionary of strings to strings."
        )

    for key, value in data.items():
        if not isinstance(key, str) or not isinstance(value, str):
            raise ValueError(
                "Regularbot package: Data must be a dictionary of strings to strings."
            )

    with open("/saved_data.json", "w") as file:
        json.dump(data, file)
