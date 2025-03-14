import random
from .RandomPlacementGenerator import RandomPlacementGenerator
from .RoadSignBuilds import Builder
from ..sim_objects.road_objects.RoadSign import RoadSign
from ..sim_objects.Colors import Colors
from ..const.constants import (SCREEN_HEIGHT, SCREEN_WIDTH, RIGHT_ROAD_LINE_END_WIDTH, LEFT_ROAD_LINE_END_WIDTH, HORIZON_HEIGHT, PLACEMENT_DEVIATION, LEFT_PLACEMENT_PROB)

random.seed()

colors = Colors()

LEFT = (LEFT_ROAD_LINE_END_WIDTH * SCREEN_WIDTH, SCREEN_HEIGHT * HORIZON_HEIGHT)
RIGHT = (RIGHT_ROAD_LINE_END_WIDTH * SCREEN_WIDTH, SCREEN_HEIGHT * HORIZON_HEIGHT)

# Places objects coming friom the left of the left road line
left_line_placement_generator = RandomPlacementGenerator(0, LEFT[0], LEFT[1], SCREEN_HEIGHT, anchor="top_right", deviation=PLACEMENT_DEVIATION)
# Places objects coming from right of the right road line
right_line_placement_generator = RandomPlacementGenerator(RIGHT[0], SCREEN_WIDTH, RIGHT[1], SCREEN_HEIGHT, anchor="top_left", deviation=PLACEMENT_DEVIATION) 

class RoadSignGenerator:
    def __init__(self, center: tuple, bounds: tuple):
        """
            Objects are generated to appear with their base on the horizon line. 
            Objects must appear either to the left of the left road line or right of the right road line.
        """
        self.center = center
        self.bounds = bounds
        self.builder = Builder(center, bounds)


    def generate_roadsign(self, roadsign_name: str, side: str):
        """

            Builds a roadsign by randomly placing its origin and drawing its initial shape on the horizon.
        
        """
        roadsign_params = self.builder.builds[roadsign_name].copy()
        
        if (side == "left"):
            # left means that its anchored to the left road line
            initial_placement = ("left", left_line_placement_generator.randomize_placement())
        elif (side == "right"):
            # right means that its anchored to the right road line
            initial_placement = ("right", right_line_placement_generator.randomize_placement())
        
        pole = self.builder.build_pole(initial_placement[1])
        start_sign_point = self._get_sign_start_point(pole)

        # Map the signs to their functions
        funcs = {
            "diamond_warning_sign": self.builder.build_diamond_sign(start_sign_point),
            "speed_limit_sign": self.builder.build_speed_limit_sign(start_sign_point),
            "stop_sign": self.builder.build_stop_sign(start_sign_point),
            "small_informational_sign": self.builder.build_small_informational_sign(start_sign_point),
            "large_informational_sign": self.builder.build_large_informational_sign(start_sign_point),
            "yield_sign": self.builder.build_yield_sign(start_sign_point),
            "freeway_sign": self.builder.build_freeway_sign(start_sign_point),
            "traffic_cone": self.builder.build_traffic_cone(initial_placement[1], initial_placement[0])
        }

        main_shape = funcs[roadsign_name]

        roadsign_params["args"][0] = main_shape
        roadsign_params["args"][1] = pole
        roadsign_params["args"] = tuple(roadsign_params["args"])

        roadsign_params["kwargs"]["reverse_sign"] = initial_placement[0] == "left"
            
        return RoadSign(*roadsign_params["args"], **roadsign_params["kwargs"])
        
    def _get_sign_start_point(self, pole):
        return ((pole[2][0] + pole[3][0]) / 2, pole[2][1])


    