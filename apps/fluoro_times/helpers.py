from .models import DOSE_CONV_FACTOR


def fluoro_dose_convert(fluoro_dose: float, dose_unit: str) -> float:
    """ Takes a fluoroscopy dose and dose unit and converts it to Gycm2

    :param fluoro_dose: The dose to convert
    :param dose_unit: The dose unit without the 2 indicating the square
    :return:
    """
    return fluoro_dose * DOSE_CONV_FACTOR[dose_unit.lower()]
