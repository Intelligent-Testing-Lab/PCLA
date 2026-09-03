import colorsys
import sys
from pathlib import Path

import carla

sys.path.append(str(Path(__file__).parent.parent))

from leaderboard_codes.global_route_planner import GlobalRoutePlanner
from leaderboard_codes.global_route_planner_dao import GlobalRoutePlannerDAO


def location_to_waypoint(client, starting_location, ending_location, distance=2, draw=False, color=None):
    # This function is used to generate waypoints between two locations
    world = client.get_world()
    amap = world.get_map()
    dao = GlobalRoutePlannerDAO(amap, distance)
    grp = GlobalRoutePlanner(dao)
    grp.setup()
    w1 = grp.trace_route(starting_location, ending_location)
    
    # draw the route on the carla simulator
    if draw:
        n = max(len(w1) - 1, 1)
        for i, w in enumerate(w1):
            t = i / n
            # sweep the hue the "long way" so we go green → cyan → blue → magenta → red
            if color is None:
                hue = 0.33 - 0.33 * t
                r, g, b = colorsys.hsv_to_rgb(hue, 1.0, 1.0)
                color = carla.Color(int(r*255), int(g*255), int(b*255))
            

            world.debug.draw_string(w[0].transform.location, 'O', draw_shadow=False,
                                     color=color, life_time=30.0, persistent_lines=True)
    
    return [wp[0] for wp in w1]
