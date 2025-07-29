
from typing import List
import logging
import re


from sqlalchemy import text
from .base import UMnetdbBase


class UMnetdb(UMnetdbBase):

    URL="postgresql+psycopg://{UMNETDB_USER}:{UMNETDB_PASSWORD}@wintermute.umnet.umich.edu/umnetdb"

    def get_neighbors(
        self, device: str, known_devices_only: bool = True
    ) -> List[dict]:
        """
        Gets a list of the neighbors of a particular device. If the port
        has a parent in the LAG table that is included as well.
        Neighbor hostname is also looked up in the device table and
        the "source of truth" hostname is returned instead of what shows
        up in lldp neighbor.

        Setting 'known_devices_only' to true only returns neighbors that are found
        in umnet_db's device table. Setting it to false will return all lldp neighbors
        and will include things like phones and APs

        Returns results as a list of dictionary entries keyed on column names.
        """

        if known_devices_only:
            select = [
                "n.port",
                "n_d.name as remote_device",
                "n.remote_port",
                "l.parent",
                "n_l.parent as remote_parent"
                ]
            joins = [
             "join device n_d on n_d.hostname=n.remote_device",
             "left outer join lag l on l.device=n.device and l.member=n.port",
             "left outer join lag n_l on n_l.device=n_d.name and n_l.member=n.remote_port",
            ]
        else:
            select = [
                "n.port",
                "coalesce(n_d.name, n.remote_device) as remote_device",
                "n.remote_port",
                "l.parent",
                "n_l.parent as remote_parent"
            ]
            joins = [
                "left outer join device n_d on n_d.hostname=n.remote_device",
                "left outer join lag l on l.device=n.device and l.member=n.port",
                "left outer join lag n_l on n_l.device=n_d.name and n_l.member=n.remote_port",
            ]

        table = "neighbor n"

        where = [f"n.device='{device}'"]

        query = self._build_select(select, table, joins, where)

        return self.execute(query)

    

    def get_dlzone(self, zone_name:str) -> List[dict]:
        """
        Gets all devices within a DL zone based on walking the 'neighbors'
        table.

        For each device, the following attributes are returned:
        "name", "ip", "version", "vendor", "model", "serial"
        """
        device_cols = ["name", "ip", "version", "vendor", "model", "serial"]

        # step 1 is to find DLs in the database - we'll seed our zone with them
        query = self._build_select(select=device_cols, table="device",where=f"name similar to '(d-|dl-){zone_name}-(1|2)'")
        dls = self.execute(query)

        if not dls:
            raise ValueError(f"No DLs found in umnetdb for zone {zone_name}")

        devices_by_name = {d['name']:d for d in dls}

        # now we'll look for neighbors on each device within the zone.
        # Note that outside of the DLs we only expect to find devices that start with
        # "s-" anything else is considered 'outside the zone'
        todo = list(devices_by_name.keys())
        while(len(todo) != 0):

            device = todo.pop()

            # note that by default this method only returns neighbors in the 'device' table,
            # any others are ignored
            neighs = self.get_neighbors(device)
            devices_by_name[device]["neighbors"] = {}
            for neigh in neighs:

                # only want 'd- or 'dl-' or 's-' devices
                if re.match(r"(dl?|s)-", neigh["remote_device"]):

                    # adding neighbor to local device's neighbor list
                    devices_by_name[device]["neighbors"][neigh["port"]] = {k:v for k,v in neigh.items() if k != "port"}

                    # if we haven't seen this neighbor yet, pull data from our device table for it, and
                    # add it to our 'to do' list to pull its neighbors.
                    if neigh["remote_device"] not in devices_by_name:

                        query = self._build_select(select=device_cols, table="device", where=f"name = '{neigh['remote_device']}'")
                        neigh_device = self.execute(query, fetch_one=True)
                        devices_by_name[neigh_device["name"]] = neigh_device
                
                        todo.append(neigh_device["name"])

        return list(devices_by_name.values())
