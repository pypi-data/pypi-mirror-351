import os
import re
import sqlite3
from config.settings import Config
from src.modules.supabasefuncs import create_power_reading_global, PowerReading

DB_PATH = Config.DB_PATH


def parse_and_log_ipmi_output(output, sample_period_label, timestamp):
    """Parse the output of ipmitool and save it in a log file."""
    if not output:
        print("Warning: Void output of ipmitool.")
        return {}

    log_dir = os.path.join(
        os.path.expanduser("~"), ".local", "share", "power_corn", "logs"
    )
    os.makedirs(log_dir, exist_ok=True)

    log_path = os.path.join(log_dir, f"{sample_period_label}_{timestamp}.txt")

    try:
        with open(log_path, "w") as file:
            file.write(output)
    except IOError as e:
        print(f"Error saving the log {log_path}: {e}")

    parsed_data = {}
    lines = output.strip().splitlines()

    for line in lines:
        # Busca todos los pares clave: valor, incluso si hay más de uno por línea
        matches = re.findall(
            r"([A-Za-z\s]+?):\s+([^\n]+?)(?=(?:\s{2,}[A-Za-z\s]+?:|$))", line
        )
        for key, value in matches:
            clean_key = key.strip()
            clean_value = value.strip().rstrip(".")  # elimina el punto final si hay
            parsed_data[clean_key] = clean_value

    return parsed_data


def save_to_db(parsed_data, period, timestamp):
    """
    Save the parsed data to the database.

    This function takes the parsed data from the ipmitool output and saves it
    to the power_readings table in the SQLite database. It also creates a record
    in the global database using the `create_power_reading_global` function.

    Args:
        parsed_data (dict): The parsed data from the ipmitool output.
        period (str): The sample period, either "now" or "1_hour".
        timestamp (float): The timestamp of the power reading.

    Returns:
        None
    """

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()

        NODE_ID = Config.NODE_ID
        data = extract_power_data(parsed_data, NODE_ID, period, timestamp)

        cursor.execute(
            """
            INSERT INTO power_readings
            (timestamp, instantaneous_power, min_power, max_power, avg_power, sample_period, power_state, period)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                data.measurement_time,
                data.instantaneous_power,
                data.min_power,
                data.max_power,
                data.avg_power,
                data.sample_period,
                data.power_state,
                period,  # "now" o "1_hour"
            ),
        )

        # create the records in the global database
        create_power_reading_global(data)


def get_latest_avg_power(period):
    """Gets the latest value of avg_power for a given period ('now' or '1_hour')."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT avg_power FROM power_readings WHERE period = ? ORDER BY timestamp DESC LIMIT 1",
        (period,),
    )
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None


def get_power_readings_now():
    return get_latest_avg_power("now")


def get_power_readings_hour():
    return get_latest_avg_power("1_hour")


def create_tables_if_not_exists():

    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    try:

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS power_readings (
            id INTEGER PRIMARY KEY,
            timestamp TEXT,
            instantaneous_power REAL,
            min_power REAL,
            max_power REAL,
            avg_power REAL,
            sample_period TEXT,
            power_state TEXT,
            period TEXT CHECK(period IN ('now', '1_hour')) NOT NULL
        )
        """
        )

        conn.commit()
        conn.close()

    except sqlite3.Error as e:
        print(f"Error creating or connecting to the database: {e}")


def extract_power_data(parsed_data, node_id, period, timestamp):
    """Extract and convert power values ​​from dictionary"""

    def extract_value(key, default="0 Watts"):
        """Extracts the number from a string with format '<value> Watts'."""
        value = parsed_data.get(key, default)
        return (
            float(re.search(r"[\d.]+", value).group())
            if re.search(r"[\d.]+", value)
            else 0.0
        )

    return PowerReading(
        node_id=node_id,
        instantaneous_power=extract_value("Instantaneous power reading"),
        min_power=extract_value("Minimum during sampling period"),
        max_power=extract_value("Maximum during sampling period"),
        avg_power=extract_value("Average power reading over sample period"),
        sample_period=parsed_data.get("Sampling period", "0")
        .replace("Seconds.", "")
        .strip(),
        power_state=parsed_data.get("Power reading state is", ""),
        period=period,
        measurement_time=timestamp,
    )
