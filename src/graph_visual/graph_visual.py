
from typing import Any

import pyray as rl

from src import Connection, Drone, Zone


class Colors:
    COLORS = {
        "lightgray": rl.LIGHTGRAY,
        "gray": rl.GRAY,
        "darkgray": rl.DARKGRAY,
        "yellow": rl.YELLOW,
        "gold": rl.GOLD,
        "orange": rl.ORANGE,
        "pink": rl.PINK,
        "red": rl.RED,
        "maroon": rl.MAROON,
        "green": rl.GREEN,
        "lime": rl.LIME,
        "darkgreen": rl.DARKGREEN,
        "skyblue": rl.SKYBLUE,
        "blue": rl.BLUE,
        "darkblue": rl.DARKBLUE,
        "purple": rl.PURPLE,
        "violet": rl.VIOLET,
        "darkpurple": rl.DARKPURPLE,
        "beige": rl.BEIGE,
        "brown": rl.BROWN,
        "darkbrown": rl.DARKBROWN,
        "white": rl.WHITE,
        "black": rl.BLACK,
        "blank": rl.BLANK,
        "magenta": rl.MAGENTA,
    }

    RED = '\033[0;31m'
    RESET = '\033[1;37m'
    BLUE = '\033[0;34m'
    GREEN = '\033[0;32m'
    CYAN = '\033[0;36m'

    def get_color(self, color: str | None) -> rl.Color:
        if color is None:
            return rl.GOLD

        return self.COLORS.get(color.lower(), rl.GOLD)


