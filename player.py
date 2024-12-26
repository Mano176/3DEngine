import numpy as np

class Player:
    def __init__(self, x, y, z, direction, horizontal_fov, vertical_fov, vertical_sample_rate, horizontal_sample_rate):
        # Initialize player position, direction, field of view, and sample rate
        self.pos = np.array([x, y, z], dtype=float)
        self.direction = direction
        self.fov = np.array([horizontal_fov, vertical_fov])
        self.sample_rate = np.array([horizontal_sample_rate, vertical_sample_rate])

    def get_position(self):
        # Return the current position of the player
        return self.pos

    def move_forward(self):
        # Move the player forward in the direction they are facing
        rad = np.deg2rad(self.direction)
        self.pos[0] += np.cos(rad) * 0.2
        self.pos[1] += np.sin(rad) * 0.2

    def move_backward(self):
        # Move the player backward in the direction they are facing
        rad = np.deg2rad(self.direction)
        self.pos[0] -= np.cos(rad) * 0.2
        self.pos[1] -= np.sin(rad) * 0.2

    def turn_left(self):
        # Turn the player to the left
        self.direction = (self.direction + 5) % 360

    def turn_right(self):
        # Turn the player to the right
        self.direction = (self.direction - 5) % 360
