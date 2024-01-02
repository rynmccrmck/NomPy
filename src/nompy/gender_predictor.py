import gzip
import logging
import os
from collections import defaultdict
from dataclasses import dataclass

import name_gender_pb2


logger = logging.getLogger()

ALL_CODE = 'ALL'
DIR_PATH = os.path.dirname(os.path.realpath(__file__))
FILENAME = f'{DIR_PATH}/data/name_gender_data_all.pb.gz'

@dataclass
class NameGender:
    name: str
    country_code: str
    gender: str
    p_male: float
    p_female: float
    confidence: float
    support: int

_all_records = None

import math

def calculate_confidence(p, support):
    # Calculate the deviation of p from 0.5 (the point of maximum uncertainty)
    prob_deviation = abs(p - 0.5) * 2  # This scales the deviation to be between 0 and 1

    # Use the logarithm of support to increase confidence with more data, but at a decreasing rate
    # Adding 1 to support to avoid log(0) when support is 0
    support_factor = math.log(support + 1)

    # Calculate the confidence as the product of the probability deviation and the logarithm of support
    confidence = prob_deviation * support_factor

    return confidence


# TODO warn on incorrect nationality iso code (pycountry)
def detect_gender(first_name: str, country_code: str = None) -> NameGender:
    record = _all_records.get(first_name)

    if not record:
        logger.debug('No data found for name', first_name)
        return None

    gender_data = None
    if record and country_code:
        gender_data = record.get(country_code)
    
    if not gender_data:
        logger.debug('No data found for country_code', country_code)
        gender_data = record.get(ALL_CODE)
    
    # TODO review these thresholds
    pct_male = gender_data.male_count / (gender_data.male_count + gender_data.female_count)
    if pct_male > 0.8:
        gender = 'male'
    elif pct_male > 0.6:
        gender = 'mostly_male'
    elif pct_male < 0.2:
        gender = 'female'
    elif pct_male < 0.4:
        gender = 'mostly_female'
    elif pct_male >= 0.4 and pct_male <= 0.6:
        gender = 'androgenous'
    else:
        gender = 'unknown'
    
    support = gender_data.male_count + gender_data.female_count
    confidence = calculate_confidence(max(pct_male, 1- pct_male), support)  # TODO review
    return NameGender(
        name=first_name,
        country_code=country_code,
        gender=gender,
        confidence=confidence,
        p_male=pct_male,
        p_female=1 - pct_male,
        support=support
    )


def _read_records(filename):
    global _all_records
    _all_records = defaultdict(dict)
    with gzip.open(filename, 'rb') as file:
        while True:
            size_bytes = file.read(4)
            if not size_bytes:
                break
            size = int.from_bytes(size_bytes, byteorder='little')
            record_data = file.read(size)
            record = name_gender_pb2.FirstNameGenderCount()
            record.ParseFromString(record_data)
            _all_records[record.first_name][record.country_code] = record
    return _all_records


_read_records(FILENAME)

