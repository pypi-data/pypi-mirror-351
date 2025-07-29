import multiprocessing
import re
from concurrent.futures import ProcessPoolExecutor
from math import ceil

import polars as pl
import us
import usaddress
from scourgify import normalize_address_record
from uszipcode import SearchEngine

from chainlink.cleaning.patterns import (
    abb_patterns as ABB_PATTERNS,
)
from chainlink.cleaning.patterns import (
    end_of_line_patterns as EOL_PATTERNS,
)
from chainlink.cleaning.patterns import (
    excluded_patterns as EXCLUDED_PATTERNS,
)
from chainlink.cleaning.patterns import (
    word_patterns as WORD_PATTERNS,
)
from chainlink.cleaning.usps_suffixes import suffixes

zip_cache: dict[str, dict[str, str]] = {}

state_names = [s.name for s in us.states.STATES_AND_TERRITORIES]
state_abbr = [s.abbr for s in us.states.STATES_AND_TERRITORIES]


def predict_org(name: str) -> int:
    """
    Given a string, predict whether or not the string is an organization name.

    Args:
        name (str): An entity name.

    Returns:
        int: 1 if the name is an organization, 0 if the name is an individual.
    """
    individual_names = re.compile(
        r"CURRENT OWNER|TAX PAYER OF|OWNER OF RECORD|PROPERTY OWNER",
        flags=re.IGNORECASE,
    )

    if (
        re.search("0-1", name)
        or re.search(ABB_PATTERNS, name)
        or re.search(WORD_PATTERNS, name)
        or re.search(EOL_PATTERNS, name)
    ):
        return 1

    # Doing this because GX PROPERTY OWNER LLC exists
    if re.search(individual_names, name):
        return 0

    else:
        return 0


def clean_zipcode(raw: str | int) -> str:
    """
    Modified from the function written by Anthony Moser of the deseguys project.

    Returns a 5-digit zipcode from a string.

    Args:
        raw (any): A zipcode.

    Returns:
        str: A 5-digit zipcode or an empty string.
    """
    try:
        zipcode = str(raw)[:5]
    except Exception:
        return ""
    else:
        return zipcode


def identify_state_city(zipcode: str) -> tuple:
    """
    Use zipcode to look up state and city info using the uszipcode API.

    Args:
        zipcode (str): A zipcode.

    Returns:
        tuple: A tuple of city and state, or (None, None) if the lookup failed.
    """
    zipcode = clean_zipcode(zipcode)
    try:
        if zipcode in zip_cache:
            zip_city = zip_cache[zipcode]["city"]
            zip_state = zip_cache[zipcode]["state"]

            return (zip_city, zip_state)

        else:
            engine = SearchEngine()
            zipcode_obj = engine.by_zipcode(int(zipcode))
            # zip_cache[zipcode] = zipcode

            zip_city = zipcode_obj.major_city.upper()
            zip_state = zipcode_obj.state

            zip_citystate = {"city": zip_city, "state": zip_state}
            zip_cache[zipcode] = zip_citystate

            return (zip_city, zip_state)

    # Handle cases where zip code is null or not a number
    except AttributeError:
        return (None, None)

    except TypeError:
        return (None, None)

    except ValueError:
        return (None, None)


def clean_address_batch(address_batch: list[str]) -> list[dict]:
    return [clean_address(addr) for addr in address_batch]


def clean_address_batch_parser(df_batch: pl.Series) -> pl.Series:
    # 2) Pull the batch into Python for parallel parsing
    addresses = df_batch.to_list()

    # 3) Spin up one process per core (or core-1)
    n_workers = multiprocessing.cpu_count()

    def chunk_list(lst: list, n_chunks: int) -> list[list]:
        chunk_size = ceil(len(lst) / n_chunks)
        return [lst[i : i + chunk_size] for i in range(0, len(lst), chunk_size)]

    chunks = chunk_list(addresses, n_workers)

    with ProcessPoolExecutor(max_workers=n_workers) as exe:
        results = exe.map(clean_address_batch, chunks)

    # Flatten the list of lists
    parsed_dicts = [item for sublist in results for item in sublist]

    # 4) Build a Polars DataFrame of the parsed results
    parsed_df = pl.DataFrame(
        parsed_dicts,
        schema={
            "raw": pl.String,
            "address_number": pl.String,
            "street_pre_directional": pl.String,
            "street_name": pl.String,
            "street_post_type": pl.String,
            "unit_type": pl.String,
            "unit_number": pl.String,
            "subaddress_type": pl.String,
            "subaddress_identifier": pl.String,
            "city": pl.String,
            "state": pl.String,
            "postal_code": pl.String,
            "street": pl.String,
        },
    )

    # 5) Re-attach the original address for the join key
    parsed_struct = parsed_df.select(pl.struct(pl.all()).alias("address_struct")).to_series(0)

    return parsed_struct


