import argparse
import logging
from io import StringIO

import psycopg2
from influxdb_client import InfluxDBClient

logger = logging.getLogger(__name__)

# Flux field names in the column order of the PostgreSQL destination table.
FIELDS = [
    'electricity_used_tariff_1',
    'electricity_used_tariff_2',
    'electricity_delivered_tariff_1',
    'electricity_delivered_tariff_2',
    'current_electricity_usage',
    'current_electricity_delivery',
    'instantaneous_voltage_l1',
    'instantaneous_voltage_l2',
    'instantaneous_voltage_l3',
    'instantaneous_current_l1',
    'instantaneous_current_l2',
    'instantaneous_current_l3',
    'instantaneous_active_power_l1_positive',
    'instantaneous_active_power_l1_negative',
    'instantaneous_active_power_l2_positive',
    'instantaneous_active_power_l2_negative',
    'instantaneous_active_power_l3_positive',
    'instantaneous_active_power_l3_negative',
]
FIELD_INDEX = dict((FIELDS[i], i) for i in range(len(FIELDS)))

FLUX_ELECTRICITY = """
from(bucket: "{bucket}")
    |> range(start: {start}, stop: {stop})
    |> filter(fn: (r) => r._measurement == "telegram")
    |> filter(fn: (r) =>
""" + ' or '.join(f'r._field == "{f}"' for f in FIELDS) + """
    )
    |> drop(columns: ["_measurement", "_start", "_stop"])
"""

FLUX_GAS = """
from(bucket: "{bucket}")
    |> range(start: {start}, stop: {stop})
    |> filter(fn: (r) => r._measurement == "gas_meter")
    |> filter(fn: (r) => r._field == "reading")
    |> drop(columns: ["_measurement", "_start", "_stop"])
"""

FLUX_COUNT = """
    |> count()
    |> group()
    |> sum()
"""

parser = argparse.ArgumentParser()
parser.add_argument('config', help="InfluxDB config file.")
parser.add_argument('bucket', help="InfluxDB bucket.")
parser.add_argument('postgres_dsn', help="PostgreSQL connection URI.")
parser.add_argument('meter_id', type=int, help="PostgreSQL meter ID.")
parser.add_argument('--range-start', default='1970-01-01')
parser.add_argument('--range-stop', default='now()')
parser.add_argument('--electricity-table',
                    help="PostgreSQL destination table for electricity readings.",
                    default='electricity_data')
parser.add_argument('--gas-table', help="PostgreSQL destination table for gas readings.", default='gas_data')
parser.add_argument('--debug', action='store_true', help="Debug output.")
args = parser.parse_args()

# Set up
logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)
client = InfluxDBClient.from_config_file(args.config)
query_api = client.query_api()

conn = psycopg2.connect(args.postgres_dsn)
curs = conn.cursor()

# Electricity
query = FLUX_ELECTRICITY.format(
    bucket=args.bucket,
    start=args.range_start,
    stop=args.range_stop)
count = query_api.query(query + FLUX_COUNT)[0].records[0].get_value()
logger.info(f"Collecting {count} electricity records.")
data = {}
i = 0
for r in query_api.query_stream(query):
    row = data.setdefault(r['_time'], len(FIELDS) * [None])
    row[FIELD_INDEX[r['_field']]] = r['_value']
    i += 1
    if i % 10000 == 0:
        logger.info(f"Collected {i}/{count} records ({round(100.0 * i / count)}%).")

logger.info("Constructing copy file.")
file = StringIO()
for time, row in data.items():
    logger.debug("Input row: %s %s", time, row)
    values = '\t'.join('\\N' if v is None else str(v) for v in row)
    line = f"{time.isoformat()}\t{args.meter_id}\t{values}\n"
    logger.debug("Line in copy file: %s", line)
    file.write(line)

logger.info("Copying to PostgreSQL.")
file.seek(0)
curs.copy_from(file, args.electricity_table)
conn.commit()

# Gas
query = FLUX_GAS.format(
    bucket=args.bucket,
    start=args.range_start,
    stop=args.range_stop)
count = query_api.query(query + FLUX_COUNT)[0].records[0].get_value()
logger.info(f"Collecting {count} gas records.")
file = StringIO()
i = 0
for r in query_api.query_stream(query):
    file.write(f"{r['_time'].isoformat()}\t{args.meter_id}\t{r['_value']}\n")
    i += 1
    if i % 10000 == 0:
        logger.info(f"Collected {i}/{count} records ({round(100.0 * i / count)}%).")
logger.info("Copying to PostgreSQL.")
file.seek(0)
curs.copy_from(file, args.gas_table)
conn.commit()