class Visual:
    def __init__(self,
                 connections: list[Connection],
                 zones: list[Zone],
                 drons: list[Drone],
                 drones_cpy: list[Drone],
                 paths: list[list[Zone]]) -> None:
        self.connections = connections
        self.scale = 80
        self.hight = 900
        self.width = 1800
        self.zones = zones
        self.colors = Colors()
        self.drons = drons
        self.in_geoal: dict[Any, Any] = {
            drone.id: False for drone in self.drons}
        self.in_next: dict[Any, Any] = {
            drone.id: False for drone in self.drons}
        self.req_zone: dict[str, Any] = {z.name: [] for z in self.zones}
        self.loaded_images: dict[int, Any] = {}
        self.curetn_turns: int = 0
        self.paths: list[list[Zone]] = paths
        self.turns: int = 0
        self.drones_cpy = drones_cpy
        self.in_geoal_cpy: dict[Any, Any] = {
            drone.id: False for drone in self.drones_cpy}
        self.turns_histrory: dict[int, Any] = {}
        self.zone_occupancy: dict[str, int] = {z.name: 0 for z in self.zones}
        self.conc_occupancy: dict[str, int] = {
            conc.zone_b.name: conc.max_link_capacity
            for conc in self.connections}
        self.zone_link_occupancy: dict[str, int] = {
            z.name: 0 for z in self.zones}

    def screen_vector(self, x: int, y: int) -> rl.Vector2:
        return rl.Vector2(
            x * self.scale + 30,
            y * self.scale + self.hight // 2)

    def get_cost(self, zone: Zone) -> int:
        if zone.zone == "restricted":
            return 2
        return 1

    def draw_zone(self, zone: Zone) -> None:
        pos = rl.get_mouse_position()
        cx = zone.x * self.scale + 30
        cy = zone.y * self.scale + self.hight // 2

        if cx - zone.zone_radius < pos.x < cx + zone.zone_radius and \
                cy - zone.zone_radius < pos.y < cy + zone.zone_radius:
            zone.zone_radius = 40
        else:
            zone.zone_radius = 30
        rl.draw_circle_v(
            self.screen_vector(
                zone.x,
                zone.y),
            zone.zone_radius,
            self.colors.get_color(
                zone.color))
        rl.draw_text(f"{zone.name}:{zone.max_drones}", cx -
                     15, cy + zone.zone_radius, 10, rl.WHITE)
        if zone.zone == "restricted":
            zone.turns = 2
        rl.draw_text(f"Turns:{zone.turns}", cx -
                     15, cy, 10, rl.BLACK)

    def draw_drone(self, drone: Drone) -> None:
        if self.loaded_images.get(drone.id) is None:
            self.loaded_images[drone.id] = rl.load_texture(drone.img)
        x = drone.x - (self.loaded_images[drone.id].width // 2)
        y = drone.y - (self.loaded_images[drone.id].height // 2)

        ve = rl.Vector2(x, y)
        rl.draw_texture_ex(
            self.loaded_images[drone.id], ve, 0.0, 30 / 32, rl.LIGHTGRAY)

    def draw_connections(self, connection: Connection) -> None:
        zone_a = connection.zone_a
        pos = rl.get_mouse_position()
        start = self.screen_vector(connection.zone_a.x, connection.zone_a.y)
        end = self.screen_vector(connection.zone_b.x, connection.zone_b.y)
        cx = zone_a.x * self.scale + 30
        cy = zone_a.y * self.scale + self.hight // 2
        if cx - zone_a.zone_radius < pos.x < cx + zone_a.zone_radius and \
                cy - zone_a.zone_radius < pos.y < cy + zone_a.zone_radius:
            tick = 8
        else:
            tick = 5
        rl.draw_text(str(connection.max_link_capacity),
                     cx + 30, cy + 10, 15, rl.WHITE)
        rl.draw_line_ex(start, end, tick, rl.BLACK)

    def path_to_drone(self) -> None:
        if not self.paths:
            return
        n = len(self.paths)
        if n > 2:
            n -= 1
            self.paths.pop()
        i = 0
        for drone in self.drons:
            drone.path = self.paths[i % n]
            i += 1

        i = 0
        for drone in self.drones_cpy:
            drone.path = self.paths[i % n]
            i += 1

    def can_move(self, next_zone: Zone) -> int:
        if self.zone_occupancy[next_zone.name] < next_zone.max_drones:
            ml = self.conc_occupancy[next_zone.name]
            if self.zone_link_occupancy[next_zone.name] < ml:
                return 1
            return 0
        return 0

    def calc_turns(self) -> None:
        for drone in self.drones_cpy:
            self.zone_occupancy[drone.current_zone.name] += 1
        while 1:
            turn_moves = {}
            self.zone_link_occupancy = {z.name: 0 for z in self.zones}
            print(f"Turn: {self.turns}")
            for drone in self.drones_cpy:
                turn_moves[drone.id] = drone.current_zone
                log = f"D{drone.id}-{drone.current_zone.name}"
                print(
                    f"{self.colors.CYAN}{log}{self.colors.RESET}", end=" ")
                self.moves(drone)
            self.turns_histrory[self.turns] = turn_moves
            print()
            if all(self.in_geoal_cpy.values()):
                break
            self.turns += 1

        self.req_zone = {z.name: [] for z in self.zones}
        self.zone_occupancy = {z.name: 0 for z in self.zones}

    def moves(self, drone: Drone) -> None:
        if drone.path_index >= len(drone.path) - 1:
            self.in_geoal_cpy[drone.id] = True
            return

        next_zone = drone.path[drone.path_index + 1]
        if not self.can_move(next_zone) or drone.availeble_at > self.turns:
            return
        old_zone = drone.current_zone
        self.zone_occupancy[next_zone.name] += 1
        self.zone_link_occupancy[next_zone.name] += 1
        self.zone_occupancy[old_zone.name] -= 1
        self.zone_link_occupancy[old_zone.name] -= 1
        drone.current_zone = next_zone
        drone.availeble_at = self.turns + drone.current_zone.turns
        drone.path_index += 1

    def move_drone(self, drone: Drone) -> None:
        next_zone = self.turns_histrory[self.curetn_turns][drone.id]
        target = self.screen_vector(next_zone.x, next_zone.y)
        x = target.x - drone.x
        y = target.y - drone.y

        m = max(abs(x), abs(y))
        if m == 0:
            self.in_next[drone.id] = True
            return
        steps_x = x / m
        steps_y = y / m

        if drone.x != target.x:
            drone.x += steps_x

        if drone.y != target.y:
            drone.y += steps_y
        if abs(drone.x - target.x) < 1 and abs(drone.y - target.y) < 1:
            old_zone = drone.current_zone

            self.zone_occupancy[next_zone.name] += 1
            self.zone_occupancy[old_zone.name] -= 1

            self.in_next[drone.id] = True
            drone.current_zone = next_zone

    def start_window(self) -> None:
        frame_counter = 0
        self.animate = False
        rl.init_window(self.width, self.hight, "Fly-in")
        rl.set_target_fps(60)
        self.path_to_drone()
        self.calc_turns()
        for drone in self.drons:
            poss = self.screen_vector(
                drone.current_zone.x, drone.current_zone.y)
            drone.x = poss.x
            drone.y = poss.y
            self.zone_occupancy[drone.current_zone.name] += 1
        while not rl.window_should_close():
            rl.begin_drawing()
            rl.clear_background(rl.BEIGE)
            frame_counter += 1
            for conc in self.connections:
                self.draw_connections(conc)
            for zone in self.zones:
                self.draw_zone(zone)
            if not self.animate:
                if rl.is_key_pressed(rl.KeyboardKey.KEY_UP):
                    if self.curetn_turns != self.turns:
                        self.curetn_turns += 1
                    self.animate = True
                    self.in_next = {drone.id: False for drone in self.drons}
            if self.animate:
                for drone in self.drons:
                    self.draw_drone(drone)
                    self.move_drone(drone)
                if all(self.in_next.values()):
                    self.animate = False

            else:
                for drone in self.drons:
                    self.draw_drone(drone)

            msg = f"Total Turns: {self.curetn_turns}/{self.turns}"
            rl.draw_text(msg, 10, 10, 15, rl.RED)
            rl.end_drawing()

        rl.close_window()
