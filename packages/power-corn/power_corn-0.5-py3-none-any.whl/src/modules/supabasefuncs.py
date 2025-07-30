import os
from config.settings import Config
from dataclasses import dataclass
from supabase import create_client, Client


URL = Config.SUPABASE_URL
KEY = Config.SUPABASE_KEY

supabase: Client = create_client(URL, KEY)


@dataclass
class PowerReading:
    node_id: int
    instantaneous_power: float
    min_power: float
    max_power: float
    avg_power: float
    sample_period: str
    power_state: str
    period: str
    measurement_time: str


def create_power_reading_global(reading: PowerReading) -> None:
    """
    Inserts a new power reading into the Supabase database.

    Args:
        node_id (str): Unique identifier for the device.
        instantaneous_power (float, optional): Instantaneous power measurement. Defaults to 0.
        min_power (float, optional): Minimum power measurement. Defaults to 0.
        max_power (float, optional): Maximum power measurement. Defaults to 0.
        avg_power (float, optional): Average power measurement. Defaults to 0.
        sample_period (str, optional): Time period of the measurement. Defaults to "".
        power_state (str, optional): Power state (e.g., "on", "off"). Defaults to "".

    Returns:
        None
    """

    if not reading.node_id:
        raise ValueError("node_id is required")

    try:
        # Create a data dictionary with the provided arguments
        data = {
            "node_id": reading.node_id,
            "instantaneous_power": reading.instantaneous_power,
            "min_power": reading.min_power,
            "max_power": reading.max_power,
            "avg_power": reading.avg_power,
            "sample_period": reading.sample_period,
            "power_state": reading.power_state,
            "period": reading.period,
            "measurement_time": reading.measurement_time,
        }

        # Insert the data into the Supabase database
        response = supabase.table("power_readings").insert(data).execute()
        # print(response.data[0]["id"])
    except Exception as e:
        print("Error saving the data in the centralized database: ", e)
