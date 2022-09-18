# Import InfluxDB energy records into PostgreSQL

First download all records from InfluxDB using `influx` CLI. E.g.:

```
$ influx query -f ./fetchelectricity.flux -r > electricity
$ influx query -f ./fetchgas.flux -r > gas
```

Then run the `import.py` script with required arguments:

```
$ python import.py --electricity ./electricity --gas ./gas postgresql://localhost 1
```
