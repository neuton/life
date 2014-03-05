#!/usr/bin/python

# ================== THE GAME Of LIFE ==================

# --------------- setting main parameters --------------
#fieldSize = [20,20,10]
#fieldSize = [60,60,1]
#fieldSize = [30,30,20]
#fieldSize = [16,16,16]
fieldSize = [14,14,1]
fieldScale = 10
tickTime = 0.2
minRand = 0.8
# rules:
rules2D = [[3],[2,3]]
#rules3D = [[6],[5,6,7]]
rules3D = [[6],[3,4,5,6]]
#rules3D = [6,8,10]
#rules3D = [6,9,11]
# ------------------------------------------------------

def getFieldSize():
    global fieldSize
    return fieldSize

def setFieldSize(size):
    global fieldSize
    fieldSize = size

def getFieldScale():
    global fieldScale
    return fieldScale

def setFieldScale(scale):
    global fieldScale
    fieldScale = scale

def getMinRand():
    global minRand
    return minRand

def setMinRand(rand):
    global minRand
    minRand = rand


from os import listdir
from os.path import isfile, join

dir = 'configs'
files = [join(dir,f) for f in listdir(dir) if isfile(join(dir,f))]
currentFileIndex = None

import Image
initialCells = None

def loadNextConfig():
    global files, currentFileIndex
    if currentFileIndex is None:
        currentFileIndex = 0
    else:
        currentFileIndex += 1
        if currentFileIndex == len(files):
            currentFileIndex = 0
    fname = files[currentFileIndex]
    if fname[-3:] == 'bmp':
        global initialCells
        img = Image.open(fname)
        pix = img.load()
        nx = img.size[0]
        ny = img.size[1]
        initialCells = [[[pix[i,j][0]>0] for j in range(ny)] for i in range(nx)]
        setFieldSize([nx,ny,1])
    else:
        initialCells = None
        f = open(fname, 'r')
        #execfile(fname)
        setFieldSize(eval(f.readline()))
        setFieldScale(eval(f.readline()))
        setMinRand(eval(f.readline()))
        f.close()

def loadPrevConfig():
    global files, currentFileIndex
    if currentFileIndex is None:
        currentFileIndex = 0
    elif currentFileIndex == 0:
        currentFileIndex = len(files)-1
    else:
        currentFileIndex -= 1
    fname = files[currentFileIndex]
    if fname[-3:] == 'bmp':
        global initialCells
        img = Image.open(fname)
        pix = img.load()
        nx = img.size[0]
        ny = img.size[1]
        initialCells = [[[pix[i,j][0]>0] for j in range(ny)] for i in range(nx)]
        setFieldSize([nx,ny,1])
    else:
        initialCells = None
        f = open(fname, 'r')
        #execfile(fname)
        setFieldSize(eval(f.readline()))
        setFieldScale(eval(f.readline()))
        setMinRand(eval(f.readline()))
        f.close()


from random import random

def setRandomField(f):
    nx = f.size[0]
    ny = f.size[1]
    nz = f.size[2]
    for i in range(nx):
        for j in range(ny):
            for k in range(nz):
                if random()>minRand:
                    f.cells[i][j][k].revive()
                else:
                    f.cells[i][j][k].kill()

def initField(f):
    global initialCells
    if initialCells is None:
        setRandomField(f)
    else:
        nx = f.size[0]
        ny = f.size[1]
        nz = f.size[2]
        for i in range(nx):
            for j in range(ny):
                for k in range(nz):
                    if initialCells[i][j][k]:
                        f.cells[i][j][k].revive()
                    else:
                        f.cells[i][j][k].kill()

