from .settings_saving import settings_load
import pygame as pg

class GameState:
    def __init__(self):
        self.controls = settings_load()
        self.clock = pg.time.Clock()
        self.location = {"mined": ((0, 0), (0, 2)), "opened": ((0, 0), (0, 0))}
        self.run = True
        self.zoom = 1
        self.target_zoom = 1
        self.inventory_number = 0
        self.inventory = {}
        self.health = 20
        self.max_health = 20
        self.save_file_name = ""
        self.menu_placement = "main_menu"
        self.velocity = [0, 0]
        self.machine_ui = "game"
        self.control_adjusted = 0
        self.machine_inventory = {}
        self.camera = (0, 0)
        self.tick = 0
        self.noise_offset = (0, 0)