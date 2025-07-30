import math

def format_time(seconds: float, seconds_precision: bool = True) -> str:
    if seconds_precision:
        return format_time_ex(
            seconds,
            ["s", "m", "h", "d"],
            [1, 60, 60, 24]
        )
    else:
        return format_time_ex(
            seconds,
            ["m", "h", "d"],
            [60, 60, 24]
        )


def format_time_ex(seconds: float, units: list, unit_lengths: list) -> str:
    if len(units) != len(unit_lengths):
        raise ValueError("Must specify exactly one unit_length for each unit")
    unit_multiplier = 1
    output_string = ""

    for index, unit_name, unit_length in zip(range(len(units)), units, unit_lengths):
        unit_multiplier *= unit_length
        unit_amount = math.floor(seconds / unit_multiplier)

        if unit_amount == 0 and index > 0:
            break

        if index + 1 < len(units):
            unit_amount %= unit_lengths[index + 1]

        output_string = f"{unit_amount}{unit_name} {output_string}"

    return output_string.strip()