def update2DField(f):
    nx, ny = f.size[0], f.size[1]
    oldCells = [[ int(f.cells[i][j][0].alive)
                      for j in range(ny)     ]
                          for i in range(nx) ]
    for i in range(nx):
        for j in range(ny):
            cell = f.cells[i][j][0]
            # ---------------------------------------------
            # counting neighbours:
            if i == nx-1:
                ri = 0
            else:
                ri = i+1
            if i == 0:
                li = nx-1
            else:
                li = i-1
            if j == ny-1:
                uj = 0
            else:
                uj = j+1
            if j == 0:
                bj = ny-1
            else:
                bj = j-1
            neighboursCount = (
                oldCells[ri][j] + oldCells[li][j] + oldCells[i][uj] + oldCells[i][bj] +
                oldCells[ri][uj]+ oldCells[li][uj]+ oldCells[ri][bj]+ oldCells[li][bj]
                )
            # --------------------------------------------
            # setting rules:
            if not cell.alive and neighboursCount in rules2D[0]:
                cell.revive()
            elif neighboursCount not in rules2D[1]:
                cell.kill()
            # --------------------------------------------

def update3DField(f):
    nx, ny, nz = f.size[0], f.size[1], f.size[2]
    oldCells = [[[ int(f.cells[i][j][k].alive)
                       for k in range(nz)         ]
                           for j in range(ny)     ]
                               for i in range(nx) ]
    for i in range(nx):
        for j in range(ny):
            for k in range(nz):
                cell = f.cells[i][j][k]
                # ---------------------------------------------
                # counting neighbours:
                if i == nx-1:
                    ri = 0
                else:
                    ri = i+1
                if i == 0:
                    li = nx-1
                else:
                    li = i-1
                if j == ny-1:
                    uj = 0
                else:
                    uj = j+1
                if j == 0:
                    bj = ny-1
                else:
                    bj = j-1
                if k == nz-1:
                    fk = 0
                else:
                    fk = k+1
                if k == 0:
                    rk = nz-1
                else:
                    rk = k-1
                neighboursCount = (
                  oldCells[ri][j][k]+ oldCells[li][j][k]+ oldCells[i][uj][k]+ oldCells[i][bj][k]+
                  oldCells[ri][uj][k]+ oldCells[li][uj][k]+ oldCells[ri][bj][k]+ oldCells[li][bj][k]+
                  oldCells[ri][uj][fk]+ oldCells[li][uj][fk]+ oldCells[i][uj][fk]+
                  oldCells[ri][bj][fk]+ oldCells[li][bj][fk]+ oldCells[i][bj][fk]+
                  oldCells[ri][j][fk]+ oldCells[li][j][fk]+ oldCells[i][j][fk]+
                  oldCells[ri][uj][rk]+ oldCells[li][uj][rk]+ oldCells[i][uj][rk]+
                  oldCells[ri][bj][rk]+ oldCells[li][bj][rk]+ oldCells[i][bj][rk]+
                  oldCells[ri][j][rk]+ oldCells[li][j][rk]+ oldCells[i][j][rk]
                  )
                # --------------------------------------------
                # setting rules:
                if not cell.alive and neighboursCount in rules3D[0]:
                    cell.revive()
                elif neighboursCount not in rules3D[1]:
                    cell.kill()
                # --------------------------------------------

def updateField(f):
    if f.size[0] > 1 and f.size[1] > 1 and f.size[2] > 1:
        update3DField(f)
    else:
        update2DField(f)


from scene_objects import *
from framework import *


