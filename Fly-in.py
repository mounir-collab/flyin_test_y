import time as te
from sys import argv
from typing import Any

from src import Connection, Drone, Init, Zone
from src.graph_visual import Visual
from src.parser import Parsing, ParsingError
from src.pathfinder import Pathfinder

RED = '\033[0;31m'
RESET = '\033[1;37m'
BLUE = '\033[0;34m'
GREEN = '\033[0;32m'
if __name__ == "__main__":
    try:
        try:
            with open("imgs/logo", "r") as logo:
                lines = logo.read().splitlines()
                for line in lines:
                    print(f"{BLUE}{line}{RESET}")
                    te.sleep(0.2)
            if len(argv) != 2:
                raise ParsingError("Usage: python Fly-in.py <map_file>")
            print(f"{GREEN}loading ...{RESET}")
            with open(argv[1], "r") as file:
                pass
        except Exception:
            raise ParsingError("Error: no such file or dir")
        parser = Parsing()
        te.sleep(0.3)
        with open(argv[1], "r") as file:
            data: Any = file.read().splitlines()
            data = parser.check_file(data)
            initializer: Init = Init()
            zons: list[Zone] = initializer.zone_init(data)
            connections: list[Connection] = initializer.connection_init(
                data, zons)
            drons: list[Drone] = initializer.drone_init(
                data, "imgs/Drone.png", zons)
            pathf = Pathfinder(zons, data, connections)
            if not pathf.path_cheker():
                raise ParsingError("no path  found from  start  to  end")
            paths: list[list[Zone]] = pathf.get_multiple_paths()
            drones_cpy: list[Drone] = initializer.drone_init(
                data, "imgs/Drone.png", zons)
            visual = Visual(connections, zons, drons, drones_cpy, paths)
            visual.start_window()
    except (ParsingError, KeyboardInterrupt) as e:
        print(f"{RED}{e}{RESET}")
