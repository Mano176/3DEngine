import numpy as np
import matplotlib
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt5.QtWidgets import QWidget, QVBoxLayout

matplotlib.use('Qt5Agg')

class Viewer3D(QWidget):
    def __init__(self, world, floor_z, player):
        super().__init__()
        self.world = np.array(world)
        self.floor_z = floor_z
        self.player = player
        x1, y1, x2, y2 = self.world.T
        max_x = max(max(x1), max(x2))
        max_y = max(max(y1), max(y2))
        min_x = min(min(x1), min(x2))
        min_y = min(min(y1), min(y2))
        self.max_distance = np.sqrt((max_x - min_x)**2 + (max_y - min_y)**2)

        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)

        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)

    def generate_angle_vectors(self, direction, fov, sample_rate):
        # Generate horizontal and vertical angles based on field of view and sample rate
        horizontal_angles = np.linspace(direction - fov[0] / 2, direction + fov[0] / 2, int(fov[0] * sample_rate[0]))
        vertical_angles = np.linspace(-fov[1] / 2, fov[1] / 2, int(fov[1] * sample_rate[1]))
        return (horizontal_angles, vertical_angles)

    def calculate_ray_lengths(self, horizontal_angles, vertical_angles, player_position, world, floor_z):
        # Convert angles to radians
        horizontal_angles = np.deg2rad(horizontal_angles)
        vertical_angles = np.deg2rad(vertical_angles)
        
        player_x, player_y, player_z = player_position

        # Calculate the end points of the rays
        ray_end_xs = player_x + np.cos(horizontal_angles) * 1000  # Large number to ensure it goes beyond the world boundaries
        ray_end_ys = player_y + np.sin(horizontal_angles) * 1000

        # Extract wall coordinates
        x1, y1, x2, y2 = world.T
        # Calculate the denominator of the intersection formula
        epsilon = 1e-10  # Small value to avoid division by zero
        denom = (x1 - x2)[:, None] * (player_y - ray_end_ys) - (y1 - y2)[:, None] * (player_x - ray_end_xs) + epsilon
        # Identify parallel lines where denominator is zero
        parallel = denom == epsilon

        # Calculate intersection parameters t and u
        t = np.where(~parallel, ((x1[:, None] - player_x) * (player_y - ray_end_ys) - (y1[:, None] - player_y) * (player_x - ray_end_xs)) / denom, np.inf)
        u = np.where(~parallel, -((x1[:, None] - x2[:, None]) * (y1[:, None] - player_y) - (y1[:, None] - y2[:, None]) * (x1[:, None] - player_x)) / denom, np.inf)

        # Determine valid intersections
        valid = (0 <= t) & (t <= 1) & (u >= 0)
        # Calculate intersection points
        intersection_xs = np.where(valid, x1[:, None] + t * (x2[:, None] - x1[:, None]), np.inf)
        intersection_ys = np.where(valid, y1[:, None] + t * (y2[:, None] - y1[:, None]), np.inf)

        # Calculate distances from player to intersection points
        distances = np.sqrt((intersection_xs - player_x) ** 2 + (intersection_ys - player_y) ** 2)

        # Find the minimum distance for each ray
        min_distances = np.min(distances, axis=0)[::-1]
        # Adjust distances based on vertical angles
        ray_lengths = (min_distances[:, None] / np.cos(vertical_angles)).T

        # Calculate distances to the floor
        floor_height = np.abs(floor_z - player_z)
        floor_distances = floor_height / np.sin(vertical_angles)
        floor_distances = np.where(floor_distances > 0, floor_distances, np.inf)

        # Reshape floor_distances to match ray_lengths
        floor_distances = np.tile(floor_distances, (ray_lengths.shape[0], 1)).T

        # Decide whether the floor or the wall is closer
        ray_lengths = np.where(ray_lengths < floor_distances, ray_lengths, floor_distances)

        return ray_lengths

    def display(self):
        # Generate angle vectors and calculate ray lengths
        horizontal_angles, vertical_angles = self.generate_angle_vectors(self.player.direction, self.player.fov, self.player.sample_rate)
        ray_lengths = self.calculate_ray_lengths(horizontal_angles, vertical_angles, self.player.get_position(), self.world, self.floor_z)
        ray_lengths_normalized = 1 - ray_lengths / self.max_distance

        # Clear the previous plot and display the new ray lengths
        self.ax.clear()
        self.ax.imshow(ray_lengths_normalized, cmap='gray', aspect='auto')
        self.canvas.draw()