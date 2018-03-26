from direct.showbase.ShowBase import ShowBase
from direct.gui.OnscreenText import OnscreenText
from direct.task import Task
from panda3d.core import WindowProperties, TextNode, Quat, Vec3

from quaternion import Quaternion, Vector3D
import math




PLAYER_SPEED_BASE = 0
PLAYER_SPEED_LIMIT = 80


PLAYER_TURN_SPEED_LIMIT = 40
PLAYER_TURN_SPEED_MANEUVERABILITY_FACTOR = 1.50




class Universe(ShowBase):
	def __init__(self):
		ShowBase.__init__(self)

		# Generate UI text
		self.instructions = list()
		self.instructions.append(self.genLabelText("Controls: WASD & Mouse | ESC to exit", 0))
		self.instructions.append(self.genLabelText("Mouse Controls", 1))
		self.instructions.append(self.genLabelText("> Left-Right: Ailerons (Roll)", 2))
		self.instructions.append(self.genLabelText("> Up-Down: Elevators (Pitch)", 3))
		self.instructions.append(self.genLabelText("Keyboard Controls", 4))
		self.instructions.append(self.genLabelText("> W & S: Throttle", 5))
		self.instructions.append(self.genLabelText("> A & D: Rudder (Yaw)", 6))

		self.tText = self.genLabelText("", 8)
		self.hprText = self.genLabelText("", 9)
		self.xyText = self.genLabelText("", 10)

		# Shader configuration
		# render.clearShader()

		# Create some text environment (ground).
		self.ground = self.loader.loadModel("environment")
		self.ground.reparentTo(self.render)

		self.ground.setScale(1, 1, 1)
		self.ground.setPos(0, 0, 0)

		# Register & setup key event handler.
		self.keys = {} # dict

		for key in ['a', 'd', 'w', 's']:
			# Make key state for each key, starting as deactivated (0)
			self.keys[key] = 0

			# Register method self.push_key for key down event handling.
			# On event, pass key identifier, & a state of 1 to handler.
			self.accept(key, self.push_key, [key, 1])

			# self.accept('shift-%s' % key, self.push_key, [key, 1])

			# Register method self.push_key for key up event handling.
			# On event, pass key identifier, & a state of 1 to handler.
			self.accept('%s-up' % key, self.push_key, [key, 0])


		# Register the escape key as the exit key.
		self.accept('escape', __import__('sys').exit, [0])

		# Setup Mouse
		self.mouse = {'x': None, 'y': None, 'dx': 0, 'dy': 0}

		# Disable default camera mouse control.
		self.disableMouse()

		wp = WindowProperties()
		wp.setMouseMode(WindowProperties.M_confined)  # Keep the mouse in the window (OS X & Linux)
		wp.setCursorHidden(True)

		wp.setSize(1080, 720)
		# wp.setFullscreen(True)
		wp.setTitle("[DEMO] Controls")
		self.win.requestProperties(wp)

		# Preset values
		self.acceleration = 0
		self.viewAxis = (1, 0, 0)

		# Preset camera
		self.camera.setPos(40, -150, 50)

		# Add the update task every frame.
		self.taskMgr.add(self.update, "Main Task")
		self.taskMgr.add(self.mouseTask, "Mouse Task")

	def push_key(self, key, value):
		# Store the value for the key
		self.keys[key] = value

	def update(self, task):
		delta = globalClock.getDt()

		# Prepare mouse variables with a limit
		dxMouse = self.mouse['dx']
		dyMouse = -self.mouse['dy']

		# Calculate the spaceship's acceleration with a limit
		self.acceleration += (0.01 if self.keys['w'] else -0.01)
		if self.acceleration < 0: self.acceleration = 0
		if self.acceleration > 1: self.acceleration = 1


		# Limit turning speed depending on speed.
		# If going fast, decrease maneuverability.
		playerTurnSpeed = PLAYER_TURN_SPEED_LIMIT * (PLAYER_TURN_SPEED_MANEUVERABILITY_FACTOR - self.acceleration)


		# Physically move the camera
		playerDisplacement = delta * PLAYER_SPEED_BASE + delta * PLAYER_SPEED_LIMIT * self.acceleration
		self.camera.setPos(self.camera, 0, playerDisplacement, 0)


		playerPossibleDelta = delta * playerTurnSpeed

		# Calculate Horizon, Vertical, & Roll offsets.
		playerHOffset = playerPossibleDelta * 0.1		 * 10 * (self.keys['a'] - self.keys['d'])
		playerVOffset = playerPossibleDelta * dyMouse * 10
		playerROffset = dxMouse * 10



		playerPOVRotation = 	Quat()
		playerPOVRotation.setHpr(Vec3(playerHOffset, playerVOffset, playerROffset))


		self.camera.setQuat(self.camera, playerPOVRotation)


		(roll, pitch, yaw) = self.camera.getHpr()
		self.tText.setText(
			"Throttle: {0:0.2f} | MdX: {1:0.2f}, MdY: {2:0.2f}".format(self.acceleration * 100, dxMouse, dyMouse))
		self.hprText.setText("Roll: {0:0.2f}, Pitch: {1:0.2f}, Yaw: {2:0.2f}".format(roll, pitch, yaw))
		self.xyText.setText("Coordinates: ({0:0.2f}, {1:0.2f})".format(self.camera.getX(), self.camera.getY()))

		return Task.cont

	def mouseTask(self, task):
		mw = self.mouseWatcherNode

		# Get the new coordinates
		#x = mw.getMouseX() if mw.hasMouse() else 0
		#y = mw.getMouseY() if mw.hasMouse() else 0

		# Calculate the difference between old and new coordinates.
		#self.mouse['dx'] = x - self.mouse['x'] if self.mouse['x'] is not None else 0
		#self.mouse['dy'] = y - self.mouse['y'] if self.mouse['y'] is not None else 0

		# Get the new coordinates; that's the offset
		self.mouse['dx'] = mw.getMouseX() if mw.hasMouse() else 0
		self.mouse['dy'] = mw.getMouseY() if mw.hasMouse() else 0

		# Update the  old coordinates to the new ones.
		#self.mouse['x'] = x
		#self.mouse['y'] = y


		base.win.movePointer(0, int(base.win.getXSize() / 2), int(base.win.getYSize() / 2))

		return Task.cont

	def genLabelText(self, text, i):
		text = OnscreenText(text=text, pos=(-1.3, .5 - .05 * i), fg=(0, 1, 0, 1), align=TextNode.ALeft, scale=.05)
		return text


if __name__ == "__main__":
	universe = Universe()
	universe.run()
