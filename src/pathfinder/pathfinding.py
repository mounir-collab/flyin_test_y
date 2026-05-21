from typing import Any

from src import Connection, Zone


class Pathfinder:
    def __init__(self,
                 zons: list[Zone],
                 data: dict[str, Any], connections: list[Connection]) -> None:
        self.connections = connections
        self.zones = zons
        for zone in self.zones:
            if zone.zone == "restricted":
                zone.turns = 2
        self.zone_map = {z.name: z for z in zons}
        self.data = data

    def path_cheker(self) -> list[Zone]:
        path: list[Zone] = []
        start: dict[str, Any] = self.data["start_hub"]
        current_zone: Zone = self.zone_map[start["name"]]
        end: dict[str, Any] = self.data["end_hub"]
        previous: dict[str, Any] = {}
        start_zone = self.zone_map[start["name"]]
        queue: list[Zone] = [start_zone]
        visited: set[str] = set()
        for key in self.zone_map:
            previous[key] = None

        while queue:
            current = queue.pop(0)
            if current.name in visited:
                continue
            visited.add(current.name)
            if current.name == end["name"]:
                break

            neighbors = self.get_nighbors(current)
            for n in neighbors:
                if n.name in visited:
                    continue
                if n.zone == "blocked":
                    continue
                if previous[n.name] is None:
                    previous[n.name] = current_zone
                queue.append(n)

        node = self.zone_map[end["name"]]
        if previous[node.name] is None:
            return []
        while node:
            path.append(node)
            node = previous[node.name]
        path.reverse()
        return (path)

    def get_nighbors(self, curent_zone: Zone) -> list[Zone]:
        nighbors: list[Zone] = []
        for c in self.connections:
            if c.zone_a.name == curent_zone.name:
                nighbors.append(c.zone_b)
            elif c.zone_b.name == curent_zone.name:
                nighbors.append(c.zone_a)

        return nighbors

    def Djikstra(self) -> list[Zone]:
        path: list[Zone] = []
        start: dict[str, Any] = self.data["start_hub"]
        current_zone: Zone = self.zone_map[start["name"]]
        end: dict[str, Any] = self.data["end_hub"]
        unvesited: set[str] = set()
        distance: dict[str, Any] = {}
        previous: dict[str, Any] = {}
        for key in self.zone_map:
            unvesited.add(key)
            distance[key] = float("inf")
            previous[key] = None

        distance[current_zone.name] = 0
        while unvesited:
            current_name = min(unvesited, key=lambda z: distance[z])
            current_zone = self.zone_map[current_name]
            unvesited.remove(current_name)
            if current_name == end["name"]:
                break
            neighbors = self.get_nighbors(current_zone)
            for n in neighbors:
                turns: Any = n.turns
                status = n.zone
                new_cost = distance[current_zone.name] + turns
                if status == "blocked":
                    new_cost = float("inf")

                if new_cost < distance[n.name]:
                    distance[n.name] = new_cost
                    previous[n.name] = current_zone

        node = self.zone_map[end["name"]]
        if previous[end["name"]] is None and end["name"] != start["name"]:
            return []
        while node is not None:
            path.append(node)
            node = previous[node.name]

        path.reverse()
        return path

    def get_multiple_paths(self) -> list[list[Zone]]:
        paths: list[list[Zone]] = []
        original_turns = {z.name: z.turns for z in self.zones}
        seen_paths: list[tuple[str, ...]] = []
        while True:
            path: list[Zone] = self.Djikstra()
            if not path:
                break
            sing = tuple(z.name for z in path)

            if sing in seen_paths:
                break
            seen_paths.append(sing)
            paths.append(path)
            for z in path:
                z.turns += 5

        for z in self.zones:
            z.turns = original_turns[z.name]
        return paths
