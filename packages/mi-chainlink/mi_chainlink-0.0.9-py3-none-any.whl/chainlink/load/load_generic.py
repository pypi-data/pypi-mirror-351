import os
from pathlib import Path

import duckdb
import polars as pl

from chainlink.load.load_utils import (
    clean_generic,
    execute_flag_bad_addresses,
    load_to_db,
    update_entity_ids,
    validate_input_data,
)
from chainlink.utils import console, logger


def load_generic(db_path: str | Path, schema_config: dict, bad_addresses: list) -> None:
    """
    Loads a generic file into the database.

    Reads config file, loops through each file listed, cleans the data,
    creates a unique id for name, street, and street_name,
    loads into cleaned files into a database using the schema name from the config file,
    and lastly updates the entity name files.

    Returns None.
    """

    schema_name = schema_config["schema_name"]

    with duckdb.connect(db_path, read_only=False) as conn:
        for table_config in schema_config["tables"]:
            # Read the data
            console.log(f"[yellow] Data: {table_config['table_name']} -- Reading data")
            logger.info(f"Data: {table_config['table_name']} -- Reading data")
            file_path = table_config.get("table_name_path")
            if not file_path:
                raise ValueError(f"No file path provided for table: {table_config['table_name']}")

            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Data file not found: {file_path}")

            file_extension = file_path.split(".")[-1].lower()
            if file_extension not in ["csv", "parquet"]:
                raise ValueError(f"Unsupported file format: {file_extension}. Supported formats: csv, parquet")

            try:
                df = (
                    pl.read_csv(file_path, infer_schema=False)
                    if file_extension == "csv"
                    else pl.read_parquet(file_path)
                )
                # convert all columns to string
                df = df.cast(pl.String)

            except Exception as e:
                raise Exception(f"Error reading file {file_path}: {e!s}") from None

            validate_input_data(df, table_config)

            # Clean the data and create ids
            console.log(f"""[yellow] Data: {table_config["table_name"]} -- Starting cleaning""")
            logger.info(f"""Data: {table_config["table_name"]} -- Starting cleaning""")

            all_columns = []
            all_columns.append(table_config["id_col_og"])
            for col in table_config.get("name_cols_og", ""):
                all_columns.append(col)
            for col in table_config.get("address_cols_og", ""):
                all_columns.append(col)

            # Make headers snake case
            df.columns = [x.lower().replace(" ", "_") for x in df.columns]
            # df.columns = df.columns.str, regex=True)

            df = clean_generic(df, table_config)

            # load the data to db
            console.log(f"""[yellow] Data: {table_config["table_name"]} -- Starting load""")

            table_name = table_config["table_name"]
            load_to_db(
                df=df,
                table_name=table_name,
                db_conn=conn,
                schema=schema_name,
            )

            # add new names to entity_names table
            console.log(f"""[yellow] Data: {table_config["table_name"]} -- Updating entity name tables""")
            logger.info(f"""Data: {table_config["table_name"]} -- Updating entity name tables""")

            all_id_cols = ["name_id", "address_id", "street_id", "street_name_id"]

            id_cols = []
            for col in df.columns:
                if any(c in col for c in all_id_cols) and "subaddress_identifier" not in col:
                    id_cols.append(col)

            for col in id_cols:
                update_entity_ids(df=df, entity_id_col=col, db_conn=conn)

            # create bad address flag
            if table_config.get("address_cols"):
                for col in table_config["address_cols"]:
                    execute_flag_bad_addresses(
                        db_conn=conn,
                        table=f"{schema_name}.{table_name}",
                        address_col=col,
                        bad_addresses=bad_addresses,
                    )


if __name__ == "__main__":
    # load_generic("load_config.json")
    pass
