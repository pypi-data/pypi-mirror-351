import os

import duckdb
import polars as pl
import pytest
from polars.testing import assert_frame_equal

from chainlink.main import chainlink, export_tables

# add pytest fixture

CONFIG_SIMPLE_1 = {
    "schema_name": "test_simple1",
    "tables": [
        {
            "table_name": "test1",
            "table_name_path": "tests/data/test1.csv",
            "id_col": "id",
            "name_cols": ["name"],
            "address_cols": ["address"],
        }
    ],
}

CONFIG_SIMPLE_2 = {
    "schema_name": "test_simple2",
    "tables": [
        {
            "table_name": "test2",
            "table_name_path": "tests/data/test2.csv",
            "id_col": "id",
            "name_cols": ["name"],
            "address_cols": ["address"],
        }
    ],
}

CONFIG_SIMPLE_MISSING_SCHEMA = {
    "schema_name": "test_simple2",
    "tables": [
        {
            "table_name": "test2",
            "table_name_path": "tests/data/test2.csv",
            "id_col": "id",
            "name_cols": ["name"],
            "address_cols": ["address", "mailing_address"],
        }
    ],
}


CONFIG_SIMPLE = {
    "options": {
        "db_path": "tests/db/test_simple.db",
        "overwrite_db": True,
        "probabilistic": True,
    },
    "schemas": [CONFIG_SIMPLE_1, CONFIG_SIMPLE_2],
}

CONFIG_SIMPLE_CROSS_SCHEMA = {
    "schema_name": "test_simple1",
    "tables": [
        {
            "table_name": "test1",
            "table_name_path": "tests/data/test1_cross.csv",
            "id_col": "id",
            "name_cols": ["name1", "name2"],
            "address_cols": ["address"],
        },
        {
            "table_name": "test2",
            "table_name_path": "tests/data/test2_cross.csv",
            "id_col": "id",
            "name_cols": ["name1", "name2"],
            "address_cols": ["address"],
        },
    ],
}

CONFIG_SIMPLE_CROSS = {
    "options": {
        "db_path": "tests/db/test_simple_cross.db",
        "overwrite_db": True,
        "probabilistic": True,
    },
    "schemas": [CONFIG_SIMPLE_CROSS_SCHEMA],
}

CONFIG_SIMPLE_MISSING = {
    "options": {
        "db_path": "tests/db/test_simple.db",
        "overwrite_db": True,
        "probabilistic": True,
    },
    "schemas": [CONFIG_SIMPLE_1, CONFIG_SIMPLE_MISSING_SCHEMA],
}

CONFIG_SMALL_LLC = {
    "schema_name": "llc",
    "tables": [
        {
            "table_name": "master",
            "table_name_path": "tests/data/small_llc.csv",
            "id_col": "file_num",
            "name_cols": ["name_raw"],
            "address_cols": ["address"],
        }
    ],
}

CONFIG_SMALL_PARCEL = {
    "schema_name": "parcel",
    "tables": [
        {
            "table_name": "parcels",
            "table_name_path": "tests/data/small_parcel.csv",
            "id_col": "pin",
            "name_cols": ["tax_payer_name"],
            "address_cols": ["mailing_address"],
        }
    ],
}

CONFIG_SMALL = {
    "options": {
        "db_path": "tests/db/test_small.db",
        "overwrite_db": True,
        "probabilistic": True,
    },
    "schemas": [CONFIG_SMALL_LLC, CONFIG_SMALL_PARCEL],
}

CONFIG_SMALL_LINK_EXCLUSION = {
    "options": {
        "db_path": "tests/db/test_small_link_exclusion.db",
        "overwrite_db": True,
        "probabilistic": True,
        "link_exclusions": ["parcel_parcel_tax_payer_name_parcel_parcel_tax_payer_name_name_match"],
    },
    "schemas": [CONFIG_SMALL_LLC, CONFIG_SMALL_PARCEL],
}


CONFIG_TWO_COLUMNS_SCHEMA = {
    "schema_name": "two_columns",
    "tables": [
        {
            "table_name": "test",
            "table_name_path": "tests/data/two_columns.csv",
            "id_col": "file_num",
            "name_cols": ["name", "name2"],
            "address_cols": ["address", "address2"],
        }
    ],
}

CONFIG_TWO_COLUMNS = {
    "options": {
        "db_path": "tests/db/test_two_columns.db",
        "overwrite_db": True,
        "probabilistic": True,
    },
    "schemas": [CONFIG_TWO_COLUMNS_SCHEMA],
}


