import google.cloud.logging
client = google.cloud.logging.Client()
client.setup_logging()
import logging


def add_constant_column(df, column_name, constant_value):
    df[column_name] = constant_value
    logging.info(f"added '{column_name}' column with constant value: {constant_value}")
    return df
