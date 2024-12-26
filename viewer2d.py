import matplotlib
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt5.QtWidgets import QWidget, QVBoxLayout

matplotlib.use('Qt5Agg')

class Viewer2D(QWidget):
    def __init__(self, world, player):
        super().__init__()
        self.world = np.array(world)
        self.player = player

        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)

        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)

    def calculate_ray_lengths(self, angles, player_position, world):
        # Convert angles to radians
        rads = np.deg2rad(angles)

        player_x, player_y, _ = player_position

        # Calculate the end points of the rays
        ray_end_xs = player_x + np.cos(rads) * 1000  # Large number to ensure it goes beyond the world boundaries
        ray_end_ys = player_y + np.sin(rads) * 1000

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
        min_distances = np.min(distances, axis=0)
        return min_distances

    def display(self):
        # Clear the previous plot
        self.ax.clear()

        # Draw the world walls
        for line in self.world:
            self.ax.plot([line[0], line[2]], [line[1], line[3]], 'k-')

        # Draw the player position
        player_x, player_y, _ = self.player.get_position()
        self.ax.plot(player_x, player_y, 'ro')

        # Draw rays
        start_angle = self.player.direction - self.player.fov[0] / 2
        end_angle = self.player.direction + self.player.fov[0] / 2
        num_rays = int(self.player.sample_rate[0] * self.player.fov[0])
        angles = np.linspace(start_angle, end_angle, num=num_rays)

        ray_lengths = self.calculate_ray_lengths(angles, self.player.get_position(), self.world)
        ray_end_xs = player_x + np.cos(np.deg2rad(angles)) * ray_lengths
        ray_end_ys = player_y + np.sin(np.deg2rad(angles)) * ray_lengths

        for ray_x, ray_y in zip(ray_end_xs, ray_end_ys):
            self.ax.plot([player_x, ray_x], [player_y, ray_y], 'r')

        # Set plot limits and aspect ratio
        self.ax.set_xlim(0, 15)
        self.ax.set_ylim(0, 15)
        self.ax.set_aspect('equal', adjustable='box')
        self.canvas.draw()