CONFIG_MULTIPLE_TABLES_SCHEMA = {
    "schema_name": "multiple_tables",
    "tables": [
        {
            "table_name": "multiple1",
            "table_name_path": "tests/data/multiple1.csv",
            "id_col": "file_num",
            "name_cols": ["name"],
            "address_cols": ["address"],
        },
        {
            "table_name": "multiple2",
            "table_name_path": "tests/data/multiple2.csv",
            "id_col": "file_num",
            "name_cols": ["name"],
            "address_cols": ["address"],
        },
    ],
}

CONFIG_MULTIPLE_TABLES = {
    "options": {
        "db_path": "tests/db/test_multiple_tables.db",
        "overwrite_db": True,
        "probabilistic": True,
    },
    "schemas": [CONFIG_MULTIPLE_TABLES_SCHEMA],
}


@pytest.fixture
def make_simple_db():
    if os.path.exists("tests/db/test_simple.db"):
        os.remove("tests/db/test_simple.db")

    pl.DataFrame({
        "id": ["1", "2", "3", "4"],
        "name": ["Aus St", "Big Calm", "Cool Cool", "Aus St"],
        "address": ["1", "2", "3", "4"],
        "skip_address": [0, 0, 0, 0],
    }).write_csv("tests/data/test1.csv")
    pl.DataFrame({
        "id": ["5", "6", "7", "8"],
        "name": ["Aus St", "Erie Erie", "Cool Cool", "Good Doom"],
        "address": ["5", "6", "3", "4"],
        "skip_address": [0, 0, 0, 0],
    }).write_csv("tests/data/test2.csv")

    chainlink(
        CONFIG_SIMPLE,
        config_path="tests/configs/config_simple.yaml",
    )


@pytest.fixture
def make_simple_cross_db():
    if os.path.exists("tests/db/test_simple_cross.db"):
        os.remove("tests/db/test_simple_cross.db")

    pl.DataFrame({
        "id": ["1", "2", "3", "4"],
        "name1": ["Aus St", "Big Calm", "Cool Cool", "Aus St"],
        "name2": ["Big Calm", "Aus St", "Cool Cool", "Aus St"],
        "address": ["1", "2", "3", "4"],
        "skip_address": [0, 0, 0, 0],
    }).write_csv("tests/data/test1_cross.csv")
    pl.DataFrame({
        "id": ["5", "1", "7", "8"],
        "name1": ["Aus St", "Cool Cool", "Cool Cool", "Good Doom"],
        "name2": ["Aus St", "Erie Erie", "Cool Cool", "Good Doom"],
        "address": ["5", "6", "7", "8"],
        "skip_address": [0, 0, 0, 0],
    }).write_csv("tests/data/test2_cross.csv")

    chainlink(
        CONFIG_SIMPLE_CROSS,
        config_path="tests/configs/config_simple_cross.yaml",
    )


@pytest.fixture
def make_small_db():
    # test_small.db exists, then delete the db
    if os.path.exists("tests/db/test_small.db"):
        os.remove("tests/db/test_small.db")

    pl.DataFrame({
        "pin": [
            "20344100300000",
            "24171070561019",
            "25212140150000",
            "25022160020000",
            "25022160020001",
            "25022160020002",
        ],
        "tax_payer_name": [
            "SANJAY PATEL",
            "GRONKA PROPERTIES INC",
            "MOBUCASA INC",
            "TAXPAYER OF",
            "NAPERVILLE BITES AND SITE , LLC",
            "TAXPAYER OF",
        ],
        "mailing_address": [
            "645 LEAMINGTON, WILMETTE, IL 60091",
            "8041 SAYRE AVE, BURBANK, IL 60459",
            "1212 S NAPER BLVD 119, NAPERVILLE, IL 60540",
            "1319 E 89TH ST, CHICAGO, IL 60619",
            "2555 W. 79TH ST. APT 5 CHICAGO IL 60652",
            "8041 SAYRE AVE, BURBANK, IL 60459",
        ],
        "skip_address": [0, 0, 0, 0, 0, 0],
    }).write_csv("tests/data/small_parcel.csv")

    pl.DataFrame({
        "file_num": [
            1338397,
            1127901,
            325194,
            717605,
            257730,
        ],
        "name_raw": [
            "WOOW HVAC LLC",
            "MOBUCASA INC",
            "WOOW HVAC LLC",
            "SANJAY PATEL",
            "NAPERVILLE BITES AND SITES , LLC",
        ],
        "address": [
            "645 LEAMINGTON, WILMETTE, IL 60091",
            "",
            "2555 W. 79TH ST. CHICAGO IL 60652",
            "8041 SAYRE AVE, BURBANK, IL 60459",
            "1319 E 89TH ST. CHICAGO IL 60638",
        ],
        "skip_address": [0, 0, 0, 0, 0],
    }).write_csv("tests/data/small_llc.csv")

    chainlink(
        CONFIG_SMALL,
        config_path="tests/configs/config_small.yaml",
    )


