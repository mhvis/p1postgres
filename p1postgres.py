import logging
import os
from typing import Dict, Tuple, Optional

import dsmr_parser.clients
import psycopg2
from dsmr_parser import telegram_specifications, obis_references
from dsmr_parser.clients import SerialReader

logger = logging.getLogger(__name__)

SQL_INSERT_ELECTRICITY = """
INSERT INTO electricity_data
    (time, meter_id, import_low, import_normal, export_low, export_normal,
    power_consumption, power_generation, voltage_l1, voltage_l2, voltage_l3,
    current_l1, current_l2, current_l3, power_l1_positive, power_l1_negative,
    power_l2_positive, power_l2_negative, power_l3_positive, power_l3_negative)
VALUES (now(), %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
    %s, %s, %s);
"""


def get_electricity_params(telegram: Dict, meter_id: int) -> Tuple:
    return (
        meter_id,
        telegram.get(obis_references.ELECTRICITY_USED_TARIFF_1),
        telegram.get(obis_references.ELECTRICITY_USED_TARIFF_2),
        telegram.get(obis_references.ELECTRICITY_DELIVERED_TARIFF_1),
        telegram.get(obis_references.ELECTRICITY_DELIVERED_TARIFF_2),
        telegram.get(obis_references.CURRENT_ELECTRICITY_USAGE),
        telegram.get(obis_references.CURRENT_ELECTRICITY_DELIVERY),
        telegram.get(obis_references.INSTANTANEOUS_VOLTAGE_L1),
        telegram.get(obis_references.INSTANTANEOUS_VOLTAGE_L2),
        telegram.get(obis_references.INSTANTANEOUS_VOLTAGE_L3),
        telegram.get(obis_references.INSTANTANEOUS_CURRENT_L1),
        telegram.get(obis_references.INSTANTANEOUS_CURRENT_L2),
        telegram.get(obis_references.INSTANTANEOUS_CURRENT_L3),
        telegram.get(obis_references.INSTANTANEOUS_ACTIVE_POWER_L1_POSITIVE),
        telegram.get(obis_references.INSTANTANEOUS_ACTIVE_POWER_L1_NEGATIVE),
        telegram.get(obis_references.INSTANTANEOUS_ACTIVE_POWER_L2_POSITIVE),
        telegram.get(obis_references.INSTANTANEOUS_ACTIVE_POWER_L2_NEGATIVE),
        telegram.get(obis_references.INSTANTANEOUS_ACTIVE_POWER_L3_POSITIVE),
        telegram.get(obis_references.INSTANTANEOUS_ACTIVE_POWER_L3_NEGATIVE),
    )


SQL_INSERT_GAS = """
INSERT INTO gas_data (time, meter_id, reading) VALUES (%s, %s, %s)
-- The gas reading might already exist, in that case do nothing.
ON CONFLICT DO NOTHING;
"""


def get_gas_params(telegram: Dict, meter_id: int) -> Optional[Tuple]:
    reading = telegram.get(obis_references.HOURLY_GAS_METER_READING) or telegram.get(obis_references.GAS_METER_READING)
    if not reading:
        return None
    return reading.datetime, meter_id, reading.value


SQL_UPDATE_METER = """
UPDATE meters SET
    short_power_failure_count = %s,
    long_power_failure_count = %s,
    power_event_failure_log = %s,
    voltage_sag_l1_count = %s,
    voltage_sag_l2_count = %s,
    voltage_sag_l3_count = %s,
    voltage_swell_l1_count = %s,
    voltage_swell_l2_count = %s,
    voltage_swell_l3_count = %s
WHERE id = %s;
"""


def get_meter_params(telegram: Dict, meter_id: int) -> Tuple:
    power_failure_object = telegram.get(obis_references.POWER_EVENT_FAILURE_LOG)
    if power_failure_object:
        power_event_failure_log = [{'event_time': e.datetime, 'duration': e.value} for e in power_failure_object.buffer]
    else:
        power_event_failure_log = None

    return (
        telegram.get(obis_references.SHORT_POWER_FAILURE_COUNT),
        telegram.get(obis_references.LONG_POWER_FAILURE_COUNT),
        power_event_failure_log,
        telegram.get(obis_references.VOLTAGE_SAG_L1_COUNT),
        telegram.get(obis_references.VOLTAGE_SAG_L2_COUNT),
        telegram.get(obis_references.VOLTAGE_SAG_L3_COUNT),
        telegram.get(obis_references.VOLTAGE_SWELL_L1_COUNT),
        telegram.get(obis_references.VOLTAGE_SWELL_L2_COUNT),
        telegram.get(obis_references.VOLTAGE_SWELL_L3_COUNT),
        meter_id,
    )


def main():
    # Setup from environment
    logging.basicConfig(level=logging.DEBUG if os.getenv('P1_DEBUG') else logging.INFO)

    # Read DSMR configuration
    serial_settings = getattr(dsmr_parser.clients, f"SERIAL_SETTINGS_{os.getenv('P1_SERIAL_SETTINGS', 'V5')}")
    telegram_specification = getattr(telegram_specifications, os.getenv('P1_TELEGRAM_SPECIFICATION', 'V5'))
    device = os.getenv('P1_DEVICE', '/dev/ttyUSB0')

    # Database connection
    conn = psycopg2.connect(os.getenv('P1_POSTGRES_DSN'))

    meter_id = int(os.getenv('P1_METER_ID'))

    reader = SerialReader(
        device=device,
        serial_settings=serial_settings,
        telegram_specification=telegram_specification
    )

    # We cache the gas data and meter statistics because they only need to be
    # updated sporadically.
    cached_meter = None
    cached_gas = None

    for telegram in reader.read():  # type: Dict
        # https://www.psycopg.org/docs/usage.html#transactions-control
        with conn:
            with conn.cursor() as curs:
                curs.execute(SQL_INSERT_ELECTRICITY, get_electricity_params(telegram, meter_id))
                # Gas
                gas = get_gas_params(telegram, meter_id)
                if gas != cached_gas:
                    logger.debug('Gas reading inserted: %s', gas)
                    curs.execute(SQL_INSERT_GAS, gas)
                    cached_gas = gas
                # Meter statistics
                meter = get_meter_params(telegram, meter_id)
                if meter != cached_meter:
                    logger.debug('Meter statistics updated: %s', meter)
                    curs.execute(SQL_UPDATE_METER, meter)
                    cached_meter = meter


if __name__ == '__main__':
    main()
