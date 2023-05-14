import pygame as pg
import numpy as np

BlockStructures = {
    'T': ['0; 0', '-1; 0', '1; 0', '0; -1'],
    'Sq': ['0; 0', '0; -1', '1; 0', '1; -1'],
    'L_r': ['0; 0', '-1; 0', '0; -1', '0; -2'],
    'L_l': ['0; 0', '1; 0', '0; -1', '0; -2'],
    'Long': ['0; 0', '0; 1', '0; -1', '0; -2'],
    'S_r': ['0; 0', '-1; 0', '0; -1', '1; -1'],
    'S_l': ['0; 0', '1; 0', '0; -1', '-1; -1']
}
BlockImages = {
    'T': 6,
    'Sq': 3,
    'L_r': 2,
    'L_l': 1,
    'Long': 0,
    'S_r': 5,
    'S_l': 4
}


class cell(pg.sprite.Sprite):
    def __init__(self, parent, pos: np.matrix):
        self.parent = parent
        super().__init__(self.parent.blockGroup)
        self.image = self.parent.image
        self.rect = self.image.get_rect()
        self.offset: np.matrix = pos
        return

    def update(self):
        pos = self.parent.tetrisManager.originPosition + ((self.parent.position + self.offset) * self.parent.blockSize)
        self.rect.topleft = (pos[0, 0], pos[1, 0])

    def checkCollision(self):
        pos = self.parent.position + self.offset
        if pos[1, 0] >= self.parent.tetrisManager.height or pos[0, 0] not in range(0, self.parent.tetrisManager.width) \
                or (pos[1, 0] >= 0 and self.parent.tetrisManager.fieldMatrix[pos[0, 0], pos[1, 0]] != -1):
            return True
        return False


class Block:
    def __init__(self, tetrisManager, block_index, image=None):
        self.tetrisManager = tetrisManager
        self.blockSize = self.tetrisManager.tileSize
        if image is None:
            self.image = self.tetrisManager.game.sprites[BlockImages[block_index]]
        else:
            self.image = image
        self.blockIndex = block_index
        self.position: np.matrix = np.matrix([[0], [0]])
        self.blocks = []
        self.blockGroup = pg.sprite.Group()
        for i in range(4):
            self.blocks.append(cell(self, np.matrix(BlockStructures[block_index][i])))

    def setPosition(self, pos):
        self.position = pos

    def tryMovePosition(self, dir: np.matrix):
        self.position += dir
        if self.blocks[0].checkCollision() or self.blocks[1].checkCollision() or self.blocks[2].checkCollision() or \
                self.blocks[3].checkCollision():
            self.position -= dir
            return False
        return True

    def rotateClockwise(self):
        if self.blockIndex == "Sq":
            return False
        failed = False
        for block in self.blocks:
            block.offset = np.matrix('0, -1; 1, 0') * block.offset #matrix transformation
            if block.checkCollision() is True:
                failed = True
        if failed:
            if self.tryMovePosition(np.matrix('-1; 0')) or self.tryMovePosition(np.matrix('1; 0')) or self.tryMovePosition(np.matrix('0; 1')) or self.tryMovePosition(np.matrix('1; 1')) or self.tryMovePosition(np.matrix('-1; 1')) or self.tryMovePosition(np.matrix('0; -1')) or self.tryMovePosition(np.matrix('-2; 0')) or self.tryMovePosition(np.matrix('2; 0')):
                return True
            for block in self.blocks:
                block.offset = np.matrix('0, 1; -1, 0') * block.offset
            return False

        return True

    def saveBlockIntoField(self):
        for block in self.blocks:
            pos = self.position + block.offset
            if pos[1,0] < 0:
                self.tetrisManager.game_over()
                return False
            self.tetrisManager.fieldMatrix[pos[0, 0], pos[1, 0]] = BlockImages[self.blockIndex]
        self.tetrisManager.score += 5
        return True

    def update(self):
        for block in self.blocks:
            block.update()

    def draw(self):
        self.blockGroup.draw(self.tetrisManager.game.screen)
