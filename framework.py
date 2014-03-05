import sys
import os
import os.path

import ogre.renderer.OGRE as ogre
import ogre.io.OIS as OIS


def getPluginPath():
    """ Return the absolute path to a valid plugins.cfg file.
    look in the current directory for plugins.cfg followed by plugins.cfg.nt|linux|mac
    If not found look one directory up
    """ 
    
    paths = [os.path.join(os.getcwd(), 'plugins.cfg'),
             os.path.join(os.getcwd(), '..','plugins.cfg'),
             ]
    if os.sys.platform == 'darwin':
        paths.insert(1, os.path.join(os.getcwd(), 'plugins.cfg.mac'))
        paths.append(os.path.join(os.getcwd(), '..', 'plugins.cfg.mac'))
    else:
        paths.insert(1,os.path.join(os.getcwd(), 'plugins.cfg.'+os.name))
        paths.append(os.path.join(os.getcwd(), '..', 'plugins.cfg.'+os.name))
        
    for path in paths:
        if os.path.exists(path):
            return path

    sys.stderr.write("\n"
        "** Warning: Unable to locate a suitable plugins.cfg file.\n"
        "** Warning: Please check your ogre installation and copy a\n"
        "** Warning: working plugins.cfg file to the current directory.\n\n")
    raise ogre.Exception(0, "can't locate a suitable 'plugins' file", "")


class OgreApplication(object):
    "This class is the base for an Ogre application."
    debugText=""

    def __init__(self):
        self.frameListener = None
        self.renderWindow = None
        self.sceneManager = None
        self.camera = None

    def go(self):
        """Starts the rendering loop."""
        if self._setUp():
            self.root.startRendering()

    def _setUp(self):
        """This sets up the ogre application"""

        pluginFile = getPluginPath()  # option here to switch to manually loading file if it doesn't exist
        self.root = ogre.Root(pluginFile)
        self.root.setFrameSmoothingPeriod(5.0)

        self._setUpResources()
        if not self._configure():
            return False

        self._chooseSceneManager()
        self._createScene()
        if self.camera is None:
            self._createDefaultCamera()
        self._createViewports()

        ogre.TextureManager.getSingleton().setDefaultNumMipmaps(5)

        self._loadResources()

        self._createFrameListener()
        return True

    def _setUpResources(self):
        """This sets up Ogre's resources, which are required to be in
        resources.cfg."""
        config = ogre.ConfigFile()
        try:
            config.load('resources.cfg') 
        except ogre.OgreFileNotFoundException:
            try:
                config.load('../resources.cfg')
            except:
                raise                
        except:
            raise               
                    
        seci = config.getSectionIterator()
        while seci.hasMoreElements():
            SectionName = seci.peekNextKey()
            Section = seci.getNext()
            for item in Section:
                ogre.ResourceGroupManager.getSingleton().\
                    addResourceLocation(item.value, item.key, SectionName)

    def _loadResources(self):
        """This loads all initial resources.  Redefine this if you do not want
        to load all resources at startup."""
        ogre.ResourceGroupManager.getSingleton().initialiseAllResourceGroups()

    def _configure(self):
        """This shows the config dialog and creates the renderWindow."""
        carryOn = self.root.showConfigDialog()
        if carryOn:
            windowTitle = os.path.join( os.getcwd(), sys.argv[0])
            if not windowTitle:
                windotTitle = "Ogre Render Window"
            self.renderWindow = self.root.initialise(True,windowTitle)
        return carryOn

    def _chooseSceneManager(self):
        """Chooses a default SceneManager."""
        self.sceneManager = self.root.createSceneManager(ogre.ST_GENERIC,"ExampleSMInstance")

    def _createViewports(self):
        """Creates the Viewport."""
        try:    
            self.viewport = self.renderWindow.addViewport(self.camera.getRealCamera())
        except AttributeError:
            self.viewport = self.renderWindow.addViewport(self.camera)
        self.viewport.BackgroundColour = ogre.ColourValue(0,0,0)
        
    def _createScene(self):
        """Creates the scene.  Override this with initial scene contents."""
        pass

    def _createDefaultCamera(self):
        self.camera = self.sceneManager.createCamera('MainCam')

    def _createFrameListener(self):
        """Creates the FrameListener."""
        self.frameListener = OgreFrameListener(self.renderWindow, self.camera)
        self.frameListener.unittest = self.unittest
        self.frameListener.showDebugOverlay(True)
        self.root.addFrameListener(self.frameListener)


def isUnitTest():
    """ use an environment variable to define that we need to do unittesting"""
    env = os.environ
    if env.has_key ("PythonOgreUnitTestPath"):
        return True
    return False
    
def UnitTest_Duration():
    return 5

