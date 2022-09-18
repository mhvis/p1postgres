import argparse

import psycopg2

COLUMN_FOR_FIELD = {
    'electricity_used_tariff_1': 'import_low',
    'electricity_used_tariff_2': 'import_normal',
    'electricity_delivered_tariff_1': 'export_low',
    'electricity_delivered_tariff_2': 'export_normal',
    'current_electricity_usage': 'power_consumption',
    'current_electricity_delivery': 'power_generation',
    'instantaneous_voltage_l1': 'voltage_l1',
    'instantaneous_voltage_l2': 'voltage_l2',
    'instantaneous_voltage_l3': 'voltage_l3',
    'instantaneous_current_l1': 'current_l1',
    'instantaneous_current_l2': 'current_l2',
    'instantaneous_current_l3': 'current_l3',
    'instantaneous_active_power_l1_positive': 'power_l1_positive',
    'instantaneous_active_power_l1_negative': 'power_l1_negative',
    'instantaneous_active_power_l2_positive': 'power_l2_positive',
    'instantaneous_active_power_l2_negative': 'power_l2_negative',
    'instantaneous_active_power_l3_positive': 'power_l3_positive',
    'instantaneous_active_power_l3_negative': 'power_l3_negative',
}

SQL_INSERT_ELECTRICITY = """
INSERT INTO electricity_data (time, meter_id)
VALUES (%s, %s)
ON CONFLICT DO NOTHING;
"""

SQL_UPDATE_ELECTRICITY = """
UPDATE electricity_data
SET {column} = %s
WHERE "time" = %s AND meter_id = %s; 
"""

SQL_INSERT_GAS = """
INSERT INTO gas_data (time, meter_id, reading) VALUES (%s, %s, %s);
"""

parser = argparse.ArgumentParser()
parser.add_argument('postgres_dsn', help="PostgreSQL connection URI.")
parser.add_argument('meter_id', type=int, help="Meter ID in the PostgreSQL database.")
parser.add_argument('--electricity', help="File which stores all electricity records fetched from InfluxDB.")
parser.add_argument('--gas', help="File which stores all gas records fetched from InfluxDB.")
args = parser.parse_args()

conn = psycopg2.connect(args.postgres_dsn)
curs = conn.cursor()

# Electricity
if args.electricity:
    with open(args.electricity) as f:
        f.readline()
        # TODO WIP

# i = 0
# for r in query_api.query_stream(electricity_query):
#     # Insert row
#     curs.execute(SQL_INSERT_ELECTRICITY, (r['_time'], args.meter_id))
#     # Set field value
#     column = COLUMN_FOR_FIELD[r['_field']]
#     curs.execute(SQL_UPDATE_ELECTRICITY.format(column=column), (r['_value'], r['_time'], args.meter_id))
#     i += 1
#     if i % 1000 == 0:
#         conn.commit()
#         print(f"Imported {i}/{electricity_count} electricity records ({round(100.0 * i / electricity_count)}%).")
# conn.commit()
# print("Done importing electricity records.")
#
# # Gas
#
#
# i = 0
# for r in query_api.query_stream(gas_query):
#     # Insert
#     curs.execute(SQL_INSERT_GAS, (r['_time'], args.meter_id, r['_value']))
#     i += 1
#     if i % 1000 == 0:
#         conn.commit()
#         print(f"Imported {i}/{gas_count} gas records ({round(100.0 * i / gas_count)}%).")
# conn.commit()
# print("Done importing all records.")