@pytest.fixture
def make_small_db_link_exclusion():
    # test_small.db exists, then delete the db
    if os.path.exists("tests/db/test_small_link_exclusion.db"):
        os.remove("tests/db/test_small_link_exclusion.db")

    pl.DataFrame({
        "pin": [
            "20344100300000",
            "24171070561019",
            "25212140150000",
            "25022160020000",
            "25022160020001",
            "25022160020002",
        ],
        "tax_payer_name": [
            "SANJAY PATEL",
            "GRONKA PROPERTIES INC",
            "MOBUCASA INC",
            "TAXPAYER OF",
            "NAPERVILLE BITES AND SITE , LLC",
            "TAXPAYER OF",
        ],
        "mailing_address": [
            "645 LEAMINGTON, WILMETTE, IL 60091",
            "8041 SAYRE AVE, BURBANK, IL 60459",
            "1212 S NAPER BLVD 119, NAPERVILLE, IL 60540",
            "1319 E 89TH ST, CHICAGO, IL 60619",
            "2555 W. 79TH ST. APT 5 CHICAGO IL 60652",
            "8041 SAYRE AVE, BURBANK, IL 60459",
        ],
        "skip_address": [0, 0, 0, 0, 0, 0],
    }).write_csv("tests/data/small_parcel.csv")

    pl.DataFrame({
        "file_num": [
            1338397,
            1127901,
            325194,
            717605,
            257730,
        ],
        "name_raw": [
            "WOOW HVAC LLC",
            "MOBUCASA INC",
            "WOOW HVAC LLC",
            "SANJAY PATEL",
            "NAPERVILLE BITES AND SITES , LLC",
        ],
        "address": [
            "645 LEAMINGTON, WILMETTE, IL 60091",
            "",
            "2555 W. 79TH ST. CHICAGO IL 60652",
            "8041 SAYRE AVE, BURBANK, IL 60459",
            "1319 E 89TH ST. CHICAGO IL 60638",
        ],
        "skip_address": [0, 0, 0, 0, 0],
    }).write_csv("tests/data/small_llc.csv")

    chainlink(
        CONFIG_SMALL_LINK_EXCLUSION,
        config_path="tests/configs/config_small_link_exclusions.yaml",
    )


@pytest.fixture
def make_two_column_db():
    # if exists, then delete the db
    if os.path.exists("tests/db/test_two_column.db"):
        os.remove("tests/db/test_two_column.db")

    pl.DataFrame({
        "file_num": [
            "1001",
            "1002",
            "1003",
            "1004",
            "1005",
        ],
        "name": [
            "SMITH ENTERPRISES",
            "JOHNSON HOLDINGS LLC",
            "ANDERSON CONSULTING",
            "WILSON PROPERTIES",
            "ANOTHER NAME",
        ],
        "name2": [
            "ROBERT SMITH",
            "MICHAEL JOHNSON",
            "JENNIFER ANDERSON",
            "JOHNSON HOLDINGS LLC",
            "SARAH TAYLOR",
        ],
        "address": [
            "565 MAIN AVE, CHICAGO, IL 60601",
            "456 OAK AVE, EVANSTON, IL 60201",
            "789 PINE BLVD, NAPERVILLE, IL 60540",
            "321 ELM DR, SKOKIE, IL 60077",
            "100 MAPLE RD, AURORA, IL 60506",
        ],
        "address2": [
            "100 MAPLE ROAD, AURORA, IL 60506",
            "200 LAKE AVE, EVANSTON, IL 60202",
            "565 MAIN ST, CHICAGO, IL 60601",
            "400 CENTRAL AVE, SKOKIE, IL 60076",
            "321 ELM DR, SKOKIE, IL 60077",
        ],
        "skip_address": [0, 0, 0, 0, 0],
    }).write_csv("tests/data/two_columns.csv")

    chainlink(
        CONFIG_TWO_COLUMNS,
        config_path="tests/configs/config_two_columns.yaml",
    )


