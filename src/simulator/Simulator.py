import os
import random
import shutil
import logging
import cv2
import numpy as np
from collections import deque
from abc import ABC, abstractmethod
from ..sim_objects.RoadObjectsData import ROAD_LINES, ROAD_OBJECTS
from ..sim_objects.Colors import Colors
from ..sim_objects.Median import Median
from ..generators.RoadSignGenerator import RoadSignGenerator
from ..video_playback import video_playback
from ..const.constants import (SCREEN_HEIGHT, SCREEN_WIDTH, HORIZON_HEIGHT, CENTER, BOUNDS, MEDIAN_LINES_PER_FRAME,
                               MEDIAN_LINE_GAP_MAX_LENGTH, MEDIAN_X_START, 
                               DEBUG, DURATION, MAX_CHAOS, LOG_PATH, IMG_OUTPUT_PATH, MASKS_OUTPUT_PATH, VIDEO_OUTPUT_PATH
                               )
# Holds BGR color values
colors = Colors()

class Simulator(ABC):
    terrain_colors = {
            "grass": colors.grass_green,
            "sand": colors.sand,
            "rock": colors.rock,
            "clay": colors.clay
        }
    def __init__(
        self, 
        number_frames: int = DURATION,  # Default frame count
        moving_speed: float = 0.1, # Default speed
        frame_rate: int = 10,      # Default FPS
        chaos: int = 5,            # Default chaos level
        sim_name: str = "test",
        terrain: str = "grass",
        video: bool = False
    ):
        """
            Initializes the parent simulator class.
            Params:
                number_frames (int) - the total number_frames generated by the simulator,
                moving_speed (float) - the rate at which objects move per frame relative to the true horizon,
                frame_rate (int) - the frame rate for video output,
                chaos (int) - leads to a greater likelihood of more objects being created within a frame
        """
        if number_frames <= 0 or number_frames > 10000:
            raise ValueError("number_frames must be a positive integer less than 10,000.")
        if moving_speed <= 0 or moving_speed > 1:
            raise ValueError("moving_speed must be greater than zero and less than 1")
        if frame_rate <= 0:
            raise ValueError("frame_rate must be a positive integer.")
        
        # Simulator values
        self.number_frames = int(number_frames)
        self.moving_speed = moving_speed # The speed at which objects move in proportion to true horizon
        self.frame_rate = frame_rate # Speed set for video playback
        self.chaos = min(chaos, MAX_CHAOS)
        self.sim_name = sim_name
        self.number_medians = int(self.number_frames / MEDIAN_LINES_PER_FRAME)
        self.horizon = HORIZON_HEIGHT * SCREEN_HEIGHT
        self.video = video

        # Initialize class objects
        self.roadsign_generator = RoadSignGenerator(CENTER, BOUNDS)
        self.road_object_names = ROAD_OBJECTS
        self.road_objects = deque([])
        self._initialize_terrain(terrain)
        self._initialize_frames()
        self._initialize_labels()
        self._initialize_median()

        # Output paths 
        self.log_path = LOG_PATH
        self.img_output_path = IMG_OUTPUT_PATH
        self.mask_output_path = MASKS_OUTPUT_PATH

        if not os.path.exists(LOG_PATH):
            os.mkdir(LOG_PATH) # Sets up the logging directory

        if os.path.exists(f"{LOG_PATH}/app.log"):
            os.remove(f"{LOG_PATH}/app.log") # Removes the log file if it already exists

        # Ensure the paths exist before trying to remove them
        # Set up the image output directory and the labels output directory
        for path in [IMG_OUTPUT_PATH, MASKS_OUTPUT_PATH]: # Don't remove the videos directory
            if os.path.exists(path):
                shutil.rmtree(path)  # Properly removes directories
        
        for path in [IMG_OUTPUT_PATH, MASKS_OUTPUT_PATH, VIDEO_OUTPUT_PATH]:
            os.makedirs(path, exist_ok=True)  # Creates directory safely

        # Configure logging
        logging.basicConfig(filename=f"{LOG_PATH}/app.log", level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")

    @abstractmethod
    def run(self):
        """
            Defined in  subclasses
        """
        pass

    def create_video(self):
        if self.video:
            video_playback(self.sim_name, self.frame_rate)

    def remove_invalid_objects(self):
        i = 0
        while (i < len(self.road_objects) and not self.road_objects[i].validate()):
            self.road_objects.popleft()
            i += 1

    def log(self, message, message_type="info"):
        """ 
            Passes messages to the logger. 
        """
        if message_type == "info":
            logging.info(message)
        
        elif message_type == "warning":
            logging.warning(message)

        elif message_type == "error":
            logging.error(message)

    def _initialize_terrain(self, terrain):
        """
            Sets the terrain color for the space between the road and the horizon. 
        """

        if terrain in self.terrain_colors:
          self.terrain = self.terrain_colors[terrain]
        
        if terrain == "random":
            self.terrain = "random"

    def _initialize_frames(self):
        """
            Initializes the frames as numpy arrays based on the input size.
            Generates the standard drawing that each image includes: road lines, ground, center (optional).
            Creates n frames of BGR values of size SCREEN_HEIGHT X SCREEN_WIDTH
        """
        self.frames = [np.zeros((SCREEN_HEIGHT, SCREEN_WIDTH, 3), dtype=np.uint8) for _ in range(self.number_frames)]

        for frame in self.frames:
            ground_color = self.terrain if self.terrain != "random" else random.choice(self.terrain_colors.values())
            for line in ROAD_LINES:
                if line in { "left_ground", "right_ground" }:
                  cv2.fillPoly(frame, [ROAD_LINES[line]["geo"]], ground_color) 
                else:
                  cv2.fillPoly(frame, [ROAD_LINES[line]["geo"]], colors.white)
                if DEBUG:
                    # Draws a circle at the centerpoint of the frame
                    cv2.circle(frame, (int(CENTER[0]), int(CENTER[1])), radius=3, color=colors.red, thickness=1)
    
    def _initialize_labels(self):
        """
            Initializes the labels corresponding to the objects that are generated within the frames.
        """
        self.labels = [np.zeros((SCREEN_HEIGHT, SCREEN_WIDTH), dtype=np.uint8) for _ in range(self.number_frames)]

    def _initialize_median(self):
        """
            Initializes the median on the first frame.
        """
        # The first median line starts at the bottom of the screen and extends for its max length
        # at angle = median line angle
        start_y = SCREEN_HEIGHT
        start_x = SCREEN_WIDTH * MEDIAN_X_START
        # The gap that follows the first median line
        pre_gap = MEDIAN_LINE_GAP_MAX_LENGTH
        self.median_head = Median(start_x, start_y, CENTER, BOUNDS, pre_gap=pre_gap, prev=None)

        median = self.median_head
        # Initialize the rest of the medians
        for _ in range(self.number_medians):
            median.calculate_next_median()
            median = median.next
