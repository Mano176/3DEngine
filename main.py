import sys
import json
import numpy as np
from player import Player
from viewer2d import Viewer2D
from viewer3d import Viewer3D
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout
from PyQt5.QtCore import Qt, QTimer

def main():
    # Initialize the application
    app = QApplication(sys.argv)
    # Load the world data from a JSON file
    world = load_world("world.json")
    # Create a player object with initial parameters
    global player, keys_pressed
    player = Player(x=5, y=5, z=2, direction=45, horizontal_fov=70, vertical_fov=70, vertical_sample_rate=1, horizontal_sample_rate=1)
    keys_pressed = set()

    # Create the main window
    main_window = QMainWindow()
    central_widget = QWidget()
    layout = QHBoxLayout(central_widget)
    main_window.setCentralWidget(central_widget)

    # Initialize 2D and 3D viewers
    global viewer2d, viewer3d
    viewer2d = Viewer2D(world=world, player=player)
    viewer3d = Viewer3D(world=world, floor_z=0, player=player)
    layout.addWidget(viewer2d)
    layout.addWidget(viewer3d)
    viewer2d.display()
    viewer3d.display()

    main_window.keyPressEvent = keyPressEvent
    main_window.keyReleaseEvent = keyReleaseEvent

    # Create a timer to update the player position
    timer = QTimer()
    timer.timeout.connect(update_player_position)
    timer.start(30)
    
    # Execute the application
    main_window.show()
    sys.exit(app.exec_())


def load_world(file_name):
    # Load the world data from a JSON file and convert it to a numpy array
    with open(file_name, 'r') as file:
        world_data = json.load(file)
    world_array = np.array(world_data)
    return world_array


def keyPressEvent(event):
        # Add key to the set of pressed keys
        global keys_pressed
        keys_pressed.add(event.key())


def keyReleaseEvent(event):
    # Remove key from the set of pressed keys
    global keys_pressed
    keys_pressed.discard(event.key())


def update_player_position():
    global keys_pressed, player
    # Map keys to player movement actions
    map_pos = [
        ([Qt.Key_W, Qt.Key_S], None),
        ([Qt.Key_W], player.move_forward),
        ([Qt.Key_S], player.move_backward),
    ]
    map_direction = [
        ([Qt.Key_A, Qt.Key_D], None),
        ([Qt.Key_A, Qt.Key_S], player.turn_right),
        ([Qt.Key_D, Qt.Key_S], player.turn_left),
        ([Qt.Key_A], player.turn_left),
        ([Qt.Key_D], player.turn_right),
    ]
    # Execute movement actions based on pressed keys
    for keys, action in map_pos:
        if all(key in keys_pressed for key in keys):
            if action is not None:
                action()
            break
    for keys, action in map_direction:
        if all(key in keys_pressed for key in keys):
            if action is not None:
                action()
            break
    # Update the display of both viewers
    global viewer2d, viewer3d
    viewer2d.display()
    viewer3d.display()


if __name__ == "__main__":
    main()