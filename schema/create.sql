CREATE TABLE meters (
    id SERIAL PRIMARY KEY,
    location varchar(50),
    short_power_failure_count integer,
    long_power_failure_count integer,
    power_event_failure_log jsonb,
    voltage_sag_l1_count integer,
    voltage_sag_l2_count integer,
    voltage_sag_l3_count integer,
    voltage_swell_l1_count integer,
    voltage_swell_l2_count integer,
    voltage_swell_l3_count integer
);


-- 'Numeric' type is more correct than 'double precision' but I use the
-- latter because it has better performance.
CREATE TABLE electricity_data (
    time timestamptz NOT NULL,
    meter_id integer REFERENCES meters NOT NULL,
    -- Meter readings for energy imported (consumed) and exported (generated)
    import_low double precision,
    import_normal double precision,
    export_low double precision,
    export_normal double precision,
    -- I use reals for instantaneous values to reduce storage
    power_consumption real,
    power_generation real,
    voltage_l1 real,
    voltage_l2 real,
    voltage_l3 real,
    current_l1 real,
    current_l2 real,
    current_l3 real,
    power_l1_positive real,
    power_l1_negative real,
    power_l2_positive real,
    power_l2_negative real,
    power_l3_positive real,
    power_l3_negative real,
    PRIMARY KEY (time, meter_id)
);
SELECT create_hypertable('electricity_data', 'time');


CREATE TABLE gas_data (
    time timestamptz NOT NULL,
    meter_id integer REFERENCES meters NOT NULL,
    reading double precision,
    PRIMARY KEY (time, meter_id)
);
SELECT create_hypertable('gas_data', 'time');


CREATE TABLE energy_contracts (
    id SERIAL PRIMARY KEY,
    period tstzrange NOT NULL,  -- I could create an index for this.
    name varchar(50),
    meter_id integer REFERENCES meters NOT NULL,
    -- Electricity price low and normal tariff, in euros per kWh.
    electricity_low double precision,
    electricity_normal double precision,
    -- Gas price, in euros per m3.
    gas double precision,
    -- Fixed price in euros per second.
    fixed double precision,
    notes text
);


-- Create a materialized view for downsampled electricity data.
--
-- The sample rate of electricity data can be quite high, up to one sample each
-- second. This view downsamples to a data point once very 5 minutes. This
-- enables quick queries over longer time periods. Monthly and yearly
-- aggregations can be quickly computed from this table.


-- CREATE MATERIALIZED VIEW electricity_downsampled
-- WITH (timescaledb.continuous) AS
-- SELECT
-- 	time_bucket('5 minutes', time) AS minute,
-- 	meter_id,
-- 	last(electricity_used_tariff_1, time) AS used_t1,
-- 	last(electricity_used_tariff_2, time) AS used_t2,
-- 	last(electricity_delivered_tariff_1, time) AS delivered_t1,
-- 	last(electricity_delivered_tariff_2, time) AS delivered_t2,
-- 	avg(current_electricity_usage) AS current_usage,
-- 	avg(current_electricity_delivery) AS current_delivery
-- FROM electricity_data
-- GROUP BY minute, meter_id;
