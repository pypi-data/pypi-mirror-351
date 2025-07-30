import platform
import subprocess
from datetime import datetime, timezone
from src.modules.utilities import parse_and_log_ipmi_output, save_to_db


def run_ipmitool(sample_period=None):
    """Execute ipmitool and return the output as string."""

    if "microsoft" in platform.uname().release:  # Detecta si está en WSL
        return mock_ipmitool_output(sample_period)
    command = ["ipmitool", "dcmi", "power", "reading"]
    if sample_period:
        command.append(sample_period)

    try:
        result = subprocess.run(command, text=True, capture_output=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error executing ipmitool: {e}")
        print(f"Error: {e.stderr}")
        return None


def mock_ipmitool_output(sample_period):
    """Simula la salida de ipmitool con valores de prueba."""
    return """\
    Instantaneous power reading:                   330 Watts
    Minimum during sampling period:                  5 Watts
    Maximum during sampling period:                629 Watts
    Average power reading over sample period:      330 Watts
    IPMI timestamp:                           05/02/2025 11:25:41 PM UTC    Sampling period:                          00000001 Seconds.
    Power reading state is:                   activated
"""


def main():
    """Perform power measurements and save data to database."""
    timestamp = datetime.now(timezone.utc).isoformat(timespec="seconds")

    for sample_period_label in ["now", "1_hour"]:
        ipmi_output = run_ipmitool(
            None if sample_period_label == "now" else sample_period_label
        )
        if ipmi_output:
            parsed_data = parse_and_log_ipmi_output(
                ipmi_output, sample_period_label, timestamp
            )

            save_to_db(parsed_data, sample_period_label, timestamp)

    print("Measurement process completed!")
