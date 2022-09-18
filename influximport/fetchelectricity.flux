from(bucket: "YOUR_BUCKET_HERE")
    |> range(start: 1970-01-01, stop: now())
    |> filter(fn: (r) => r._measurement == "telegram")
    |> filter(fn: (r) =>
        r._field == "electricity_used_tariff_1"
        or r._field == "electricity_used_tariff_2"
        or r._field == "electricity_delivered_tariff_1"
        or r._field == "electricity_delivered_tariff_2"
        or r._field == "current_electricity_usage"
        or r._field == "current_electricity_delivery"
        or r._field == "instantaneous_voltage_l1"
        or r._field == "instantaneous_voltage_l2"
        or r._field == "instantaneous_voltage_l3"
        or r._field == "instantaneous_current_l1"
        or r._field == "instantaneous_current_l2"
        or r._field == "instantaneous_current_l3"
        or r._field == "instantaneous_active_power_l1_positive"
        or r._field == "instantaneous_active_power_l1_negative"
        or r._field == "instantaneous_active_power_l2_positive"
        or r._field == "instantaneous_active_power_l2_negative"
        or r._field == "instantaneous_active_power_l3_positive"
        or r._field == "instantaneous_active_power_l3_negative"
        )
    |> drop(columns: ["_measurement", "_start", "_stop"])
