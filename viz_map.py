import argparse
import pickle

import carla
import matplotlib.pyplot as plt


class Line:
    def __init__(self):
        self.x = []
        self.y = []


class MapVisualization:
    def __init__(self, args):
        self.carla_client = carla.Client(args.host, args.port, worker_threads=1)
        self.carla_client.set_timeout(30.0)
        # self.carla_client.load_world(args.map)
        self.world = self.carla_client.get_world()
        self.map = self.world.get_map()
        self.fig, self.ax = plt.subplots(figsize=(10, 10))
        self.line_list = []

    def destroy(self):
        self.carla_client = None
        self.world = None
        self.map = None

    @staticmethod
    def lateral_shift(transform, shift):
        """Makes a lateral shift of the forward vector of a transform"""
        transform.rotation.yaw += 90
        return transform.location + shift * transform.get_forward_vector()

    def draw_line(self, points: list):
        x = []
        y = []
        for p in points:
            x.append(p.x)
            y.append(-p.y)
        line = Line()
        line.x = x
        line.y = y
        self.line_list.append(line)
        self.ax.plot(x, y, color="darkslategrey", markersize=2, linewidth=1)
        return True

    def draw_spawn_points(self):
        spawn_points = self.map.get_spawn_points()
        for i in range(len(spawn_points)):
            p = spawn_points[i]
            x = p.location.x
            y = -p.location.y
            self.ax.scatter(
                x,
                y,
                color="darkorange",
                s=10,  # Size of marker
                zorder=5,  # Draws on top of road lines
                label="Spawn Points",
            )

    def draw_roads(self):
        precision = 0.1
        topology = self.map.get_topology()
        topology = [x[0] for x in topology]
        topology = sorted(topology, key=lambda w: w.transform.location.z)
        set_waypoints = []
        for waypoint in topology:
            waypoints = [waypoint]
            nxt = waypoint.next(precision)
            if len(nxt) > 0:
                nxt = nxt[0]
                while nxt.road_id == waypoint.road_id:
                    waypoints.append(nxt)
                    nxt = nxt.next(precision)
                    if len(nxt) > 0:
                        nxt = nxt[0]
                    else:
                        break
            set_waypoints.append(waypoints)

        for waypoints in set_waypoints:
            road_left_side = [self.lateral_shift(w.transform, -w.lane_width * 0.5) for w in waypoints]
            road_right_side = [self.lateral_shift(w.transform, w.lane_width * 0.5) for w in waypoints]

            if len(road_left_side) > 2:
                self.draw_line(points=road_left_side)
            if len(road_right_side) > 2:
                self.draw_line(points=road_right_side)


def main():
    argparser = argparse.ArgumentParser(description=__doc__)
    argparser.add_argument(
        "--host",
        metavar="H",
        default="localhost",
        help="IP of the host CARLA Simulator (default: localhost)",
    )
    argparser.add_argument(
        "-p",
        "--port",
        metavar="P",
        default=2000,
        type=int,
        help="TCP port of CARLA Simulator (default: 2000)",
    )
    argparser.add_argument("-m", "--map", default="Town02", help="Load a new map to visualize")

    args = argparser.parse_args()
    viz = MapVisualization(args)
    viz.draw_roads()
    viz.draw_spawn_points()

    # Set title with the map name
    map_title = viz.map.name.split("/")[-1]
    viz.ax.set_title(f"CARLA Map: {map_title}", fontsize=14, fontweight="bold")
    viz.ax.set_aspect("equal", adjustable="box")

    # Save visualization info to pickle
    with open("/tmp/map_info.pkl", "wb") as pickle_file:
        pickle.dump(viz.line_list, pickle_file)

    viz.destroy()

    # Apply tight layout and save figure to PDF
    pdf_filename = f"./{args.map}.pdf"
    plt.tight_layout()
    plt.savefig(pdf_filename, format="pdf", bbox_inches="tight")
    print(f"Saved map visualization to {pdf_filename}")

    plt.show()


if __name__ == "__main__":
    main()