def UnitTest_Screenshot():
    if isUnitTest():
        env = os.environ
        path = env["PythonOgreUnitTestPath"]
        parentpath = os.getcwd().split(os.path.sep)[-1] # get the last part of the parent directory
        filename = parentpath+'.'+ sys.modules['__main__'].__file__.split('.')[0] # file name is parent.demo.xx
        path = os.path.join ( path, filename )
        return path
    else:
        return "test"

class OgreFrameListener(ogre.FrameListener, ogre.WindowEventListener):
    """A default frame listener, which takes care of basic mouse and keyboard
    input."""

    def __init__(self, renderWindow, camera, bufferedKeys = False, bufferedMouse = False, bufferedJoy = False):
        ogre.FrameListener.__init__(self)
        ogre.WindowEventListener.__init__(self)
        self.camera = camera
        self.renderWindow = renderWindow
        self.statisticsOn = True
        self.numScreenShots = 0
        self.timeUntilNextToggle = 0
        self.sceneDetailIndex = 0
        self.moveScale = 0.0
        self.rotationScale = 0.0
        self.translateVector = ogre.Vector3(0.0,0.0,0.0)
        self.filtering = ogre.TFO_BILINEAR
        self.showDebugOverlay(True)
        self.rotateSpeed =  ogre.Degree(36)
        self.moveSpeed = 100.0
        self.rotationSpeed = 8.0
        self.displayCameraDetails = False
        self.bufferedKeys = bufferedKeys
        self.bufferedMouse = bufferedMouse
        self.rotationX = ogre.Degree(0.0)
        self.rotationY = ogre.Degree(0.0)
        self.bufferedJoy = bufferedJoy
        self.shouldQuit = False # set to True to exit..
        self.MenuMode = False   # lets understand a simple menu function
        
        self.unittest = isUnitTest()
        self.unittest_duration = UnitTest_Duration()  # seconds before screen shot a exit
#         self.unittest_screenshot = sys.modules['__main__'].__file__.split('.')[0]     # file name for unittest screenshot
        self.unittest_screenshot = UnitTest_Screenshot()
        ## we can tell if we are using OgreRefapp based upon the camera class
        
        if self.camera.__class__ == ogre.Camera:
            self.RefAppEnable = False
        else:
            self.RefAppEnable = True
        self._setupInput()
        
    def __del__ (self ):
      ogre.WindowEventUtilities.removeWindowEventListener(self.renderWindow, self)
      self.windowClosed(self.renderWindow)
    
    def _inputSystemParameters (self ):
        """ ovreride to extend any OIS system parameters
        """
        return []
                
    def _setupInput(self):
         # ignore buffered input
        
         # FIXME: This should be fixed in C++ propbably
         import platform
         int64 = False
         for bit in platform.architecture():
             if '64' in bit:
                 int64 = True
         if int64:
             windowHnd = self.renderWindow.getCustomAttributeUnsignedLong("WINDOW")
         else:
             windowHnd = self.renderWindow.getCustomAttributeInt("WINDOW")

         #
         # Here is where we create the OIS input system using a helper function that takes python list of tuples
         #            
         t= self._inputSystemParameters()
         params = [("WINDOW",str(windowHnd))]
         params.extend(t)   
         self.InputManager = OIS.createPythonInputSystem( params )
         
         #
         # an alternate way is to use a multimap which is exposed in ogre 
         #
#          pl = ogre.SettingsMultiMap()
#          windowHndStr = str(windowHnd)
#          pl.insert("WINDOW", windowHndStr)
#          for  v in self._inputSystemParameters():
#               pl.insert(v[0],v[1])
#          im = OIS.InputManager.createInputSystem( pl )
         
         #Create all devices (We only catch joystick exceptions here, as, most people have Key/Mouse)
         self.Keyboard = self.InputManager.createInputObjectKeyboard( OIS.OISKeyboard, self.bufferedKeys )
         self.Mouse = self.InputManager.createInputObjectMouse( OIS.OISMouse, self.bufferedMouse )
         try:
            self.Joy = self.InputManager.createInputObjectJoyStick( OIS.OISJoyStick, self.bufferedJoy )
         except:
            self.Joy = False