def clean_address(raw: str) -> dict:
    """
    Given a raw address, first conduct baseline address cleaning, then
    identify and return the components of the address. Where possible, infer
    correct city and state value from the zip code given.

    Args:
        raw (str): A raw address.

    Returns:
        dict: A dictionary of address components.
    """
    if not isinstance(raw, str) or raw == "":
        return {
            "raw": raw,
            "address_number": None,
            "street_pre_directional": None,
            "street_name": None,
            "street_post_type": None,
            "unit_type": None,
            "unit_number": None,
            "subaddress_type": None,
            "subaddress_identifier": None,
            "city": None,
            "state": None,
            "postal_code": None,
            "street": None,
            "address_norm": None,
        }

    FIELD_NAMES = [
        "AddressNumber",
        "StreetNamePreDirectional",
        "StreetName",
        "StreetNamePostType",
        "OccupancyType",
        "OccupancyIdentifier",
        "SubaddressType",
        "SubaddressIdentifier",
        "PlaceName",
        "StateName",
        "ZipCode",
    ]

    # remove spaces and punct
    raw_stripped = re.sub(r",|\.", "", raw).strip()
    # replace # with UNIT
    to_normalize = re.sub(r"#", " UNIT ", raw_stripped)
    # replace multiple spaces with single space
    to_normalize = re.sub(r"\s+", " ", to_normalize)

    try:
        normalized = normalize_address_record(to_normalize)
        normalized = " ".join(value for value in normalized.values() if value is not None)

    except Exception:
        normalized = to_normalize

    try:
        tags = usaddress.tag(normalized)
        tags = dict(tags[0])

    # retain any successfully parsed fields
    except usaddress.RepeatedLabelError as e:
        tags = {}

        for parsed_field in e.parsed_string:
            value, label = parsed_field

            if label in FIELD_NAMES:
                tags[label] = value

    record = {
        "raw": raw,
        "address_number": tags.get("AddressNumber"),
        "street_pre_directional": tags.get("StreetNamePreDirectional"),
        "street_name": tags.get("StreetName"),
        "street_post_type": tags.get("StreetNamePostType"),
        "unit_type": tags.get("OccupancyType"),
        "unit_number": tags.get("OccupancyIdentifier"),
        "subaddress_type": tags.get("SubaddressType"),
        "subaddress_identifier": tags.get("SubaddressIdentifier"),
        "city": tags.get("PlaceName"),
        "state": tags.get("StateName"),
        "postal_code": tags.get("ZipCode"),
        "address_norm": str(re.sub(r"[^a-zA-Z0-9]+", "", raw).upper()),
    }

    if record["city"] is not None:
        record["city"] = re.sub(r"[^A-z\s]", "", record["city"]).strip()

        if record["city"] == "":
            record["city"] = None

    if record["street_name"] is not None:
        record["street_name"] = re.sub(r",\.", "", record["street_name"]).strip()
        # Remove unit from street name for cases where the address parser
        # erroneously included it
        record["street_name"] = re.sub(r"UNIT.*", "", record["street_name"]).strip()
        if record["street_name"] == "":
            record["street_name"] = None

    if record["unit_number"] is not None:
        record["unit_number"] = re.sub(r"[^[A-z0-9]", "", record["unit_number"])

        if record["unit_number"] == "":
            record["unit_number"] = None

    # Overwrite city and state using uszip if the parsed state is not valid
    if record["state"] not in state_abbr or record["state"] is None:
        zip_city, zip_state = identify_state_city(record["postal_code"])

        # if don't find valid city, state, leave original
        if zip_city is not None:
            record["city"] = zip_city

        if zip_state is not None:
            record["state"] = zip_state

    street_fields = [
        "address_number",
        "street_pre_directional",
        "street_name",
        "street_post_type",
    ]
    record["street"] = " ".join([
        record[field] for field in street_fields if (record[field] is not None) and (record[field] != "")
    ])
    if (record["street"] == "") or (record["street"] == " "):
        record["street"] = None

    if suffixes.get(record["street_post_type"]):
        record["street_post_type"] = suffixes.get(record["street_post_type"])

    for key, value in record.items():
        record[key] = None if value == "" else value

    for k, v in record.items():
        if v is None:
            continue
        # Force everything to a Python string:
        if not isinstance(v, str):
            record[k] = str(v)

    return record


def remove_initial_I(raw: str) -> str:
    """
    Remove the "I" or I" present for some names in corporation
    and LLC data where name was incorrectly entered in the
    style of "I, John Smith" instead of just "John Smith"
    """
    if raw[:3] == '"I"':
        raw = raw[3:]
    if raw[:2] == 'I"':
        raw = raw[2:]
    return raw


def clean_names(raw: str) -> str | None:
    """
    Given a raw name string, clean the name and return it. Contains conditional
    logic based on the source of the data to handle data-specific cleaning cases.
    Returns none if the name resembles a list of excluded strings. Strips
    most non-alphanumeric characters.

    Args:
        raw (str): A raw name string.

    Returns:
        str: A cleaned name string.
    """

    if re.search(EXCLUDED_PATTERNS, raw):
        return None

    name = raw.upper()

    name = name.replace("&", "AND").replace("-", " ").replace("@", "AT").replace("—", " ")

    name = re.sub(r"[^a-zA-Z0-9\s]", "", name)
    name = re.sub(r"\s{2,}", " ", name)
    if (name == "") or (name == " "):
        return None
    else:
        return name
    return name
