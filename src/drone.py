from typing import Any, Optional

from pydantic import BaseModel, Field, ValidationError

from src.parser import ParsingError


class Zone(BaseModel):
    zone: Optional[str] = Field(default="normal")
    x: int
    y: int
    color: Optional[str] = Field(default=None)
    max_drones: int = Field(default=1)
    turns: int = 1
    name: str
    zone_radius: int


class Connection(BaseModel):
    zone_a: Zone
    zone_b: Zone
    max_link_capacity: int = 1
    all_connections: list[Zone]


class Drone(BaseModel):
    id: int  # drone id
    img: str  # img path
    x: int | float
    y: int | float
    path: list[Zone] = []
    path_index: int = 0
    availeble_at: int = 0
    current_zone: Zone


class Init:
    def zone_init(self, data: dict[str, Any]) -> list[Zone]:
        zons: list[Zone] = []
        try:
            for hub in data["hubs"].values():
                zons.append(
                    Zone(
                        name=hub["name"],
                        x=hub["x"],
                        y=hub["y"],
                        zone_radius=30,
                        **hub["metadata"]))
        except ValidationError:
            raise ParsingError("Error during zone initialization")
        for zone in zons:
            if zone.name == data["start_hub"]["name"] \
                    or zone.name == data["end_hub"]["name"]:
                zone.max_drones = data["nb_drones"]
        return zons

    def connection_init(
            self, data: dict[str, Any], zons: list[Zone]) -> list[Connection]:
        connections: list[Connection] = []
        zone_map = {z.name: z for z in zons}
        try:
            for from_name, value in data["connections"].items():
                zone_a = zone_map[from_name]
                all_connections: list[Zone] = []
                for memb in value:
                    to_name = list(memb.keys())[0]
                    metadata = memb[to_name]
                    zone_b = zone_map[to_name]
                    all_connections.append(zone_b)

                for memb in value:
                    to_name = list(memb.keys())[0]
                    metadata = memb[to_name]
                    zone_b = zone_map[to_name]
                    connections.append(
                        Connection(
                            zone_a=zone_a,
                            zone_b=zone_b,
                            all_connections=all_connections,
                            **metadata))
        except ValidationError:
            raise ParsingError("Error during connections initialization")

        return connections

    def drone_init(self,
                   data: dict[str,
                              Any],
                   img_path: str,
                   zons: list[Zone]) -> list[Drone]:
        drons: list[Drone] = []
        try:
            zone_map = {z.name: z for z in zons}
            for i in range(data["nb_drones"]):
                x = data["start_hub"]["x"]
                y = data["start_hub"]["y"]
                current_zone = zone_map[data["start_hub"]["name"]]
                drons.append(
                    Drone(
                        id=i + 1,
                        img=img_path,
                        x=x,
                        y=y,
                        current_zone=current_zone))
        except ValidationError:
            raise ParsingError("Error during drone initialization")

        return drons
