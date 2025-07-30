# umnetdb-utils
Helper classes for gathering data from umnet databases

This package is hosted on pypi - you can install it with `pip install umnetdb-utils` and use it in your own code.

## Database Helper Classes
As of May 2025 this repo defines db wrapper classes for Equipdb, Netinfo, Netdisco and UMnetdb (populated by agador, hosted on wintermute).
To use these classes you need to provide credentials, either in a config file that you pass into the initializer, in `.env`, or in your environment:
* Netinfo: `NETINFO_USERNAME`, `NETINFO_PASSSWORD`
* Netdisco: `NETDISCO_DB_USER`, `NETDISCO_DB_PASSWORD`
* Equipdb: `EQUIP_DB_USER`, `EQUIP_DB_PASSWORD`
* UMnetdb: `UMNETDB_USER`, `UMNETDB_PASSWORD`

Netinfo, Netdisco, and Equipdb classes are copied over from `umnet-scripts` which is reaching the end of its life as a package.
