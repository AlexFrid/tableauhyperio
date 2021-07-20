import numpy as np
import pandas as pd
from tqdm import tqdm
from tableauhyperapi import (
    HyperProcess,
    Telemetry,
    Connection,
    SqlType,
    TableDefinition,
    CreateMode,
    TableName,
    Inserter,
)

dtype_mapper = {
    "string": SqlType.text(),
    "str": SqlType.text(),
    "object": SqlType.text(),
    "O": SqlType.text(),
    "int64": SqlType.big_int(),
    "float64": SqlType.double(),
    "bool": SqlType.bool(),
    "datetime64[ns]": SqlType.timestamp(),
    "timedelta[ns]": SqlType.interval(),
    "category": SqlType.text(),
}


def read_hyper(path_to_hyper_file, custom_schema="Extract"):
    """Read a Tableau Hyper file and turn it into a Pandas DataFrame.

    Currently can only read single table extracts, which is Tableau's
    default way of creating an extract.

    Args:
        path_to_hyper_file: Specify the path to the .hyper file
        custom_schema: If you need to change the schema name. Defaults to "Extract"

    Returns:
        Pandas DataFrame
    """

    # Starts the Hyper Process
    with HyperProcess(
        telemetry=Telemetry.DO_NOT_SEND_USAGE_DATA_TO_TABLEAU,
        parameters={"log_config": ""},
    ) as hyper:

        # Connects to an existing .hyper file
        with Connection(
            endpoint=hyper.endpoint, database=path_to_hyper_file
        ) as connection:

            table_names = connection.catalog.get_table_names(schema=custom_schema)

            if table_names == []:
                table_names = connection.catalog.get_table_names(schema="public")
                if table_names == []:
                    raise Exception(
                        """The table schema was not found.
                        If your schema name is different from the Tableau default
                        'Extract' or 'public' then you need to specify that using
                        the custom_schema argument"""
                    )

            if len(table_names) > 1:
                raise Exception(
                    """you're trying to read in multiple tables,
                    which this function doesn't support.
                    You'll need to change the hyper format to Tableau's
                    default single table extract to use this function"""
                )

            table_definition = connection.catalog.get_table_definition(
                name=table_names[0]
            )

            table_data = tqdm(
                connection.execute_query(query=f"SELECT * FROM {table_names[0]}")
            )

            column_names = [
                str(column.name).strip('"') for column in table_definition.columns
            ]

            df = pd.DataFrame(table_data, columns=column_names)

            # To prevent any potential data type problems later on
            # because of a tableau datatype being stored as an object
            # if Pandas cannot infer the correct data type then the
            # column will be converted to a string
            for column in df.columns:
                if "tableau" in str(type(df[column][0])):
                    df[column] = df[column].astype("str")

            return df


def to_hyper(dfs, hyper_file_name, custom_table_names=["Extract"], custom_schema="Extract"):
    """
    Write a Tableau Hyper file from a Pandas DataFrame.

    Args:
        df: Specify which DataFrame or list of DataFrames you want to output
        hyper_file_name: Specify the file name such as "Example.hyper"
        custom_schema: If you need to change the schema name. Defaults to "Extract"
        custom_table_name: Name or names of the given DataFrames

    Returns:
        Tableau Hyper file
    """

    # Check if dfs and xustom_table_names have the right format
    if type(dfs) is not list:
        dfs = [dfs]
    if type(custom_table_names) is not list:
        custom_table_names = [custom_table_names]


    # Starts the Hyper Process
    with HyperProcess(
        telemetry=Telemetry.DO_NOT_SEND_USAGE_DATA_TO_TABLEAU,
        parameters={"log_config": ""},
    ) as hyper:

        # Creates a .hyper file to put the data into
        with Connection(
            hyper.endpoint, hyper_file_name, CreateMode.CREATE_AND_REPLACE
        ) as connection:

            connection.catalog.create_schema(custom_schema)

            # Creates one table for each DataFrame
            for df, name in zip(dfs, custom_table_names):

                # create a .hyper compatible column definition
                # from pd DataFrame column names and dtypes
                # using 3 list comprehensions to loop through
                # all the columns in the DataFrame

                column_names = [column for column in df.columns]

                column_dtype = [dtype for dtype in df.dtypes]

                hyper_table = TableDefinition(
                    TableName(custom_schema, name),
                    [
                        TableDefinition.Column(
                            column_names[column], dtype_mapper[str(column_dtype[column])]
                        )
                        for column in range(len(column_names))
                    ],
                )
                connection.catalog.create_table(hyper_table)

                # Repace NaN with None, otherwise it will not be Null in Tableau
                df.replace({np.nan: None}, inplace=True)

                # Insert the data values into the hyper file
                data_to_insert = df.to_numpy()
                with Inserter(connection, hyper_table) as inserter:
                    inserter.add_rows(tqdm((row for row in data_to_insert)))
                    inserter.execute()
