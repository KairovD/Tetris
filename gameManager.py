import math
import numpy as np
import pygame as pg
from block import Block
from block import BlockImages
from block import BlockStructures
import random
import pathlib
import os
colorDict = {
    'SINGLE': (38, 208, 255),
    'DOUBLE': (208, 255, 38),
    'TRIPLE': (255, 161, 38),
    'TETRIS': (255, 38, 38)
}

class UIImage(pg.sprite.Sprite):
    def __init__(self, image, spriteGroup):
        super().__init__(spriteGroup)
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (0,0)
    def setPosition(self, pos):
        self.rect.topleft = pos
class fieldElement(pg.sprite.Sprite):
    def __init__(self, tetrisManager, gridPos, image):
        self.tetrisManager = tetrisManager
        super().__init__(self.tetrisManager.fieldSpriteGroup)
        self.image = image
        self.rect = self.image.get_rect()
        pos = self.tetrisManager.originPosition + (gridPos * self.tetrisManager.tileSize)
        self.rect.topleft = (pos[0, 0], pos[1, 0])


class tetrisManager:
    def __init__(self, game):
        self.game = game
        # self.fieldOffsetX = (game.screen.get_width() // 2) - ((self.width / 2) * self.tileSize)
        # self.fieldOffsetY = (game.screen.get_height() // 2) - (((self.height / 2) - 1) * self.tileSize)
        self.width = self.game.width
        self.height = self.game.height
        self.tileSize = self.game.tileSize
        self.originPosition = np.matrix([[(game.screen.get_width() // 2) - ((self.width / 2) * self.tileSize)], [(game.screen.get_height() // 2) - (((self.height / 2)) * self.tileSize)]])
        self.gravity = 40#lower values mean faster fall down
        self.gravityTimeout = self.gravity
        self.levelModifier = 0
        self.fieldMatrix = np.full((self.width, self.height), -1)
        self.block = None
        self.nextBlock = random.choice(list(BlockStructures.keys()))
        self.secondNextBlock = random.choice(list(BlockStructures.keys()))
        self.thirdNextBlock = random.choice(list(BlockStructures.keys()))
        self.nextBlockVis = None
        self.secondNextBlockVis = None
        self.thirdNextBlockVis = None
        self.fieldSpriteGroup = pg.sprite.Group()
        self.gameOver = False
        self.UISpriteGroup = pg.sprite.Group()
        self.nextUI = UIImage(pg.transform.scale(pg.image.load(pathlib.Path(os.path.abspath('assets/sprites/UI/NextUI.png'))).convert_alpha(),
                                               (self.tileSize * 14, self.tileSize * 14)), self.UISpriteGroup)
        self.blockProjectionImage = pg.transform.scale(pg.image.load(pathlib.Path(os.path.abspath('assets/sprites/UI/blockProjection.png'))).convert_alpha(), (self.tileSize, self.tileSize))
        self.blockProjection = None
        self.score = 0
        self.visScore = 0
        self.linesCleared = 0

        self.comboCaption = ""
        self.comboTimeout = 0

        self.scorePos = self.originPosition + (np.matrix([[(self.width//2) - 1], [self.height + 1]]) * self.tileSize)
        self.centerPos = self.originPosition + (np.matrix([[(self.width//2)], [self.height + 1]]) * self.tileSize)
        self.upperCenterPos = self.originPosition + (np.matrix([[(self.width//2)], [-2]]) * self.tileSize)
        self.nextUIpos = self.originPosition + np.matrix([[self.width], [0]]) * self.tileSize

        self.toolTipTimeout = 1200
    def spawnNewBlock(self):
        self.block = Block(self, self.nextBlock)
        self.block.setPosition(np.matrix([[4], [0]]))
        self.blockProjection = Block(self, self.nextBlock, image=self.blockProjectionImage)
        self.projectBlock()
        self.nextBlock = self.secondNextBlock
        self.nextBlockVis = Block(self, self.nextBlock)
        self.nextBlockVis.setPosition(np.matrix([[self.width + 2], [3]]))
        self.nextBlockVis.update()

        self.secondNextBlock = self.thirdNextBlock
        self.secondNextBlockVis = Block(self, self.secondNextBlock)
        self.secondNextBlockVis.setPosition(np.matrix([[self.width + 2], [7.1]]))
        self.secondNextBlockVis.update()

        self.thirdNextBlock = random.choice(list(BlockStructures.keys()))
        self.thirdNextBlockVis = Block(self, self.thirdNextBlock)
        self.thirdNextBlockVis.setPosition(np.matrix([[self.width + 2], [11.2]]))
        self.thirdNextBlockVis.update()

    def projectBlock(self):
        self.blockProjection.setPosition(np.matrix(self.block.position))
        for i in range(4):
            self.blockProjection.blocks[i].offset = self.block.blocks[i].offset
        while True:
            if self.blockProjection.tryMovePosition(np.matrix('0; 1')) is False:
                break

    def renderUI(self):
        self.nextUI.setPosition((self.nextUIpos[0, 0], self.nextUIpos[1, 0]))
        self.UISpriteGroup.draw(self.game.screen)
        if self.toolTipTimeout > 0:
            self.game.font.render_to(self.game.screen, (self.nextUIpos[0, 0] + (self.tileSize * 1), self.centerPos[1, 0] + (self.tileSize * -6)),
                                     text='[LEFT, RIGHT] ~ MOVE HORIZONTALLY', fgcolor=(255, 255, 255, 254 * min(1.0, self.toolTipTimeout / 60)), size=self.tileSize * 0.5)
            self.game.font.render_to(self.game.screen, (self.nextUIpos[0, 0] + (self.tileSize * 1), self.centerPos[1, 0] + (self.tileSize * -5)),
                                     text='[UP] ~ ROTATE CLOCKWISE', fgcolor=(255, 255, 255, 254 * min(1.0, self.toolTipTimeout / 60)), size=self.tileSize * 0.5)
            self.game.font.render_to(self.game.screen, (self.nextUIpos[0, 0] + (self.tileSize * 1), self.centerPos[1, 0] + (self.tileSize * -4)),
                                     text='[DOWN] ~ FAST FALL', fgcolor=(255, 255, 255, 254 * min(1.0, self.toolTipTimeout / 60)), size=self.tileSize * 0.5)
            self.game.font.render_to(self.game.screen, (self.nextUIpos[0, 0] + (self.tileSize * 1), self.centerPos[1, 0] + (self.tileSize * -3)),
                                     text='[SPACE] ~ LAND', fgcolor=(255, 255, 255, 254 * min(1.0, self.toolTipTimeout / 60)), size=self.tileSize * 0.5)
            self.toolTipTimeout -= 1
        if self.score > self.visScore:
            self.visScore += max(1, (self.score - self.visScore) // 20)

        self.game.font.render_to(self.game.screen, (self.centerPos[0, 0] - (self.tileSize * len(str(self.visScore)) * 0.3), self.centerPos[1,0]),
                                text=str(self.visScore), fgcolor='white', size= self.tileSize * 1.2, rotation=0)

        self.game.font.render_to(self.game.screen, (self.centerPos[0, 0] - (self.tileSize * len(str(self.linesCleared)) * 0.12), self.centerPos[1, 0] + (self.tileSize * 1.25)),
                                 text=str(self.linesCleared), fgcolor='white', size=self.tileSize * 0.8, rotation=0)

        if self.comboTimeout > 0:
            self.game.font.render_to(self.game.screen, (
            self.upperCenterPos[0, 0] - (self.tileSize * len(self.comboCaption) * 0.3), self.upperCenterPos[1, 0]),
                                     text=str(self.comboCaption), fgcolor=(colorDict[self.comboCaption] + (254 * min(1.0, self.comboTimeout / 20),)), size=self.tileSize * 1.2, rotation=0)
            self.comboTimeout -= 1

    def draw_grid(self):
        self.game.screen.fill(color = (20,20,20), rect= (self.originPosition[0, 0], self.originPosition[1, 0], self.tileSize * self.width, self.tileSize * self.height))
        for x in range(self.width):
            for y in range(self.height):
                pg.draw.rect(self.game.screen, (40,40,40),
                             (self.originPosition[0, 0] + (x * self.tileSize), self.originPosition[1, 0] + (y * self.tileSize), self.tileSize, self.tileSize), 1)
    def removeLine(self, lineIndex):
        for y in reversed(range(1, lineIndex + 1)):
            self.fieldMatrix[:, y] = self.fieldMatrix[:, y-1]
        self.fieldMatrix[:,0] = [-1] * self.width
    def checkLineFill(self):
        lineCleared = 0
        for y in range(self.height):
            if -1 in self.fieldMatrix[:,y]:
                continue
            else:
                lineCleared += 1
                self.linesCleared += 1
                self.removeLine(y)
        if lineCleared > 0:
            self.levelModifier = self.linesCleared // 2
            pg.mixer.Sound.play(self.game.lineClearedSound)
            self.comboTimeout = 300
            if lineCleared == 1:
                self.score += 40
                self.comboCaption = 'SINGLE'
            elif lineCleared == 2:
                self.score += 100
                self.comboCaption = 'DOUBLE'
            elif lineCleared == 3:
                self.score += 300
                self.comboCaption = 'TRIPLE'
            elif lineCleared == 4:
                self.score += 1200
                self.comboCaption = 'TETRIS'

    def game_over(self):
        self.gameOver = True
        pg.mixer.Sound.play(self.game.gameOverSound)
        self.game.data["PrevScore"] = self.score
        if self.score > self.game.data["BestScore"]:
            self.game.data["BestScore"] = self.score

    def draw_borders(self):
        pg.draw.line(self.game.screen, 'White', tuple((self.originPosition[0, 0] + (0 * self.tileSize), self.originPosition[1, 0] + (self.height * self.tileSize))), tuple((self.originPosition[0, 0] + (self.width * self.tileSize), self.originPosition[1, 0] + (self.height * self.tileSize))), 2)
        pg.draw.line(self.game.screen, 'White', tuple((self.originPosition[0, 0] + (0 * self.tileSize) - 2, self.originPosition[1, 0] + (-1 * self.tileSize))), tuple((self.originPosition[0, 0] + (0 * self.tileSize) - 2, self.originPosition[1, 0] + (self.height * self.tileSize))), 2)
        pg.draw.line(self.game.screen, 'White', tuple((self.originPosition[0, 0] + (self.width * self.tileSize), self.originPosition[1, 0] + (-1 * self.tileSize))), tuple((self.originPosition[0, 0] + (self.width * self.tileSize), self.originPosition[1, 0] + (self.height * self.tileSize))), 2)
    def update(self):
        if self.gravityTimeout <= 0:
            self.gravityTimeout = self.gravity - self.levelModifier
            if self.block.tryMovePosition(np.matrix('0; 1')) is False:
                self.block.saveBlockIntoField()
                pg.mixer.Sound.play(self.game.dropSound)
                self.checkLineFill()
                self.redrawField()
                self.block = None
                self.blockProjection = None
        if self.gameOver is True:
            return
        if not self.block:
            self.spawnNewBlock()
        self.gravityTimeout -= 1
        self.block.update()
        self.blockProjection.update()
    def redrawField(self):
        self.fieldSpriteGroup = pg.sprite.Group()
        for x in range(self.width):
            for y in range(self.height):
                if self.fieldMatrix[x,y] != -1:
                    fieldElement(self, np.matrix([[x],[y]]), self.game.sprites[self.fieldMatrix[x,y]])


    def draw(self):
        self.draw_grid()
        if self.gameOver is False:
            self.blockProjection.draw()
            self.block.draw()
        self.fieldSpriteGroup.draw(self.game.screen)
        self.draw_borders()
        self.renderUI()
        self.nextBlockVis.draw()
        self.secondNextBlockVis.draw()
        self.thirdNextBlockVis.draw()
    def moveLeft(self):
        self.block.tryMovePosition(np.matrix('-1; 0'))
        self.projectBlock()
    def moveRight(self):
        self.block.tryMovePosition(np.matrix('1; 0'))
        self.projectBlock()
    def rotate(self):
        self.block.rotateClockwise()
        self.projectBlock()

    def moveDown(self):
        self.block.tryMovePosition(np.matrix('0; 1'))
        self.projectBlock()

    def snapToPosition(self):
        while True:
            if self.block.tryMovePosition(np.matrix('0; 1')) is False:
                break



