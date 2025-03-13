SCREEN_HEIGHT, SCREEN_WIDTH = 800, 1216
HORIZON_HEIGHT = 0.45
CENTER = (0.49 * SCREEN_WIDTH + 5, HORIZON_HEIGHT * SCREEN_HEIGHT - 16)
BOUNDS = (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)

ROAD_LINE_MAX_LENGTH = int(SCREEN_HEIGHT * 0.18)
ROAD_LINE_GAP_MAX_LENGTH  = int(SCREEN_HEIGHT * 0.2232)

MEDIAN_LINE_ANGLE = 63.018

LEFT_ROAD_LINE_START_HEIGHT1 = 0.87
LEFT_ROAD_LINE_START_HEIGHT2 = 0.88
LEFT_ROAD_LINE_END_WIDTH = 0.48

RIGHT_ROAD_LINE_START_WIDTH1 = 0.86
RIGHT_ROAD_LINE_START_WIDTH2 = 0.87
RIGHT_ROAD_LINE_END_WIDTH = 0.50

PLACEMENT_DEVIATION = 0.05
MINIMUM_PLACEMENT_DEVIATION = 0.022
LEFT_PLACEMENT_PROB = 1

MINIMUM_POLE_HEIGHT = 20#px
MINIMUM_POLE_WIDTH =  1#px

DEBUG = False

OUTPUT_PATH = ".\src\outputs"