@pytest.fixture
def make_multiple_tables_db():
    # if exists, then delete the db
    if os.path.exists("tests/db/test_multiple_tables.db"):
        os.remove("tests/db/test_multiple_tables.db")

    pl.DataFrame({
        "file_num": [
            "1001",
            "1002",
            "1003",
            "1004",
            "1005",
        ],
        "name": [
            "SMITH ENTERPRISES",
            "JOHNSON HOLDINGS LLC",
            "ANDERSON CONSULTING",
            "WILSON PROPERTIES",
            "ANOTHER NAME",
        ],
        "address": [
            "565 MAIN AVE, CHICAGO, IL 60601",
            "456 OAK AVE, EVANSTON, IL 60201",
            "789 PINE BLVD, NAPERVILLE, IL 60540",
            "321 ELM DR, SKOKIE, IL 60077",
            "100 MAPLE RD, AURORA, IL 60506",
        ],
        "skip_address": [0, 0, 0, 0, 0],
    }).write_csv("tests/data/multiple1.csv")

    pl.DataFrame({
        "file_num": [
            "1001",
            "1022",
            "1003",
            "1044",
            "1055",
        ],
        "name": [
            "SUMMIT INNOVATIONS",
            "JOHNSON HOLDINGS LLC",  # This name is kept
            "PINNACLE CONSULTING",
            "RIVERSTONE PROPERTIES",
            "EVERGREEN VENTURES",
        ],
        "address": [
            "123 LAKE SHORE DR, CHICAGO, IL 60611",
            "456 OAK AVE, EVANSTON, IL 60201",  # This address is kept
            "500 UNIVERSITY AVE, NAPERVILLE, IL 60540",
            "742 MAPLE ST, SKOKIE, IL 60077",
            "321 ELM DR, SKOKIE, IL 60077",
        ],
        "skip_address": [0, 0, 0, 0, 0],
    }).write_csv("tests/data/multiple2.csv")

    chainlink(
        CONFIG_MULTIPLE_TABLES,
        config_path="tests/configs/config_multiple_tables.yaml",
    )


def test_simple_exact_within(make_simple_db):
    with duckdb.connect("tests/db/test_simple.db", read_only=True) as db_conn:
        query = "SELECT * FROM link.test_simple1_test_simple1"
        df = db_conn.execute(query).pl()

    # one match
    assert df.shape[0] == 1

    # id_1,
    # id_2,
    # test_simple1_test1_name_test_simple1_test1_name_name_match,
    # test_simple1_test1_address_test_simple1_test1_address_street_fuzzy_match
    # test_simple1_test1_address_test_simple1_test1_address_unit_fuzzy_match
    # test_simple1_test1_name_test_simple1_test1_name_fuzzy_match,
    # test_simple1_test1_address_test_simple1_test1_address_address_match,
    # test_simple1_test1_address_test_simple1_test1_address_street_match,
    # test_simple1_test1_address_test_simple1_test1_address_unit_match,
    # test_simple1_test1_address_test_simple1_test1_address_street_num_match
    assert df.shape[1] == 9


def test_simple_exact_across(make_simple_db):
    with duckdb.connect("tests/db/test_simple.db", read_only=True) as db_conn:
        query = "SELECT * FROM link.test_simple1_test_simple2"
        df = db_conn.execute(query).pl()

    # one match
    assert df.shape[0] == 4

    # test1_id,
    # test2_id,
    # test_simple1_test1_name_test_simple2_test2_name_name_match,
    # test_simple1_test1_name_test_simple2_test2_name_fuzzy_match,
    # test_simple1_test1_address_test_simple2_test2_address_address_match,
    # test_simple1_test1_address_test_simple2_test2_address_street_match,
    # test_simple1_test1_address_test_simple2_test2_address_street_fuzzy_match,
    # test_simple1_test1_address_test_simple2_test2_address_unit_match,
    # test_simple1_test1_address_test_simple2_test2_address_unit_fuzzy_match,
    # test_simple1_test1_address_test_simple2_test2_address_street_num_match
    assert df.shape[1] == 9


def test_small_entity_tables(make_small_db):
    db_path = "tests/db/test_small.db"
    with duckdb.connect(db_path, read_only=True) as db_conn:
        query = "SELECT * FROM entity.name"
        df = db_conn.execute(query).pl()
        assert df.shape[0] == 7

        query = "SELECT * FROM entity.address"
        df = db_conn.execute(query).pl()
        assert df.shape[0] == 8

        query = "SELECT * FROM entity.street"
        df = db_conn.execute(query).pl()
        assert df.shape[0] == 6