class FrameListener(OgreFrameListener):

    def __init__(self, app):
        self.updating = False
        self.isEnterKeyDown = False
        self.isGKeyDown = False
        self.isRKeyDown = False
        self.isRightKeyDown = False
        self.isLeftKeyDown = False
        self.isSpaceKeyDown = False
        self.app = app
        self.field = app.field
        self.t = 0
        global tickTime
        self.tickTime = tickTime
        self.camNode = app.sceneManager.getSceneNode('CameraNode')
        OgreFrameListener.__init__(self, app.renderWindow, app.camera)

    def _updateSimulation(self, frameEvent):
        if self.updating:
            self.t += frameEvent.timeSinceLastFrame
            if self.t >= self.tickTime:
                self.t = 0
                updateField(self.field)
        return True

    def _processUnbufferedKeyInput(self, frameEvent):
        dt = frameEvent.timeSinceLastFrame
        if self.Keyboard.isKeyDown(OIS.KC_LBRACKET):
            self.tickTime *= 10**dt
        if self.Keyboard.isKeyDown(OIS.KC_RBRACKET):
            self.tickTime /= 10**dt
        if self.Keyboard.isKeyDown(OIS.KC_0):
            self.tickTime = 0
        if self.Keyboard.isKeyDown(OIS.KC_BACK):
            global tickTime
            self.tickTime = tickTime
        if self.Keyboard.isKeyDown(OIS.KC_MINUS):
            self.camera.position *= 10**dt
        if self.Keyboard.isKeyDown(OIS.KC_EQUALS):
            self.camera.position /= 10**dt
        if self.Keyboard.isKeyDown(OIS.KC_G):
            if not self.isGKeyDown:
                gridMesh = self.field.grid.mesh
                gridMesh.setVisible(not gridMesh.getVisible())
                self.isGKeyDown = True
        else:
            self.isGKeyDown = False
        if self.Keyboard.isKeyDown(OIS.KC_R):
            if not self.isRKeyDown:
                self.updating = False
                initField(self.field)
                self.isRKeyDown = True
        else:
            self.isRKeyDown = False
        if self.Keyboard.isKeyDown(OIS.KC_RETURN):
            if not self.isEnterKeyDown:
                self.updating = not self.updating
                self.isEnterKeyDown = True
        else:
            self.isEnterKeyDown = False
        if self.Keyboard.isKeyDown(OIS.KC_RIGHT):
            if not self.isRightKeyDown:
                self.updating = False
                loadNextConfig()
                self.app.createNewField()
                self.field = self.app.field
                self.isRightKeyDown = True
        else:
            self.isRightKeyDown = False
        if self.Keyboard.isKeyDown(OIS.KC_LEFT):
            if not self.isLeftKeyDown:
                self.updating = False
                loadPrevConfig()
                self.app.createNewField()
                self.field = self.app.field
                self.isLeftKeyDown = True
        else:
            self.isLeftKeyDown = False
        if self.Keyboard.isKeyDown(OIS.KC_SPACE):
            if not self.isSpaceKeyDown:
                updateField(self.field)
                self.isSpaceKeyDown = True
        else:
            self.isSpaceKeyDown = False
        return not self.Keyboard.isKeyDown(OIS.KC_ESCAPE)

    def _moveCamera(self, frameEvent):
        dt = frameEvent.timeSinceLastFrame
        self.camNode.yaw(50*dt*self.rotationX)
        self.camNode.pitch(50*dt*self.rotationY)


class Application(OgreApplication):

    def __init__(self):
        OgreApplication.__init__(self)
        self.field = None
        
    def createNewField(self, size=None, scale=None):
        if self.field is not None:
            self.field.remove()
        if size is None:
            size = getFieldSize()
        if scale is None:
            scale = getFieldScale()
        self.field = Field(self.sceneManager, size, scale)
        initField(self.field)

    def _createScene(self):
        sm = self.sceneManager
        sm.ambientLight = .05, .05, .05
        light = sm.createLight('Light')
        light.diffuseColour = 1, 1, 1
        light.specularColour = 1, 1, 1
        camera = sm.createCamera('PlayerCam')
        camera.nearClipDistance = 0.1
        camNode = sm.getRootSceneNode().createChildSceneNode('CameraNode')
        camNode.attachObject(camera)
        camNode.attachObject(light)
        light.position = 0, 0, 200
        camera.position = 0, 0, 200
        camera.lookAt(0, 0, 0)
        self.camera = camera
        self.createNewField()

    def _createFrameListener(self):
        self.frameListener = FrameListener(self)
        self.root.addFrameListener(self.frameListener)
        self.frameListener.showDebugOverlay(False)


if __name__ == '__main__':
    try:
        app = Application()
        app.go()
    except ogre.OgreException, e:
        print e
