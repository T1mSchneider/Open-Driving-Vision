import cv2
import numpy as np
from ..const.constants import (SCREEN_HEIGHT, SCREEN_WIDTH, HORIZON_HEIGHT, CENTER, BOUNDS, MEDIAN_LINE_ANGLE,
                               ROAD_LINE_MAX_LENGTH, ROAD_LINE_GAP_MAX_LENGTH, IMG_OUTPUT_PATH, LABELS_OUTPUT_PATH,
                               LEFT_ROAD_LINE_START_HEIGHT1, LEFT_ROAD_LINE_START_HEIGHT2, LEFT_ROAD_LINE_END_WIDTH,
                               RIGHT_ROAD_LINE_START_WIDTH1, RIGHT_ROAD_LINE_START_WIDTH2, RIGHT_ROAD_LINE_END_WIDTH,
                               DEBUG, DURATION, MAX_CHAOS
                               )
from ..sim_objects.RoadLines import ROAD_LINES
from ..sim_objects.Colors import Colors

colors = Colors()

class Simulator:
    def __init__(self, number_frames: int, moving_speed: float, frame_rate: int, chaos: int=2):
        """
            Initializes the parent simulator class.
            Params:
                number_frames (int) - the total number_frames generated by the simulator,
                moving_speed (float) - the rate at which objects move per frame relative to the true horizon,
                frame_rate (int) - the frame rate for video output,
                chaos (int) - leads to a greater likelihood of more objects being created within a frame
        """
        assert(isinstance(number_frames, int) and number_frames <= 10000), "number_frames must be of type int and must be less than or equal to 10000."
        self.number_frames = int(number_frames)
        self.moving_speed = moving_speed
        self.frame_rate = frame_rate
        self.chaos = min(chaos, MAX_CHAOS)

        self._initialize_frames()
        self._initialize_labels()

    def _initialize_frames(self):
        """
            Initializes the frames as numpy arrays based on the input size.
            Creates n frames of BGR values of size SCREEN_HEIGHT X SCREEN_WIDTH
        """
        self.frames = [np.zeros((SCREEN_HEIGHT, SCREEN_WIDTH, 3), dtype=np.uint8) for _ in range(self.number_frames)]

        for frame in self.frames:
            for line in ROAD_LINES:
                cv2.fillPoly(frame, [ROAD_LINES[line]["geo"]], ROAD_LINES[line]["color"])  # Fill with white
                if DEBUG:
                    cv2.circle(frame, (int(CENTER[0]), int(CENTER[1])), radius=3, color=colors.red, thickness=1)

    
    def _initialize_labels(self):
        """
            Initializes the labels corresponding to the objects that are generated within the frames.
        """
        self.labels = [np.zeros((SCREEN_HEIGHT, SCREEN_WIDTH), dtype=np.uint8) for _ in range(self.number_frames)]