def test_small_exact_within(make_small_db):
    db_path = "tests/db/test_small.db"
    with duckdb.connect(db_path, read_only=True) as db_conn:
        query = "SELECT * FROM link.llc_llc"
        df = db_conn.execute(query).pl()

        correct_df = pl.DataFrame({
            "llc_file_num_1": ["1338397"],
            "llc_file_num_2": ["325194"],
            "llc_master_address_llc_master_address_unit_fuzzy_match": [0.0],
            "llc_master_address_llc_master_address_street_fuzzy_match": [0.0],
            "llc_master_name_raw_llc_master_name_raw_fuzzy_match": [0.0],
            "llc_master_name_raw_llc_master_name_raw_name_match": [1],
            "llc_master_address_llc_master_address_address_match": [0],
            "llc_master_address_llc_master_address_street_match": [0],
            "llc_master_address_llc_master_address_unit_match": [0],
        })
        # for row in df.rows():
        #     print(row)

        # one match
        assert df.shape[0] == 1
        assert df.shape[1] == 9
        assert_frame_equal(correct_df, df, check_column_order=False, check_dtypes=False)

        query = "SELECT * FROM link.parcel_parcel"
        df = db_conn.execute(query).pl()

        correct_df = pl.DataFrame({
            "parcel_pin_1": ["24171070561019"],
            "parcel_pin_2": ["25022160020002"],
            "parcel_parcels_mailing_address_parcel_parcels_mailing_address_unit_fuzzy_match": [0.0],
            "parcel_parcels_mailing_address_parcel_parcels_mailing_address_street_fuzzy_match": [0.0],
            "parcel_parcels_tax_payer_name_parcel_parcels_tax_payer_name_fuzzy_match": [0.0],
            "parcel_parcels_tax_payer_name_parcel_parcels_tax_payer_name_name_match": [0],
            "parcel_parcels_mailing_address_parcel_parcels_mailing_address_address_match": [1],
            "parcel_parcels_mailing_address_parcel_parcels_mailing_address_street_match": [1],
            "parcel_parcels_mailing_address_parcel_parcels_mailing_address_unit_match": [0],
        })

        # one match
        assert df.shape[0] == 1
        # on within fuzzy match
        assert df.shape[1] == 9
        assert_frame_equal(correct_df, df, check_column_order=False, check_dtypes=False)


def test_small_exact_across(make_small_db):
    db_path = "tests/db/test_small.db"

    with duckdb.connect(db_path, read_only=True) as db_conn:
        query = "SELECT * FROM link.llc_parcel"
        df = db_conn.execute(query).pl()

    correct_df = pl.DataFrame({
        "llc_file_num": [
            "325194",
            "717605",
            "1127901",
            "257730",
            "1338397",
            "717605",
            "717605",
            "257730",
        ],
        "parcel_pin": [
            "25022160020001",
            "20344100300000",
            "25212140150000",
            "25022160020000",
            "20344100300000",
            "25022160020002",
            "24171070561019",
            "25022160020001",
        ],
        "llc_master_address_parcel_parcels_mailing_address_unit_fuzzy_match": [
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
        ],
        "llc_master_address_parcel_parcels_mailing_address_street_fuzzy_match": [
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
        ],
        "llc_master_name_raw_parcel_parcels_tax_payer_name_fuzzy_match": [
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.9805094416874218,
        ],
        "llc_master_name_raw_parcel_parcels_tax_payer_name_name_match": [
            0,
            1,
            1,
            0,
            0,
            0,
            0,
            0,
        ],
        "llc_master_address_parcel_parcels_mailing_address_address_match": [
            0,
            0,
            0,
            0,
            1,
            1,
            1,
            0,
        ],
        "llc_master_address_parcel_parcels_mailing_address_street_match": [
            1,
            0,
            0,
            1,
            1,
            1,
            1,
            0,
        ],
        "llc_master_address_parcel_parcels_mailing_address_unit_match": [
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
        ],
    })

    # eight matches
    assert df.shape[0] == 8
    assert df.shape[1] == 9
    assert_frame_equal(
        correct_df.sort(["llc_file_num", "parcel_pin"]),
        df.sort(["llc_file_num", "parcel_pin"]),
        check_column_order=False,
        check_dtypes=False,
    )


def test_small_fuzzy(make_small_db):
    db_path = "tests/db/test_small.db"

    with duckdb.connect(db_path, read_only=True) as db_conn:
        query = "SELECT * FROM link.llc_parcel"
        df = db_conn.execute(query).pl()

    # Create a DataFrame with the test data
    correct_df = pl.DataFrame({
        "llc_file_num": ["257730"],
        "parcel_pin": ["25022160020001"],
        "llc_master_address_parcel_parcels_mailing_address_unit_fuzzy_match": [0.0],
        "llc_master_address_parcel_parcels_mailing_address_street_fuzzy_match": [0.0],
        "llc_master_name_raw_parcel_parcels_tax_payer_name_fuzzy_match": [0.9805094416874218],
        "llc_master_name_raw_parcel_parcels_tax_payer_name_name_match": [0],
        "llc_master_address_parcel_parcels_mailing_address_address_match": [0],
        "llc_master_address_parcel_parcels_mailing_address_street_match": [0],
        "llc_master_address_parcel_parcels_mailing_address_unit_match": [0],
    })

    # one fuzzy match
    df_test = df.filter(pl.col("llc_master_name_raw_parcel_parcels_tax_payer_name_fuzzy_match") > 0)
    assert df_test.shape[0] == 1
    assert_frame_equal(df_test, correct_df, check_column_order=False, check_dtypes=False)


def test_small_link_exclusion(make_small_db_link_exclusion):
    db_path = "tests/db/test_small_link_exclusion.db"

    with duckdb.connect(db_path, read_only=True) as db_conn:
        query = "SELECT * FROM link.parcel_parcel"
        df = db_conn.execute(query).pl()

    assert "parcel_tax_payer_name_parcel_parcel_tax_payer_name_name_match" not in df.columns


