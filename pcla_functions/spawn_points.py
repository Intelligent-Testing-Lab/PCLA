import carla

"""
This script draws the spawn points in the CARLA simulator as their corresponding numbers.
"""


def draw_spawn_points(world, life_time=20):
    # Connect to the client and retrieve the world object
    client = carla.Client("localhost", 2000)
    world = client.get_world()

    # Set up the simulator in synchronous mode
    settings = world.get_settings()
    settings.synchronous_mode = True  # Enables synchronous mode
    settings.fixed_delta_seconds = 0.05
    world.apply_settings(settings)

    spawn_points = world.get_map().get_spawn_points()
    # Draw the spawn point locations as numbers in the map
    for i, spawn_point in enumerate(spawn_points):
        world.debug.draw_string(spawn_point.location, str(i), life_time=life_time)

    world.tick()

    settings.synchronous_mode = False  # Disables synchronous mode
    world.apply_settings(settings)