#          
         #Set initial mouse clipping size
         self.windowResized(self.renderWindow)
         
         self.showDebugOverlay(True)
         
         #Register as a Window listener
         ogre.WindowEventUtilities.addWindowEventListener(self.renderWindow, self);
         
         
         
    def setMenuMode(self, mode):
        self.MenuMode = mode

    def _updateSimulation(self, frameEvent):
        # create a real version of this to update the simulation
        pass
           
    def windowResized (self, rw):
         dummyint = 0
         width, height, depth, left, top= rw.getMetrics(dummyint,dummyint,dummyint, dummyint, dummyint)  # Note the wrapped function as default needs unsigned int's
         ms = self.Mouse.getMouseState()
         ms.width = width
         ms.height = height
         
    def windowClosed(self, rw):
      #Only close for window that created OIS (mWindow)
      if( rw == self.renderWindow ):
         if( self.InputManager ):
            self.InputManager.destroyInputObjectMouse( self.Mouse )
            self.InputManager.destroyInputObjectKeyboard( self.Keyboard )
            if self.Joy:
                self.InputManager.destroyInputObjectJoyStick( self.Joy )
            OIS.InputManager.destroyInputSystem(self.InputManager)
            self.InputManager=None

    # NOTE the in Ogre 1.6 (1.7) this is changed to frameRenderingQueued !!!
    def frameRenderingQueued ( self, evt ):
        if(self.renderWindow.isClosed() or self.shouldQuit ):
            return False
        if self.unittest:
            self.unittest_duration -= evt.timeSinceLastFrame 
            if self.unittest_duration < 0:
                self.renderWindow.writeContentsToFile(self.unittest_screenshot + '.jpg')
                return False                     
        #Need to capture/update each device - this will also trigger any listeners
        self.Keyboard.capture()    
        self.Mouse.capture()
        buffJ = True
        if( self.Joy ):
            self.Joy.capture()
            buffJ = self.Joy.buffered()

        #Check if one of the devices is not buffered
        if not self.Mouse.buffered() or not self.Keyboard.buffered() or not buffJ :
            # one of the input modes is immediate, so setup what is needed for immediate movement
            if self.timeUntilNextToggle >= 0:
                self.timeUntilNextToggle -= evt.timeSinceLastFrame

            # Move about 100 units per second
            self.moveScale = self.moveSpeed * evt.timeSinceLastFrame
            # Take about 10 seconds for full rotation
            self.rotScale = self.rotateSpeed * evt.timeSinceLastFrame

        self.rotationX = ogre.Degree(0.0)
        self.rotationY = ogre.Degree(0.0)
        self.translateVector = ogre.Vector3().ZERO

        #Check to see which device is not buffered, and handle it
        if not self.Keyboard.buffered():
            if  not self._processUnbufferedKeyInput(evt):
                return False
        if not self.Mouse.buffered():
            if not self._processUnbufferedMouseInput(evt):
                return False

        if not self.Mouse.buffered() or not self.Keyboard.buffered() or not buffJ:
            self._moveCamera(evt)
        
        self._updateSimulation(evt)
        return True

    def showDebugOverlay(self, show):
        """Turns the debug overlay (frame statistics) on or off."""
        overlay = ogre.OverlayManager.getSingleton().getByName('POCore/DebugOverlay')
        if overlay is None:
            self.statisticsOn = False
            ogre.LogManager.getSingleton().logMessage( "ERROR in framework.py: Could not find overlay POCore/DebugOverlay" )
            return
        if show:
            overlay.show()
        else:
            overlay.hide()

    def _processUnbufferedKeyInput(self, frameEvent):
        if self.Keyboard.isKeyDown(OIS.KC_A):
            self.translateVector.x = -self.moveScale

        if self.Keyboard.isKeyDown(OIS.KC_D):
            self.translateVector.x = self.moveScale

        if self.Keyboard.isKeyDown(OIS.KC_UP) or self.Keyboard.isKeyDown(OIS.KC_W):
            self.translateVector.z = -self.moveScale

        if self.Keyboard.isKeyDown(OIS.KC_DOWN) or self.Keyboard.isKeyDown(OIS.KC_S):
            self.translateVector.z = self.moveScale

        if self.Keyboard.isKeyDown(OIS.KC_PGUP):
            self.translateVector.y = self.moveScale

        if self.Keyboard.isKeyDown(OIS.KC_PGDOWN):
            self.translateVector.y = - self.moveScale

        if self.Keyboard.isKeyDown(OIS.KC_RIGHT):
            self.rotationX = - self.rotationScale

        if self.Keyboard.isKeyDown(OIS.KC_LEFT):
            self.rotationX = self.rotationScale

        if self.Keyboard.isKeyDown(OIS.KC_ESCAPE) or self.Keyboard.isKeyDown(OIS.KC_Q):
            return False

        if( self.Keyboard.isKeyDown(OIS.KC_F) and self.timeUntilNextToggle <= 0 ): 
             self.statisticsOn = not self.statisticsOn
             self.showDebugOverlay(self.statisticsOn)
             self.timeUntilNextToggle = 1

        if self.Keyboard.isKeyDown(OIS.KC_T) and self.timeUntilNextToggle <= 0:
            if self.filtering == ogre.TFO_BILINEAR:
                self.filtering = ogre.TFO_TRILINEAR
                self.Aniso = 1
            elif self.filtering == ogre.TFO_TRILINEAR:
                self.filtering = ogre.TFO_ANISOTROPIC
                self.Aniso = 8
            else:
                self.filtering = ogre.TFO_BILINEAR
                self.Aniso = 1

            ogre.MaterialManager.getSingleton().setDefaultTextureFiltering(self.filtering)
            ogre.MaterialManager.getSingleton().setDefaultAnisotropy(self.Aniso)
            self.showDebugOverlay(self.statisticsOn)
            self.timeUntilNextToggle = 1
        
        if self.Keyboard.isKeyDown(OIS.KC_SYSRQ) and self.timeUntilNextToggle <= 0:
            path = 'screenshot_%d.png' % self.numScreenShots
            self.numScreenShots += 1
            self.renderWindow.writeContentsToFile(path)
            OgreApplication.debugText = 'screenshot taken: ' + path
            self.timeUntilNextToggle = 0.5
        
        if self.Keyboard.isKeyDown(OIS.KC_R) and self.timeUntilNextToggle <= 0:
            detailsLevel = [ ogre.PM_SOLID,
                             ogre.PM_WIREFRAME,
                             ogre.PM_POINTS ]
            self.sceneDetailIndex = (self.sceneDetailIndex + 1) % len(detailsLevel)
            self.camera.polygonMode=detailsLevel[self.sceneDetailIndex]
            self.timeUntilNextToggle = 0.5
            
        if self.Keyboard.isKeyDown(OIS.KC_F) and self.timeUntilNextToggle <= 0:
            self.statisticsOn = not self.statisticsOn
            self.showDebugOverlay(self.statisticsOn)
            self.timeUntilNextToggle = 1
        
        if self.Keyboard.isKeyDown(OIS.KC_P) and self.timeUntilNextToggle <= 0:
            self.displayCameraDetails = not self.displayCameraDetails
            if not self.displayCameraDetails:
                OgreApplication.debugText = ""
                
        if self.displayCameraDetails:
            # Print camera details
            pos = self.camera.getDerivedPosition()
            o = self.camera.getDerivedOrientation()
            OgreApplication.debugText = "P: %.3f %.3f %.3f O: %.3f %.3f %.3f %.3f"  \
                        % (pos.x,pos.y,pos.z, o.w,o.x,o.y,o.z)
        return True        
        
    def _isToggleKeyDown(self, keyCode, toggleTime = 1.0):
        if self.Keyboard.isKeyDown(keyCode)and self.timeUntilNextToggle <=0:
            self.timeUntilNextToggle = toggleTime
            return True
        return False
        
    def _isToggleMouseDown(self, Button, toggleTime = 1.0): 
        ms = self.Mouse.getMouseState() 
        if ms.buttonDown( Button ) and self.timeUntilNextToggle <=0: 
            self.timeUntilNextToggle = toggleTime 
            return True 
        return False 

    def _processUnbufferedMouseInput(self, frameEvent):
        ms = self.Mouse.getMouseState()
        if ms.buttonDown( OIS.MB_Right ):
            self.translateVector.x += ms.X.rel * 0.13
            self.translateVector.y -= ms.Y.rel * 0.13
        else:
            self.rotationX = ogre.Degree(- ms.X.rel * 0.13)
            self.rotationY = ogre.Degree(- ms.Y.rel * 0.13)
        return True
        
    def _moveCamera(self, evt):
        self.camera.yaw(self.rotationX)
        self.camera.pitch(self.rotationY)