def test_two_columns(make_two_column_db):
    db_path = "tests/db/test_two_columns.db"

    with duckdb.connect(db_path, read_only=True) as db_conn:
        query = "SELECT * FROM link.two_columns_two_columns"
        links = db_conn.execute(query).pl()

        query = "SELECT * FROM two_columns.test"
        df = db_conn.execute(query).pl()

    # Verify each expected column exists in the DataFrame
    assert "name" in df.columns
    assert "name2" in df.columns
    assert "address" in df.columns
    assert "address2" in df.columns

    assert links.shape[0] == 3


def test_multiple_tables(make_multiple_tables_db):
    db_path = "tests/db/test_multiple_tables.db"

    with duckdb.connect(db_path, read_only=True) as db_conn:
        query = "SELECT * FROM link.multiple_tables_multiple_tables"
        links = db_conn.execute(query).pl()

        query = "show all tables"
        all_df = db_conn.execute(query).pl()

    # confirm multiple1 and multiple2 tables exist
    assert all_df.filter(pl.col("name").is_in(["multiple1", "multiple2"])).shape[0] == 2

    assert links.shape[0] == 2


def test_col_not_in_file():
    if os.path.exists("tests/db/test_simple_missing.db"):
        os.remove("tests/db/test_simple_missing.db")

    pl.DataFrame({
        "id": ["1", "2", "3", "4"],
        "name": ["Aus St", "Big Calm", "Cool Cool", "Aus St"],
        "address": ["1", "2", "3", "4"],
        "skip_address": [0, 0, 0, 0],
    }).write_csv("tests/data/test1.csv")
    pl.DataFrame({
        "id": ["5", "6", "7", "8"],
        "name": ["Aus St", "Erie Erie", "Cool Cool", "Good Doom"],
        "address": ["5", "6", "3", "4"],
        "skip_address": [0, 0, 0, 0],
    }).write_csv("tests/data/test2.csv")

    with pytest.raises(ValueError):
        chainlink(
            CONFIG_SIMPLE_MISSING,
            config_path="tests/configs/config_simple_missing.yaml",
        )


def test_export_tables():
    export_tables("tests/db/test_small.db", "tests/export")

    assert pl.scan_parquet("tests/export/link_llc_llc.parquet").collect().shape[0] == 1
    assert pl.scan_parquet("tests/export/link_llc_parcel.parquet").collect().shape[0] == 8
    assert pl.scan_parquet("tests/export/link_parcel_parcel.parquet").collect().shape[0] == 1


