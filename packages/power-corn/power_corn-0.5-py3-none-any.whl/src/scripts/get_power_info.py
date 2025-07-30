from src.modules.utilities import get_power_readings_now, get_power_readings_hour


def main():
    last_power = get_power_readings_now()
    avg_power_hour = get_power_readings_hour()
    # print(f"{last_power},{avg_power_hour}")
