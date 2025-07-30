import subprocess
import os
import shutil


def main():
    log_dir = os.path.expanduser("~/.local/share/power_corn/logs")
    os.makedirs(log_dir, exist_ok=True)

    # Detect absolute path of power_corn
    power_corn_path = shutil.which("power_corn")
    if not power_corn_path:
        print("Error: 'power_corn' not in PATH.")
        return

    CRON_LINES = f"""
* * * * * {power_corn_path} >> {log_dir}/power.log 2>&1
* * * * * sleep 20; {power_corn_path} >> {log_dir}/power.log 2>&1
* * * * * sleep 40; {power_corn_path} >> {log_dir}/power.log 2>&1
    """

    try:
        current_cron = subprocess.check_output(
            ["crontab", "-l"], stderr=subprocess.DEVNULL
        ).decode()
    except subprocess.CalledProcessError:
        current_cron = ""

    if CRON_LINES.strip() in current_cron:
        print("Cronjobs already installed.")
        return

    new_cron = current_cron.strip() + "\n" + CRON_LINES.strip() + "\n"
    proc = subprocess.run(["crontab", "-"], input=new_cron.encode())

    if proc.returncode == 0:
        print("Cronjobs installed successfully.")
    else:
        print("Error installing cronjobs.")


if __name__ == "__main__":
    main()