def test_not_force_db():
    CONFIG_SIMPLE_1_AMENDED = {
        "schema_name": "test_simple1",
        "tables": [
            {
                "table_name": "test1",
                "table_name_path": "tests/data/test1.csv",
                "id_col": "id",
                "name_cols": ["name"],
                "address_cols": [],
            }
        ],
    }

    CONFIG_SIMPLE_PT1 = {
        "options": {
            "db_path": "tests/db/test_force_db.db",
            "overwrite_db": True,
            "probabilistic": True,
        },
        "schemas": [CONFIG_SIMPLE_1],
    }
    CONFIG_SIMPLE_PT2_A = {
        "options": {
            "db_path": "tests/db/test_force_db.db",
            "overwrite_db": False,
            "probabilistic": True,
        },
        "schemas": [CONFIG_SIMPLE_1, CONFIG_SIMPLE_2],
    }

    CONFIG_SIMPLE_PT2_B = {
        "options": {
            "db_path": "tests/db/test_force_db.db",
            "overwrite_db": False,
            "probabilistic": True,
        },
        "schemas": [CONFIG_SIMPLE_1_AMENDED, CONFIG_SIMPLE_2],
    }

    CONFIG_SIMPLE_PT3 = {
        "options": {
            "db_path": "tests/db/test_force_db.db",
            "overwrite_db": True,
            "probabilistic": True,
        },
        "schemas": [CONFIG_SIMPLE_1_AMENDED, CONFIG_SIMPLE_2],
    }

    chainlink(
        CONFIG_SIMPLE_PT1,
        config_path="tests/configs/config_force_db.yaml",
    )

    # check if db exists
    assert os.path.exists("tests/db/test_force_db.db")
    # check if table exists
    with duckdb.connect("tests/db/test_force_db.db", read_only=True) as db_conn:
        query = "SHOW ALL TABLES"
        df = db_conn.execute(query).pl()
    assert df.filter(pl.col("schema") == "link").shape[0] == 1
    assert df.filter(pl.col("schema") == "test_simple1").shape[0] == 1
    assert df.filter(pl.col("schema") == "test_simple2").shape[0] == 0
    list_of_link_cols = df.filter(pl.col("schema") == "link").select("column_names").item()
    assert len(list_of_link_cols) == 9

    chainlink(
        CONFIG_SIMPLE_PT2_A,
        config_path="tests/configs/config_force_db.yaml",
    )

    assert os.path.exists("tests/db/test_force_db.db")
    # check if table exists
    with duckdb.connect("tests/db/test_force_db.db", read_only=True) as db_conn:
        query = "SHOW ALL TABLES"
        df = db_conn.execute(query).pl()
    assert df.filter(pl.col("schema") == "link").shape[0] == 3
    assert df.filter(pl.col("schema") == "test_simple1").shape[0] == 1
    assert df.filter(pl.col("schema") == "test_simple2").shape[0] == 1
    list_of_link_cols = (
        df.filter((pl.col("schema") == "link") & (pl.col("name") == "test_simple1_test_simple1"))
        .select("column_names")
        .item()
    )
    assert len(list_of_link_cols) == 9

    chainlink(
        CONFIG_SIMPLE_PT2_B,
        config_path="tests/configs/config_force_db.yaml",
    )

    assert os.path.exists("tests/db/test_force_db.db")
    # check if table exists
    with duckdb.connect("tests/db/test_force_db.db", read_only=True) as db_conn:
        query = "SHOW ALL TABLES"
        df = db_conn.execute(query).pl()
    assert df.filter(pl.col("schema") == "link").shape[0] == 3
    assert df.filter(pl.col("schema") == "test_simple1").shape[0] == 1
    assert df.filter(pl.col("schema") == "test_simple2").shape[0] == 1
    list_of_link_cols = (
        df.filter((pl.col("schema") == "link") & (pl.col("name") == "test_simple1_test_simple1"))
        .select("column_names")
        .item()
    )
    assert len(list_of_link_cols) == 9

    chainlink(
        CONFIG_SIMPLE_PT3,
        config_path="tests/configs/config_force_db.yaml",
    )

    assert os.path.exists("tests/db/test_force_db.db")
    # check if table exists
    with duckdb.connect("tests/db/test_force_db.db", read_only=True) as db_conn:
        query = "SHOW ALL TABLES"
        df = db_conn.execute(query).pl()
    assert df.filter(pl.col("schema") == "link").shape[0] == 3
    assert df.filter(pl.col("schema") == "test_simple1").shape[0] == 1
    assert df.filter(pl.col("schema") == "test_simple2").shape[0] == 1
    list_of_link_cols = (
        df.filter((pl.col("schema") == "link") & (pl.col("name") == "test_simple1_test_simple1"))
        .select("column_names")
        .item()
    )
    assert len(list_of_link_cols) == 4


