# P1 to PostgreSQL

Insert DSMR P1 readings in a PostgreSQL database with TimescaleDB.


## Docker configuration

See the Docker Compose example for possible environment variables.

```yaml
name: p1postgres

services:
  app:
    image: mhvis/p1postgres
    environment:
      # See https://www.postgresql.org/docs/current/libpq-connect.html#LIBPQ-CONNSTRING
      P1_POSTGRES_DSN: postgresql://user:secret@localhost
      # DSMR version. Possible values: V2_2, V4, V5.
      P1_SERIAL_SETTINGS: V5
      # Usually the same as serial settings.
      P1_TELEGRAM_SPECIFICATION: V5
      P1_DEVICE: /dev/ttyUSB0
      # The meter ID in the database. Should have been inserted beforehand.
      P1_METER_ID: 1
    devices:
      - /dev/ttyUSB0:/dev/ttyUSB0
    restart: unless-stopped
```