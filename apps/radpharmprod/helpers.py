from typing import List


def get_formatted_half_life(half_life: float):
    tmp_half_life = half_life
    half_life = []
    half_life_unit = []

    if tmp_half_life < 60:
        half_life.append(tmp_half_life)
        half_life_unit.append('s')
        return ' '.join(_format_half_life_strings(half_life, half_life_unit))

    minutes, seconds = divmod(tmp_half_life, 60)
    if seconds > 0:
        half_life.append(seconds)
        half_life_unit.append('s')

    if minutes < 60:
        half_life.append(minutes)
        half_life_unit.append('min')
        return ' '.join(_format_half_life_strings(half_life, half_life_unit))

    hours, minutes = divmod(minutes, 60)
    if minutes > 0:
        half_life.append(minutes)
        half_life_unit.append('min')

    if hours < 24:
        half_life.append(hours)
        half_life_unit.append('h')
        return ' '.join(_format_half_life_strings(half_life, half_life_unit))

    days, hours = divmod(hours, 24)
    if hours > 0:
        half_life.append(hours)
        half_life_unit.append('h')

    half_life.append(days)
    half_life_unit.append('d')

    return ' '.join(_format_half_life_strings(half_life, half_life_unit))


def _format_half_life_strings(half_life: List[float], half_life_unit: List[str]) -> List[str]:
    return [f'{half_life[ind]} {half_life_unit[ind]}' for ind in reversed(range(half_life))]