def test_simple_cross(make_simple_cross_db):
    db_path = "tests/db/test_simple_cross.db"
    with duckdb.connect(db_path, read_only=True) as db_conn:
        query = "SELECT * FROM link.test_simple1_test_simple1"
        df = db_conn.execute(query).pl()

    assert df.shape[0] == 9  # 1-2, 1-4, 2-4, 1-5, 2-5, 4-5, 3-7, 1-3, 1-7
    num_columns = (
        2  # id columns
        + 4  # name to name within table 1
        + 4  # name to name fuzzy within table 1
        + 4  # name to name within table 2
        + 4  # name to name fuzzy within table 2
        + 2  # table 1 name 1 to table 2 name 1 + fuzzy
        + 2  # table 1 name 1 to table 2 name 2 + fuzzy
        + 2  # table 1 name 2 to table 2 name 1 + fuzzy
        + 2  # table 1 name 2 to table 2 name 2 + fuzzy
        + 8  # all above reversed
        + 3  # address to address within table 1
        + 2  # address to address fuzzy within table 1
        + 3  # address to address within table 2
        + 2  # address to address fuzzy within table 2
        + 5  # table 1 address to table 2 address + fuzzy
        + 5  # table 2 address to table 1 address + fuzzy
    )
    for col in df.columns:
        if "name_match" in col:
            print(col)

    assert df.shape[1] == num_columns

    assert df.filter((pl.col("test_simple1_id_1") == "1") & (pl.col("test_simple1_id_2") == "2")).select(
        pl.concat_list(
            pl.col("test_simple1_test1_name1_test_simple1_test1_name1_name_match"),
            pl.col("test_simple1_test1_name1_test_simple1_test1_name2_name_match"),
            pl.col("test_simple1_test1_name2_test_simple1_test1_name1_name_match"),
            pl.col("test_simple1_test1_name2_test_simple1_test1_name2_name_match"),
        )
    ).item().to_list() == [
        0,
        1,
        1,
        0,
    ]

    assert df.filter((pl.col("test_simple1_id_1") == "1") & (pl.col("test_simple1_id_2") == "4")).select(
        pl.concat_list(
            pl.col("test_simple1_test1_name1_test_simple1_test1_name1_name_match"),
            pl.col("test_simple1_test1_name1_test_simple1_test1_name2_name_match"),
            pl.col("test_simple1_test1_name2_test_simple1_test1_name1_name_match"),
            pl.col("test_simple1_test1_name2_test_simple1_test1_name2_name_match"),
        )
    ).item().to_list() == [
        1,
        1,
        0,
        0,
    ]

    assert df.filter((pl.col("test_simple1_id_1") == "2") & (pl.col("test_simple1_id_2") == "4")).select(
        pl.concat_list(
            pl.col("test_simple1_test1_name1_test_simple1_test1_name1_name_match"),
            pl.col("test_simple1_test1_name1_test_simple1_test1_name2_name_match"),
            pl.col("test_simple1_test1_name2_test_simple1_test1_name1_name_match"),
            pl.col("test_simple1_test1_name2_test_simple1_test1_name2_name_match"),
        )
    ).item().to_list() == [
        0,
        0,
        1,
        1,
    ]

    assert df.filter((pl.col("test_simple1_id_1") == "1") & (pl.col("test_simple1_id_2") == "5")).select(
        pl.concat_list(
            pl.col("test_simple1_test1_name1_test_simple1_test2_name1_name_match"),
            pl.col("test_simple1_test1_name1_test_simple1_test2_name2_name_match"),
            pl.col("test_simple1_test1_name2_test_simple1_test2_name1_name_match"),
            pl.col("test_simple1_test1_name2_test_simple1_test2_name2_name_match"),
        )
    ).item().to_list() == [
        1,
        1,
        0,
        0,
    ]

    assert df.filter((pl.col("test_simple1_id_1") == "2") & (pl.col("test_simple1_id_2") == "5")).select(
        pl.concat_list(
            pl.col("test_simple1_test1_name1_test_simple1_test2_name1_name_match"),
            pl.col("test_simple1_test1_name1_test_simple1_test2_name2_name_match"),
            pl.col("test_simple1_test1_name2_test_simple1_test2_name1_name_match"),
            pl.col("test_simple1_test1_name2_test_simple1_test2_name2_name_match"),
        )
    ).item().to_list() == [
        0,
        0,
        1,
        1,
    ]

    assert df.filter((pl.col("test_simple1_id_1") == "4") & (pl.col("test_simple1_id_2") == "5")).select(
        pl.concat_list(
            pl.col("test_simple1_test1_name1_test_simple1_test2_name1_name_match"),
            pl.col("test_simple1_test1_name1_test_simple1_test2_name2_name_match"),
            pl.col("test_simple1_test1_name2_test_simple1_test2_name1_name_match"),
            pl.col("test_simple1_test1_name2_test_simple1_test2_name2_name_match"),
        )
    ).item().to_list() == [
        1,
        1,
        1,
        1,
    ]

    assert df.filter((pl.col("test_simple1_id_1") == "3") & (pl.col("test_simple1_id_2") == "7")).select(
        pl.concat_list(
            pl.col("test_simple1_test1_name1_test_simple1_test2_name1_name_match"),
            pl.col("test_simple1_test1_name1_test_simple1_test2_name2_name_match"),
            pl.col("test_simple1_test1_name2_test_simple1_test2_name1_name_match"),
            pl.col("test_simple1_test1_name2_test_simple1_test2_name2_name_match"),
        )
    ).item().to_list() == [
        1,
        1,
        1,
        1,
    ]

    assert df.filter((pl.col("test_simple1_id_1") == "1") & (pl.col("test_simple1_id_2") == "7")).select(
        pl.concat_list(
            pl.col("test_simple1_test2_name1_test_simple1_test2_name1_name_match"),
            pl.col("test_simple1_test2_name1_test_simple1_test2_name2_name_match"),
            pl.col("test_simple1_test2_name2_test_simple1_test2_name1_name_match"),
            pl.col("test_simple1_test2_name2_test_simple1_test2_name2_name_match"),
        )
    ).item().to_list() == [
        1,
        1,
        0,
        0,
    ]

    assert df.filter((pl.col("test_simple1_id_1") == "1") & (pl.col("test_simple1_id_2") == "3")).select(
        pl.concat_list(
            pl.col("test_simple1_test2_name1_test_simple1_test1_name1_name_match"),
            pl.col("test_simple1_test2_name1_test_simple1_test1_name2_name_match"),
            pl.col("test_simple1_test2_name2_test_simple1_test1_name1_name_match"),
            pl.col("test_simple1_test2_name2_test_simple1_test1_name2_name_match"),
        )
    ).item().to_list() == [
        1,
        1,
        0,
        0,
    ]
