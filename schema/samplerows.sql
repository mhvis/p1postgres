-- Adapt these sample rows to your needs and insert them into the database.
--
-- Note: insert your energy contracts separately after inserting the meters, so
-- that you have the correct meter id.


-- Insert your meters.
INSERT INTO meters (location) VALUES ('Eindhoven'), ('Veldhoven');


-- Insert energy contracts for spending views.
--
-- The fixed price is for all fixed costs in the contract and should be given
-- as euros per second. To compute it, combine all fixed costs and divide them
-- by their time period. You can also add in the 'teruggave energiebelasting'
-- in The Netherlands (785 euros in 2022) by subtracting the per second value
-- from the fixed price, i.e. 785/(seconds in a year: 60*60*24*365).
--
-- Contract periods should not overlap, use the [) inclusive-exclusive bound to
-- achieve this (see PostgreSQL documentation on tstzrange types).
INSERT INTO energy_contracts (period, name, meter_id, electricity_low, electricity_normal, gas, fixed, notes)
VALUES
    ('[2021-07-01 00:00 Europe/Amsterdam, 2022-01-01 00:00 Europe/Amsterdam)', 'Innova Energie variabel', 1,
        0.24564, 0.25732, 0.90975, 0.000002000887874175549, ''),
    ('[2022-01-01 00:00 Europe/Amsterdam, 2022-02-01 00:00 Europe/Amsterdam)', 'Innova Energie variabel', 1,
        0.36806, 0.40205, 1.42867, -0.000006535705225773717, ''),
    ('[2022-02-01 00:00 Europe/Amsterdam, 2022-07-01 00:00 Europe/Amsterdam)', 'Innova Energie variabel', 1,
        0.58346, 0.61656, 2.27991, -0.000006535705225773717, ''),
    ('[2022-07-01 00:00 Europe/Amsterdam, 2022-09-01 00:00 Europe/Amsterdam)', 'Innova Energie variabel', 1,
        0.45383, 0.51683, 1.83960, -0.000005887874175545409, ''),
    ('[2022-09-01 00:00 Europe/Amsterdam, 2022-10-01 00:00 Europe/Amsterdam)', 'Innova Energie variabel', 1,
        0.72869, 0.83692, 2.69282, -0.000005887874175545409, 'I do not know the exact prices for this month. I used those of next month.'),
    ('[2022-10-01 00:00 Europe/Amsterdam, 2023-01-01 00:00 Europe/Amsterdam)', 'Innova Energie variabel', 1,
        0.72869, 0.83692, 2.69282, -0.000005887874175545409, '');
