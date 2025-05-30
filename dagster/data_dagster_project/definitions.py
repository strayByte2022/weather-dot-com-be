from dagster import Definitions, load_assets_from_modules

from . import assets
from .assets import kafka_io_manager

all_assets = load_assets_from_modules([assets])

# defs = Definitions(
#     assets=all_assets,
# )

defs = Definitions(

    assets=all_assets,
    resources={
        "kafka_io_manager": kafka_io_manager.configured({
            "producer_config": {"bootstrap.servers": "localhost:29092", "acks": "1"},
            "topic": "weather_data"
        })
    }
)