#         try:
#             self.camera.translate(self.translateVector) # for using OgreRefApp
#         except AttributeError:
        self.camera.moveRelative(self.translateVector)

    def _updateStatistics(self):
        statistics = self.renderWindow
        self._setGuiCaption('POCore/AverageFps', 'Avg FPS: %u' % statistics.getAverageFPS())
        self._setGuiCaption('POCore/CurrFps', 'FPS: %u' % statistics.getLastFPS())
#         self._setGuiCaption('POCore/BestFps',
#                              'Best FPS: %f %d ms' % (statistics.getBestFPS(), statistics.getBestFrameTime()))
#         self._setGuiCaption('POCore/WorstFps',
#                              'Worst FPS: %f %d ms' % (statistics.getWorstFPS(), statistics.getWorstFrameTime()))
        self._setGuiCaption('POCore/NumTris', 'Trianges: %u' % statistics.getTriangleCount())
        self._setGuiCaption('POCore/NumBatches', 'Batches: %u' % statistics.batchCount)
        
        self._setGuiCaption('POCore/DebugText', OgreApplication.debugText)

    def _setGuiCaption(self, elementName, text):
        element = ogre.OverlayManager.getSingleton().getOverlayElement(elementName, False)
        ##d=ogre.UTFString("hell0")
        ##element.setCaption(d)
        
        #element.caption="hello"
        
        #element.setCaption("help")
        element.setCaption(text) # ogre.UTFString(text))
