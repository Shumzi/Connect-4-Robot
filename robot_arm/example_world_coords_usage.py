"""
Example: Using World Coordinates with Robot

This example shows how to:
1. Load the world coordinate transformation
2. Set the world reference on the robot
3. Use world coordinates directly
"""

from pymycobot import MyCobot280 as MyCobot
from world_coord_helper import load_world_transform


def main():
    # Initialize robot
    robot = MyCobot("COM11")  # Adjust port as needed
    
    # Load world coordinate transformation
    print("Loading world coordinate transformation...")
    world_coords = load_world_transform()
    
    # Get world reference parameters
    world_ref_params = world_coords.get_world_reference_params()
    print(f"World reference params: {world_ref_params}")
    
    # Set world reference on robot
    print("\nSetting world reference on robot...")
    robot.set_world_reference(world_ref_params)
    
    # Now you can use world coordinates directly!
    print("\nNow using world coordinates...")
    
    # Example: Move to position 100mm along X, 50mm along Y, 0mm Z (on floor)
    world_position = [0, 0, 10]
    
    # Get head orientation (facing floor)
    head_orientation = world_coords.get_head_orientation("floor")
    
    # Combine position and orientation
    world_coords_full = world_position + head_orientation
    
    print(f"Sending world coordinates: {world_coords_full}")
    robot.sync_send_coords(world_coords_full, 50)
    
    # Get current position in world coordinates
    current_robot_coords = robot.get_coords()
    current_world_pos, current_world_orient = world_coords.to_world(
        current_robot_coords[:3],
        current_robot_coords[3:]
    )
    print(f"\nCurrent position in world coordinates:")
    print(f"  Position: {current_world_pos}")
    print(f"  Orientation: {current_world_orient}")


if __name__ == "__main__":
    main()

