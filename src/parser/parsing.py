from typing import Any

from .parsingError import ParsingError


class Parsing:
    def check_metadata(self, metadata: str, line: int) -> dict[str, Any]:
        metadata = metadata.strip()[1:-1]
        if not metadata:
            return {}
        line += 1
        data = metadata.split()
        zone_types = ["normal", "blocked", "restricted", "priority"]
        default_keys = ["zone", "color", "max_drones", "max_link_capacity"]
        if data[0].startswith("["):
            raise ParsingError(f"invalid metadata format in line {line}")
        if "]" in data[len(data) - 1]:
            raise ParsingError(f"invalid metadata format in  line {line}")
        res: dict[str, Any] = {}
        for memb in data:
            if "=" not in memb:
                raise ParsingError(f"invalid metadata formatn  in line {line}")
            key, value = memb.split("=", 1)
            if key not in default_keys:
                raise ParsingError(
                    f"the {key} is not a valid key in line{line}")
            if "=" in key or "=" in value:
                raise ParsingError(f"invalid metadata format in line {line}")

            if key == "zone" and value not in zone_types:
                raise ParsingError(f"invalid zone type in line {line}")

            if key == "max_drones" or key == "max_link_capacity":
                if not value.isdigit():
                    msg = f"value_type {type(value)} in line {line}"
                    raise ParsingError(
                        f"invalid args type key{key} {msg}")
                i_value = int(value)
                if i_value <= 0:
                    raise ParsingError(
                        f"invalid value must be > 0 in line {line}")
                res[key] = i_value
                continue
            if key == "color" and not isinstance(value, str):
                raise ParsingError(
                    f"the color must  be instance of str in line {line}")
            res[key] = value
        return (res)

    def pars_hub(self, values: list[Any],
                 metadata: Any, line: int) -> dict[str, Any]:
        if len(values) < 4:
            raise ParsingError(f"invalid hub format in line {line + 1}")
        x = 0
        y = 0
        try:
            x = int(values[2])
            y = int(values[3])
        except ValueError:
            raise ParsingError(
                f"x, y must be valid integers in line {line + 1}")
        if "-" in values[1]:
            msg = f"{values[1]} in line {line + 1}"
            raise ParsingError(
                f"the hub name must  not contain dash  {msg}")

        hub = {
            "name": values[1],
            "x": x,
            "y": y,
            "metadata": {}
        }
        if metadata:
            hub["metadata"] = self.check_metadata(metadata, line)
        return (hub)

    def check_file(self, file_data: list[str]) -> dict[str, Any]:

        i = 0
        values: list[Any] = []
        connections: dict[str, Any] = {}
        nb_drones: Any = 0
        start_hub = {}
        end_hub = {}
        known_hubs = set()
        seen_conc = set()
        hubs: dict[str, Any] = {}
        keys: list[str] = [
            "start_hub:",
            "end_hub:",
            "hub:",
            "connection:",
            "nb_drones:"]
        while (i < len(file_data)):
            line = file_data[i].strip()
            if not line or line.startswith("#"):
                i += 1
                continue

            line = line.split("#", 1)[0].strip()

            metadata = None
            if "[" in line:
                line, metadata = line.split("[", 1)
                metadata = "[" + metadata

            values = line.strip().split()
            if values[0] not in keys:
                raise ParsingError(
                    f"the key {values[0]} not a valid key line {i + 1}")
            if line.startswith("nb_drones:"):
                if len(values) != 2:
                    raise ParsingError(
                        f"invalid nb_drones format in line {i + 1}")
                if not values[1].isdigit():
                    raise ParsingError(
                        f"nb_drones must be numeric in line {i + 1}")
                if nb_drones:
                    raise ParsingError(f"duplicate nb_drones in line {i + 1}")
                nb_drones = int(values[1])
                if nb_drones <= 0:
                    msg = f"valid intger in line {i}"
                    raise ParsingError(
                        f"nb_drones must be a positive {msg}")

            if line.startswith("start_hub:"):
                start_hub = self.pars_hub(values, metadata, i)
                if start_hub["name"] in known_hubs:
                    raise ParsingError(f"duplicate hub name in line {i + 1}")

                if start_hub["metadata"].get("zone") == "blocked":
                    raise ParsingError(
                        f"start_hub cannot be blocked line {i + 1}")
                m = start_hub["metadata"].get("max_drones")
                if m is None:
                    m = float("inf")
                if m < nb_drones:
                    msg = f"less then nb_drones line {i + 1}"
                    raise ParsingError(
                        f"start_hub max drons cannot be {msg}")
                known_hubs.add(start_hub["name"])
                hubs[start_hub["name"]] = start_hub

            if line.startswith("end_hub:"):
                end_hub = self.pars_hub(values, metadata, i)
                if end_hub["name"] in known_hubs:
                    raise ParsingError(f"duplicate hub name in line {i + 1}")

                known_hubs.add(end_hub["name"])
                m = end_hub["metadata"].get("max_drones")
                if m is None:
                    m = float("inf")
                if m < nb_drones:
                    msg = f"less then nb_drones line {i + 1}"
                    raise ParsingError(
                        f"end_hub max_drones cannot be {msg}")
                if end_hub["metadata"].get("zone") == "blocked":
                    raise ParsingError(
                        f"end_hub cannot be blocked line {i + 1}")
                hubs[end_hub["name"]] = end_hub

            if line.startswith("hub:"):
                hub = self.pars_hub(values, metadata, i)
                if hub["name"] in known_hubs:
                    raise ParsingError(f"duplicate hub name in line {i + 1}")
                for name in known_hubs:
                    x = hubs[name]["x"]
                    y = hubs[name]["y"]
                    if x == hub["x"] and y == hub["y"]:
                        raise ParsingError(
                            f"duplicate cordinats in line {i + 1}")
                hubs[hub["name"]] = hub
                known_hubs.add(hub["name"])
            if line.startswith("connection:"):
                if len(values) < 2:
                    raise ParsingError(
                        f"invalid connection format in line {i + 1}")
                value = values[1].strip().split("-", 1)
                if len(value) != 2:
                    raise ParsingError(
                        f"invalid connection format in line {i + 1}")
                if value[0] == value[1]:
                    msg = f"cant be the same in line {i + 1}"
                    raise ParsingError(
                        f"the hubs connection {msg}")
                if value[0] not in known_hubs or value[1] not in known_hubs:
                    raise ParsingError(
                        f"unknown hub in connection in line {i + 1}")
                conc = frozenset((value[0], value[1]))
                if conc in seen_conc:
                    raise ParsingError(f"duplicate connection in line {i + 1}")
                seen_conc.add(conc)
                start: dict[str, Any] = {
                    value[1]: {},
                }
                if metadata:
                    start[value[1]] = self.check_metadata(metadata, i)
                if value[0] not in connections:
                    connections[value[0]] = []
                connections[value[0]].append(start)
            i += 1
        if not nb_drones or not start_hub or not end_hub \
                or not hubs or not connections:
            raise ParsingError(
                "some of the mandatory  keys are missing in line 1")
        return {
            "nb_drones": nb_drones,
            "start_hub": start_hub,
            "end_hub": end_hub,
            "hubs": hubs,
            "connections": connections,
        }
