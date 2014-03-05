import ogre.renderer.OGRE as ogre
from ogre.renderer.OGRE import Vector3


class SceneObject:
    """
        Base scene object class for inheritance.
    """
    def __init__(self, sceneManager, node=None, mesh=None):
        if sceneManager is None:
            raise Exception('sceneManager is None!')
        #if node is not None and not sceneManager.hasSceneNode(node.name): #don't know how to handle this
        #    raise Exception('node is not in sceneManager!')
        self.sceneManager = sceneManager
        if node is None:
            self.node = self._createNode()
        else:
            self.node = node
        if mesh is None:
            self.mesh = self._createMesh()
        else:
            self.mesh = mesh
        if self.mesh is not None:
            self.node.attachObject(self.mesh)

    def _createNode(self):
        return self.sceneManager.getRootSceneNode()

    def _createMesh(self):
        return None

    def remove(self):
        if isinstance(self.mesh, ogre.Entity):
            self.sceneManager.destroyEntity(self.mesh)
        elif isinstance(self.mesh, ogre.ManualObject):
            self.sceneManager.destroyManualObject(self.mesh)
        if self.node is not None and not (self.node.name == 'Ogre/SceneRoot'):
            self.sceneManager.destroySceneNode(self.node)


class Grid(SceneObject):
    """
        A 3-dimensional grid scene object.
    """
    def __init__(self, sceneManager, size, scale=1.0, node=None):
        if len(size) == 1:
            self.size = size[0:1] + [1, 1]
        elif len(size) == 2:
            self.size = size[0:2] + [1]
        elif len(size) == 3:
            self.size = size[0:3]
        else:
            raise Exception('len(size) of Grid may only be 1, 2 or 3!')
        self.scale = scale
        SceneObject.__init__(self, sceneManager, node)
    
    def _createMesh(self):
        mesh = self.sceneManager.createManualObject('GridMesh')
        sx, sy, sz = self.size[0], self.size[1], self.size[2]
        n20, n21, n22 = sx*self.scale*0.5, sy*self.scale*0.5, sz*self.scale*0.5
        l0 = [k*self.scale-n20 for k in range(sx+1)]
        l1 = [k*self.scale-n21 for k in range(sy+1)]
        l2 = [k*self.scale-n22 for k in range(sz+1)]
        mb = lambda : mesh.begin("pale", ogre.RenderOperation.OT_LINE_STRIP)
        me = lambda : mesh.end()
        po = lambda x, y, z: mesh.position(x, y, z)
        for i in l0:
            for j in l1:
                mb()
                po(i, j, -n22)
                po(i, j, n22)
                me()
        for i in l1:
            for j in l2:
                mb()
                po(-n20, i, j)
                po(n20, i, j)
                me()
        for i in l0:
            for j in l2:
                mb()
                po(i, -n21, j)
                po(i, n21, j)
                me()
        return mesh


class GridFrame(SceneObject):
    """
        A 3-dimensional grid frame scene object.
    """
    def __init__(self, sceneManager, size, scale=1.0, node=None):
        if len(size) == 1:
            self.size = size[0:1] + [1, 1]
        elif len(size) == 2:
            self.size = size[0:2] + [1]
        elif len(size) == 3:
            self.size = size[0:3]
        else:
            raise Exception('len(size) of GridFrame may only be 1, 2 or 3!')
        self.scale = scale
        SceneObject.__init__(self, sceneManager, node)
    
    def _createMesh(self):
        mesh = self.sceneManager.createManualObject('GridFrameMesh')
        sx, sy, sz = self.size[0], self.size[1], self.size[2]
        n20, n21, n22 = (sx+0.1)*self.scale*0.5, (sy+0.1)*self.scale*0.5, (sz+0.1)*self.scale*0.5
        l0 = [-(0.5*sx+0.05)*self.scale, (0.5*sx+0.05)*self.scale]
        l1 = [-(0.5*sy+0.05)*self.scale, (0.5*sy+0.05)*self.scale]
        l2 = [-(0.5*sz+0.05)*self.scale, (0.5*sz+0.05)*self.scale]
        mb = lambda : mesh.begin("red", ogre.RenderOperation.OT_LINE_STRIP)
        me = lambda : mesh.end()
        po = lambda x, y, z: mesh.position(x, y, z)
        for i in l0:
            for j in l1:
                mb()
                po(i, j, -n22)
                po(i, j, n22)
                me()
        for i in l1:
            for j in l2:
                mb()
                po(-n20, i, j)
                po(n20, i, j)
                me()
        for i in l0:
            for j in l2:
                mb()
                po(i, -n21, j)
                po(i, n21, j)
                me()
        return mesh


cellsCount = 0

class Cell(SceneObject):
    """
        Basic cell scene object (a cube with states).
    """
    def __init__(self, sceneManager, position=Vector3(0.0,0.0,0.0), scale=1.0, node=None):
        self.position = position
        SceneObject.__init__(self, sceneManager, node)
        self.node.setPosition(self.position)
        self.node.setScale(scale*0.008, scale*0.008, scale*0.008)
        global cellsCount
        cellsCount += 1
    
    def _createMesh(self):
        return self.sceneManager.createEntity('CellMesh'+str(cellsCount), 'cube.mesh')
    
    def remove(self):
        SceneObject.remove(self)
        global cellsCount
        cellsCount -= 1

    def revive(self):
        self.mesh.setVisible(True)
        self.alive = True

    def kill(self):
        self.mesh.setVisible(False)
        self.alive = False

    #def updateColor(self):
    #    self.mesh.setMaterialName("pale")


class Field(SceneObject):
    """
        The main field of the game.
        Contains a grid filled with cells.
    """
    def __init__(self, sceneManager, size, scale=1.0, node=None):
        SceneObject.__init__(self, sceneManager, node)
        if len(size) == 1:
            self.size = size[0:1] + [1, 1]
        elif len(size) == 2:
            self.size = size[0:2] + [1]
        elif len(size) == 3:
            self.size = size[0:3]
        else:
            raise Exception('len(size) of Grid may only be 1, 2 or 3!')
        self.gridFrame = GridFrame(sceneManager, self.size, scale, self.node)
        self.grid = Grid(sceneManager, self.size, scale, self.node)
        self.cells = [[[None for i in range(size[2])] for i in range(size[1])] for i in range(size[0])]
        global cellsCount
        n20, n21, n22 = (size[0]-1)*0.5, (size[1]-1)*0.5, (size[2]-1)*0.5
        for i in range(size[0]):
            for j in range(size[1]):
                for k in range(size[2]):
                    cellNode = self.node.createChildSceneNode('CellNode'+str(cellsCount))
                    p = Vector3((i-n20)*scale, (j-n21)*scale, (k-n22)*scale)
                    cell = self.cells[i][j][k] = Cell(sceneManager, p, scale, cellNode)
                    cell.kill()
    
    def remove(self):
        self.gridFrame.remove()
        self.grid.remove()
        for i in range(self.size[0]):
            for j in range(self.size[1]):
                for k in range(self.size[2]):
                    self.cells[i][j][k].remove()
        SceneObject.remove(self)
