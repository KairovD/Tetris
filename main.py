import random

import pygame as pg
from pygame import freetype as ft
import sys
from gameManager import tetrisManager as tm
from gameManager import UIImage
import os
import numpy as np
import json

class Background(pg.sprite.Sprite):
    def __init__(self, image):
        pg.sprite.Sprite.__init__(self)
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (0, 0)
class Game:
    def __init__(self):
        pg.init()
        pg.display.set_caption('Tetris')
        self.data = dict()
        self.data["BestScore"] = 0
        self.data["PrevScore"] = 0
        try:
            with open('PlayerSaves.txt') as load_file:
                self.data = json.load(load_file)
        except:
            with open('PlayerSaves.txt', 'w') as store_file:
                json.dump(self.data, store_file)
        self.inMenu = False
        self.screen = pg.display.set_mode((0, 0), pg.FULLSCREEN)
        self.clock = pg.time.Clock()
        self.width = 10
        self.height = 20
        self.tileSize = (self.screen.get_height() * 0.75) // self.height
        self.leftPressed = False
        self.rightPressed = False
        self.upPressed = False
        self.downPressed = False
        self.spacePressed = False
        self.tetrisManager = tm(self)
        self.sprites = self.load_sprites()
        self.backgroundGroup = pg.sprite.Group()
        self.backgrounds = self.load_backgrounds()
        self.backGround = Background(self.backgrounds[random.randrange(0, len(self.backgrounds) - 1)])
        # self.blockIcon = pg.transform.scale(pg.image.load(pathlib.Path(os.path.abspath('assets/sprites/UI/BlockIcon.png'))).convert_alpha(), (self.tileSize, self.tileSize))
        self.blockIcon = pg.transform.scale(pg.image.load('assets/sprites/UI/BlockIcon.png').convert_alpha(), (self.tileSize, self.tileSize))

        self.font = ft.Font(os.path.abspath('assets/fonts/FiraSans-Bold.ttf'))
        self.lineClearedSound = pg.mixer.Sound('assets/sounds/Lineclear.wav')
        self.gameOverSound = pg.mixer.Sound('assets/sounds/Gameover.wav')
        self.dropSound = pg.mixer.Sound('assets/sounds/Drop.wav')
        pg.mixer.music.load('assets/sounds/Soundtrack.wav')
        pg.mixer.music.play(-1)

    def renderGameOver(self):
        icons = pg.sprite.Group()
        gameOverUIPos = self.tetrisManager.originPosition - (np.matrix([[self.width//2], [-self.tetrisManager.height//2]]) * self.tileSize)
        # pg.draw.rect(self.screen, (0,0,0, 100), (gameOverUIPos[0, 0] - (self.tetrisManager.tileSize * 5), gameOverUIPos[1, 0] - (self.tetrisManager.tileSize * 4), self.tetrisManager.tileSize * 10, self.tetrisManager.tileSize * 10))
        self.font.render_to(self.screen, (
            gameOverUIPos[0, 0] - (self.tileSize * 4.5), gameOverUIPos[1, 0] - (self.tileSize * 4)),
                                 text='GAME OVER', fgcolor='white', size=self.tileSize * 1.5)

        UIImage(self.blockIcon, icons).setPosition((gameOverUIPos[0, 0] - (self.tileSize * 4.5),
            gameOverUIPos[1, 0] + (self.tileSize * -1)))
        self.font.render_to(self.screen, (
            gameOverUIPos[0, 0] - (self.tileSize * 3.25),
            gameOverUIPos[1, 0] + (self.tileSize * -1)),
                            text='[Enter] RETRY', fgcolor=(200,200,200), size=self.tileSize * 1.1)
        UIImage(self.blockIcon, icons).setPosition((gameOverUIPos[0, 0] - (self.tileSize * 3.75),
            gameOverUIPos[1, 0] + (self.tileSize * 2)))
        self.font.render_to(self.screen, (
            gameOverUIPos[0, 0] - (self.tileSize * 2.5),
            gameOverUIPos[1, 0] + (self.tileSize * 2)),
                            text='[Esc] MENU', fgcolor=(200,200,200), size=self.tileSize * 1.1)
        icons.draw(self.screen)

    def renderMenu(self):
        icons = pg.sprite.Group()
        ScoreUIPos = np.matrix([[self.screen.get_width() // 2], [8 * self.tileSize]])
        scoreTXT = str(self.data['PrevScore']) + ' | ' + str(self.data['BestScore'])
        self.font.render_to(self.screen, (
            ScoreUIPos[0, 0] - (self.tileSize * 0.42 * len(scoreTXT)),
            ScoreUIPos[1, 0] + (self.tileSize * 0)),
                            text=scoreTXT, fgcolor='white', size=self.tileSize * 1.5)
        UIImage(self.blockIcon, icons).setPosition((ScoreUIPos[0, 0] - (self.tileSize * 4.5),
            ScoreUIPos[1, 0] + (self.tileSize * 3)))
        self.font.render_to(self.screen, (
            ScoreUIPos[0, 0] - (self.tileSize * 3.25),
            ScoreUIPos[1, 0] + (self.tileSize * 3)),
                            text='[Enter] PLAY', fgcolor=(200,200,200), size=self.tileSize * 1.1)
        UIImage(self.blockIcon, icons).setPosition((ScoreUIPos[0, 0] - (self.tileSize * 3.75),
            ScoreUIPos[1, 0] + (self.tileSize * 5)))
        self.font.render_to(self.screen, (
            ScoreUIPos[0, 0] - (self.tileSize * 2.5),
            ScoreUIPos[1, 0] + (self.tileSize * 5)),
                            text='[Esc] EXIT', fgcolor=(200,200,200), size=self.tileSize * 1.1)
        icons.draw(self.screen)

    def update(self):
        if self.tetrisManager.gameOver is False:
            self.tetrisManager.update()
        return

    def load_backgrounds(self):
        # files = [item for item in pathlib.Path(os.path.abspath('assets/sprites/backgrounds')).rglob('*.png') if item.is_file()]
        # images = [pg.image.load(file).convert_alpha() for file in files]
        # images = [pg.transform.scale(image, (self.screen.get_width(), self.screen.get_height())) for image in images]
        # return images
        images = []
        for filename in os.listdir('assets/sprites/backgrounds'):
            if filename.endswith('.png'):
                path = os.path.join('assets/sprites/backgrounds', filename)
                images.append(pg.transform.scale(pg.image.load(path).convert_alpha(), (self.screen.get_width(), self.screen.get_height())))
        return images
    def load_sprites(self):
        # files = [item for item in pathlib.Path(os.path.abspath('assets/sprites')).rglob('*.png') if item.is_file()]
        # images = [pg.image.load(file).convert_alpha() for file in files]
        # images = [pg.transform.scale(image, (self.tileSize, self.tileSize)) for image in images]
        images = []
        for filename in os.listdir('assets/sprites'):
            if filename.endswith('.png'):
                path = os.path.join('assets/sprites', filename)
                images.append(pg.transform.scale(pg.image.load(path).convert_alpha(), (self.tileSize, self.tileSize)))
        return images

    def draw(self):
        self.screen.fill('black')
        self.screen.blit(self.backGround.image, self.backGround.rect)
        self.backgroundGroup.draw(self.screen)
        if self.inMenu is False:
            self.tetrisManager.draw()
        if self.tetrisManager.gameOver and self.inMenu is False:
            self.renderGameOver()
        if self.inMenu is True:
            self.renderMenu()
        pg.display.flip()


    def check_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                with open('PlayerSaves.txt', 'w') as store_file:
                    json.dump(self.data, store_file)
                pg.quit()
                sys.exit()
            if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                if self.inMenu is True:
                    with open('PlayerSaves.txt', 'w') as store_file:
                        json.dump(self.data, store_file)
                    pg.quit()
                    sys.exit()
                elif self.tetrisManager.gameOver:
                    self.inMenu = True
            if event.type == pg.KEYDOWN and event.key == pg.K_RETURN:
                if self.inMenu is True or self.tetrisManager.gameOver is True:
                    self.inMenu = False
                    self.tetrisManager.__init__(self)
                    self.backGround = Background(self.backgrounds[random.randrange(0, len(self.backgrounds))])
            if event.type == pg.KEYDOWN and event.key == pg.K_LEFT:
                self.leftPressed = True
            if event.type == pg.KEYDOWN and event.key == pg.K_RIGHT:
                self.rightPressed = True
            if event.type == pg.KEYDOWN and event.key == pg.K_UP:
                self.upPressed = True
            if event.type == pg.KEYDOWN and event.key == pg.K_DOWN:
                self.downPressed = True
            if event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                self.spacePressed = True
            if event.type == pg.KEYUP and event.key == pg.K_LEFT:
                self.leftPressed = False
            if event.type == pg.KEYUP and event.key == pg.K_RIGHT:
                self.rightPressed = False
            if event.type == pg.KEYUP and event.key == pg.K_UP:
                self.upPressed = False
            if event.type == pg.KEYUP and event.key == pg.K_DOWN:
                self.downPressed = False
            if event.type == pg.KEYUP and event.key == pg.K_SPACE:
                self.spacePressed = False
    def determineMovement(self):
        if self.downPressed:
            self.tetrisManager.moveDown()
        if self.leftPressed and not self.rightPressed:
            self.tetrisManager.moveLeft()
            return True
        elif self.rightPressed and not self.leftPressed:
            self.tetrisManager.moveRight()
            return True

        return self.downPressed

    def run(self):
        movementFrame = -1
        while True:
            self.check_events()
            if self.tetrisManager.gameOver is False:
                if movementFrame >= 0 and movementFrame < 6:
                    movementFrame += 1
                else:
                    if self.determineMovement() is True:
                        movementFrame = 0
                    else:
                        movementFrame = -1
                if self.upPressed is True:
                    self.tetrisManager.rotate()
                    self.upPressed = False
                if self.spacePressed is True:
                    self.tetrisManager.snapToPosition()
                    self.spacePressed = False

            self.update()
            self.draw()
            self.clock.tick(60)


game = Game()
game.run()
