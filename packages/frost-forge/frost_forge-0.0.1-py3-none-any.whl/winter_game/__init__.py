from os import path, listdir

import pygame as pg

from .info import FPS
from .update import update
from .settings_saving import settings_save
from .rendering import render
from .game_state import GameState


def main() -> None:
    pg.init()
    pg.mouse.set_visible(False)

    state = GameState()
    chunks = {(0, 0, 0, 0): {}}
    window = pg.display.set_mode((0, 0), pg.FULLSCREEN)
    SPRITES_FOLDER = "src/sprites"
    IMAGES = {}
    for filename in listdir(SPRITES_FOLDER):
        IMAGES[filename.split(".")[0]] = pg.image.load(path.join(SPRITES_FOLDER, filename)).convert_alpha()
    while state.run:
        state.position = pg.mouse.get_pos()
        chunks = update(state, chunks)
        state.camera, window = render(state, chunks, window, IMAGES)
        state.clock.tick(FPS)
    pg.quit()
    settings_save(state.controls)