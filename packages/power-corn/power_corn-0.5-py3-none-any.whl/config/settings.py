import os


class Config:
    DB_PATH = os.path.join(
        os.path.expanduser("~"),
        ".local",
        "share",
        "power_corn",
        "power_timeseries.sqlite",
    )
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    NODE_ID = os.getenv("NODE_ID")
