-- Insert your meters.
INSERT INTO meters (location) VALUES ('Meter 1'), ('Meter 2');


-- Create energy contracts to make spending views.
--
-- The fixed price can include all fixed costs in the contract. Usually they
-- are given per month or per year. Normalize it to euros per second. Tax
-- reduction in Netherlands can be added as well by subtracting it from the
-- fixed price. For example if the tax reduction is 800 euros yearly, subtract
-- 800/(number of seconds in a year: 60*60*24*365).
INSERT INTO energy_contracts VALUES
    ('2021-07-01 00:00 Europe/Amsterdam', '2022-01-01 00:00 Europe/Amsterdam', 'Innova Energie', 1,
        0.24564, 0.25732, 0.90975, 0.000002000887874175549, ''),
    ('2022-01-01 00:00 Europe/Amsterdam', '2022-02-01 00:00 Europe/Amsterdam', 'Innova Energie', 1,
        0.36806, 0.40205, 1.42867, -0.000006535705225773717, ''),
    ('2022-02-01 00:00 Europe/Amsterdam', '2022-07-01 00:00 Europe/Amsterdam', 'Innova Energie', 1,
        0.58346, 0.61656, 2.27991, -0.000006535705225773717, ''),
    ('2022-07-01 00:00 Europe/Amsterdam', '2022-09-01 00:00 Europe/Amsterdam', 'Innova Energie', 1,
        0.45383, 0.51683, 1.83960, -0.000005887874175545409, ''),
    ('2022-09-01 00:00 Europe/Amsterdam', '2023-01-01 00:00 Europe/Amsterdam', 'Innova Energie', 1,
        0.72869, 0.83692, 2.69282, -0.000005887874175545409, 'This contract actually starts in October.');
