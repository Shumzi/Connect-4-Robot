"""
World Coordinate System Helper Module

Provides utilities for loading and using world coordinate transformations.
After calibration, use this module to work with world coordinates.
"""

import json
import numpy as np
from pathlib import Path


class WorldCoordSystem:
    """Manages world coordinate system transformation."""
    
    def __init__(self, transform_data: dict):
        """
        Initialize with transformation data.
        
        Args:
            transform_data: Dictionary containing transformation parameters
                (loaded from world_coord_transform.json)
        """
        self.origin = np.array(transform_data["origin"])
        self.R = np.array(transform_data["rotation_matrix"])  # Rotation matrix
        self.R_inv = self.R.T  # Inverse rotation (transpose for orthogonal matrix)
        self.coordinate_axes = transform_data["coordinate_axes"]
        self.head_orientations = transform_data.get("head_orientations", {})
        self.default_head_orientation = transform_data.get("default_head_orientation", "floor")
        
    def get_world_reference_params(self):
        """
        Get parameters for robot.set_world_reference().
        
        Returns:
            List [x, y, z, rx, ry, rz] in format expected by set_world_reference()
        """
        return self.origin.tolist() + self._rotation_matrix_to_euler_zyx(self.R)
    
    def to_world(self, robot_pos, robot_orientation=None):
        """
        Convert robot coordinates to world coordinates.
        
        Args:
            robot_pos: [x, y, z] position in robot base coordinates
            robot_orientation: Optional [rx, ry, rz] orientation in robot coordinates
        
        Returns:
            world_pos: [x, y, z] position in world coordinates
            world_orientation: [rx, ry, rz] orientation in world coordinates (if provided)
        """
        robot_pos = np.array(robot_pos)
        
        # Transform position: translate to origin, then rotate
        world_pos = self.R @ (robot_pos - self.origin)
        
        if robot_orientation is not None:
            # Convert orientation: convert Euler angles to rotation matrix,
            # apply world rotation, convert back
            robot_orientation = np.array(robot_orientation)
            R_robot_orient = self._euler_zyx_to_rotation_matrix(robot_orientation)
            R_world_orient = self.R @ R_robot_orient
            world_orientation = self._rotation_matrix_to_euler_zyx(R_world_orient)
            return world_pos.tolist(), world_orientation
        
        return world_pos.tolist()
    
    def to_robot(self, world_pos, world_orientation=None):
        """
        Convert world coordinates to robot coordinates.
        
        Args:
            world_pos: [x, y, z] position in world coordinates
            world_orientation: Optional [rx, ry, rz] orientation in world coordinates
        
        Returns:
            robot_pos: [x, y, z] position in robot base coordinates
            robot_orientation: [rx, ry, rz] orientation in robot coordinates (if provided)
        """
        world_pos = np.array(world_pos)
        
        # Transform position: rotate back, then translate
        robot_pos = self.R_inv @ world_pos + self.origin
        
        if world_orientation is not None:
            # Convert orientation: convert Euler angles to rotation matrix,
            # apply inverse world rotation, convert back
            world_orientation = np.array(world_orientation)
            R_world_orient = self._euler_zyx_to_rotation_matrix(world_orientation)
            R_robot_orient = self.R_inv @ R_world_orient
            robot_orientation = self._rotation_matrix_to_euler_zyx(R_robot_orient)
            return robot_pos.tolist(), robot_orientation
        
        return robot_pos.tolist()
    
    def get_head_orientation(self, facing="floor"):
        """
        Get Euler angles for head orientation.
        
        Args:
            facing: "floor" or "wall"
        
        Returns:
            [rx, ry, rz] Euler angles in world coordinates
        """
        if facing not in ["floor", "wall"]:
            facing = self.default_head_orientation
        
        if facing in self.head_orientations:
            return self.head_orientations[facing]["euler_angles"]
        else:
            raise ValueError(f"Head orientation '{facing}' not found in calibration data")
    
    def _rotation_matrix_to_euler_zyx(self, R):
        """Convert rotation matrix to Euler angles (ZYX convention)."""
        sy = np.sqrt(R[0, 0]**2 + R[1, 0]**2)
        singular = sy < 1e-6
        
        if not singular:
            rx = np.arctan2(R[2, 1], R[2, 2])
            ry = np.arctan2(-R[2, 0], sy)
            rz = np.arctan2(R[1, 0], R[0, 0])
        else:
            rx = np.arctan2(-R[1, 2], R[1, 1])
            ry = np.arctan2(-R[2, 0], sy)
            rz = 0
        
        return [np.degrees(rx), np.degrees(ry), np.degrees(rz)]
    
    def _euler_zyx_to_rotation_matrix(self, euler_angles):
        """Convert Euler angles (ZYX convention) to rotation matrix."""
        rx, ry, rz = np.radians(euler_angles)
        
        # ZYX rotation (intrinsic) = XYZ rotation (extrinsic)
        # R = Rz(rz) * Ry(ry) * Rx(rx)
        cx, sx = np.cos(rx), np.sin(rx)
        cy, sy = np.cos(ry), np.sin(ry)
        cz, sz = np.cos(rz), np.sin(rz)
        
        R = np.array([
            [cy*cz, -cy*sz, sy],
            [cx*sz + sx*sy*cz, cx*cz - sx*sy*sz, -sx*cy],
            [sx*sz - cx*sy*cz, sx*cz + cx*sy*sz, cx*cy]
        ])
        
        return R


def load_world_transform(json_path=None):
    """
    Load world coordinate transformation from JSON file.
    
    Args:
        json_path: Path to world_coord_transform.json file.
                   If None, looks in robot_arm/ directory.
    
    Returns:
        WorldCoordSystem object
    """
    if json_path is None:
        json_path = Path(__file__).parent / "world_coord_transform.json"
    else:
        json_path = Path(json_path)
    
    if not json_path.exists():
        raise FileNotFoundError(
            f"World coordinate transform file not found: {json_path}\n"
            "Please run calibrate_world_coord_system.py first."
        )
    
    with open(json_path, "r") as f:
        transform_data = json.load(f)
    
    return WorldCoordSystem(transform_data)


# Example usage
if __name__ == "__main__":
    # Load transformation
    world_coords = load_world_transform()
    
    # Get world reference parameters for set_world_reference()
    world_ref_params = world_coords.get_world_reference_params()
    print("World reference parameters for set_world_reference():")
    print(f"  {world_ref_params}")
    
    # Get head orientation
    floor_orientation = world_coords.get_head_orientation("floor")
    print(f"\nHead orientation (facing floor): {floor_orientation}")
    
    wall_orientation = world_coords.get_head_orientation("wall")
    print(f"Head orientation (facing wall): {wall_orientation}")

