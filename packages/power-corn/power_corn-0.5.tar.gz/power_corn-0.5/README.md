# Power Corn v1.0

A project to measure and record energy consumption data of the servers

## Instalation

1. Install ipmitool. This is a requirements since we use it to measure the energy comsupmtion of the servers [IBM Power ](https://www.ibm.com/docs/es/power8?topic=power8-p8eih-p8eih-ipmitool-htm).

   ```bash
    apt-get install ipmitool
   ```

2. Configure the necessary environment variables that powercorn use:

   - **SUPABASE_UR** The URl of your database where you're going to store the power reading metrics
   - **SUPABASE_KEY**: The supabase admin key to authenticate your requests
   - **NODE_ID**: The id of the node in the database to relate de power readings

3. Install the app with pip:
   ```bash
   pip install power-corn
   ```
4. Configure cronjobs onece power_corn is installed:
   ```bash
   power_corn install-cron
   ```
