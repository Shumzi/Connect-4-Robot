import json
import numpy as np
from time import sleep
from pathlib import Path
from pymycobot import MyCobot280 as MyCobot


class CalibrateWorldCoordSystem:
    def __init__(self, robot: MyCobot):
        self.robot = robot
        self.floor_points = []
        self.wall_points = []

    def collect_point(self, prompt: str) -> list:
        """Collect a single point from the robot."""
        print(f"\n{prompt}")
        print("Position the robot arm and press Enter to mark this point...")
        self.robot.release_all_servos()
        input()
        self.robot.power_on()
        sleep(0.5)
        coords = self.robot.get_coords()
        if not coords or len(coords) < 6:
            raise ValueError(f"Failed to get coordinates from robot")
        # Extract only position (x, y, z)
        point = coords[:3]
        print(f"Marked point: [{point[0]:.2f}, {point[1]:.2f}, {point[2]:.2f}]")
        return point

    def calibrate(self):
        """Main calibration routine - collects 6 points and calculates world coordinate system."""
        print("=" * 60)
        print("World Coordinate System Calibration")
        print("=" * 60)
        print("\nYou will mark 6 points total:")
        print("  - 3 points on the floor (non-collinear)")
        print("  - 3 points on the wall (non-collinear)")
        print("\nThe first floor point will become the origin (0, 0, 0)")
        print("The floor plane will become the XY plane (Z pointing up)")
        print("=" * 60)

        # Collect floor points
        print("\n--- FLOOR POINTS ---")
        for i in range(3):
            p = self.collect_point(f"Floor point {i+1}/3:")
            self.floor_points.append(p)

        # Collect wall points
        print("\n--- WALL POINTS ---")
        for i in range(3):
            p = self.collect_point(f"Wall point {i+1}/3:")
            self.wall_points.append(p)

        # Calculate coordinate system
        print("\n--- CALCULATING COORDINATE SYSTEM ---")
        transform_data = self.calculate_coordinate_system()

        # Ask for default head orientation
        print("\n--- HEAD ORIENTATION ---")
        print("Default head orientation:")
        print("  (f) Floor - head points downward")
        print("  (w) Wall - head points toward wall")
        choice = input("Choose (f/w) [default: f]: ").strip().lower()
        default_orientation = "floor" if choice != "w" else "wall"

        # Calculate head orientations
        head_orientations = self.calculate_head_orientations(transform_data)
        transform_data["head_orientations"] = head_orientations
        transform_data["default_head_orientation"] = default_orientation

        # Save to JSON
        output_file = Path(__file__).parent / "world_coord_transform.json"
        with open(output_file, "w") as f:
            json.dump(transform_data, f, indent=2)
        print(f"\n--- SAVED ---")
        print(f"Transformation data saved to: {output_file}")

        # Display summary
        self.display_summary(transform_data)

        return transform_data

    def calculate_coordinate_system(self):
        """Calculate world coordinate system from floor and wall points."""
        # Convert to numpy arrays
        p1, p2, p3 = [np.array(p) for p in self.floor_points]
        p4, p5, p6 = [np.array(p) for p in self.wall_points]

        # Calculate floor plane normal
        v1 = p2 - p1
        v2 = p3 - p1
        n_floor = np.cross(v1, v2)
        n_floor_norm = np.linalg.norm(n_floor)
        
        if n_floor_norm < 1e-6:
            raise ValueError("Floor points are collinear! Please choose non-collinear points.")
        
        n_floor = n_floor / n_floor_norm

        # Calculate wall plane normal
        v3 = p5 - p4
        v4 = p6 - p4
        n_wall = np.cross(v3, v4)
        n_wall_norm = np.linalg.norm(n_wall)
        
        if n_wall_norm < 1e-6:
            raise ValueError("Wall points are collinear! Please choose non-collinear points.")
        
        n_wall = n_wall / n_wall_norm

        # Check if planes are parallel
        cross_normals = np.cross(n_floor, n_wall)
        if np.linalg.norm(cross_normals) < 1e-6:
            raise ValueError("Floor and wall planes are parallel! Please adjust points.")

        # Ensure Z-axis points upward (floor normal pointing up)
        if n_floor[2] < 0:
            n_floor = -n_floor

        # Build coordinate system
        # X-axis: intersection line of floor and wall planes
        X = np.cross(n_floor, n_wall)
        X = X / np.linalg.norm(X)

        # Z-axis: floor normal (pointing up)
        Z = n_floor.copy()

        # Y-axis: right-handed completion
        Y = np.cross(Z, X)
        Y = Y / np.linalg.norm(Y)

        # Verify right-handed coordinate system
        det = np.linalg.det(np.column_stack([X, Y, Z]))
        if abs(det - 1.0) > 0.1:
            print(f"Warning: Coordinate system determinant is {det:.3f} (should be ~1.0)")

        # Build rotation matrix (columns are X, Y, Z)
        R = np.column_stack([X, Y, Z])

        # Origin is first floor point
        origin = p1.tolist()

        # Convert rotation matrix to Euler angles (ZYX convention for pymycobot)
        # This gives us rx, ry, rz for set_world_reference()
        euler_angles = self.rotation_matrix_to_euler_zyx(R)

        # Calculate world reference parameters for set_world_reference()
        # Position: origin in robot base coordinates
        # Orientation: Euler angles from rotation matrix
        world_reference_params = origin + euler_angles

        return {
            "origin": origin,
            "rotation_matrix": R.tolist(),
            "coordinate_axes": {
                "x": X.tolist(),
                "y": Y.tolist(),
                "z": Z.tolist()
            },
            "floor_plane": {
                "normal": n_floor.tolist(),
                "points": [p.tolist() for p in [p1, p2, p3]]
            },
            "wall_plane": {
                "normal": n_wall.tolist(),
                "points": [p.tolist() for p in [p4, p5, p6]]
            },
            "world_reference_params": world_reference_params,  # [x, y, z, rx, ry, rz]
            "euler_angles": euler_angles
        }

    def rotation_matrix_to_euler_zyx(self, R):
        """
        Convert rotation matrix to Euler angles using ZYX convention.
        This matches pymycobot's convention (rz, ry, rx order).
        
        Returns: [rx, ry, rz] in degrees
        """
        # Extract angles using ZYX (intrinsic) convention
        # This is equivalent to extrinsic XYZ
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

        # Convert to degrees
        rx_deg = np.degrees(rx)
        ry_deg = np.degrees(ry)
        rz_deg = np.degrees(rz)

        return [rx_deg, ry_deg, rz_deg]

    def calculate_head_orientations(self, transform_data):
        """Calculate head orientation direction vectors and Euler angles."""
        n_floor = np.array(transform_data["floor_plane"]["normal"])
        n_wall = np.array(transform_data["wall_plane"]["normal"])

        # Facing floor: point downward (negative floor normal)
        d_floor = -n_floor
        euler_floor = self.direction_to_euler(d_floor)

        # Facing wall: point toward wall (use wall normal, check direction)
        # For now, use wall normal directly (user can adjust if needed)
        d_wall = n_wall
        euler_wall = self.direction_to_euler(d_wall)

        return {
            "facing_floor": {
                "direction_vector": d_floor.tolist(),
                "euler_angles": euler_floor
            },
            "facing_wall": {
                "direction_vector": d_wall.tolist(),
                "euler_angles": euler_wall
            }
        }

    def direction_to_euler(self, direction):
        """
        Convert direction vector to Euler angles.
        Sets roll (rz) to 0 to avoid J6 spinning issues.
        
        Returns: [rx, ry, rz] in degrees
        """
        d = direction / np.linalg.norm(direction)
        
        # Calculate pitch and yaw
        pitch = -np.arcsin(np.clip(d[2], -1, 1))  # How much up/down
        yaw = np.arctan2(d[1], d[0])  # How much left/right
        
        # Set roll to 0 to avoid J6 spinning
        roll = 0
        
        # Convert to degrees
        rx = np.degrees(pitch)
        ry = np.degrees(roll)
        rz = np.degrees(yaw)
        
        return [rx, ry, rz]

    def display_summary(self, transform_data):
        """Display calibration summary."""
        print("\n" + "=" * 60)
        print("CALIBRATION SUMMARY")
        print("=" * 60)
        
        print(f"\nOrigin (P1): {transform_data['origin']}")
        
        print(f"\nCoordinate Axes:")
        print(f"  X-axis: {[f'{x:.3f}' for x in transform_data['coordinate_axes']['x']]}")
        print(f"  Y-axis: {[f'{y:.3f}' for y in transform_data['coordinate_axes']['y']]}")
        print(f"  Z-axis: {[f'{z:.3f}' for z in transform_data['coordinate_axes']['z']]}")
        
        print(f"\nWorld Reference Parameters (for set_world_reference()):")
        wrp = transform_data['world_reference_params']
        print(f"  Position: [{wrp[0]:.2f}, {wrp[1]:.2f}, {wrp[2]:.2f}]")
        print(f"  Rotation: [rx={wrp[3]:.2f}°, ry={wrp[4]:.2f}°, rz={wrp[5]:.2f}°]")
        
        print(f"\nHead Orientations:")
        ho = transform_data['head_orientations']
        print(f"  Facing Floor: rx={ho['facing_floor']['euler_angles'][0]:.2f}°, "
              f"ry={ho['facing_floor']['euler_angles'][1]:.2f}°, "
              f"rz={ho['facing_floor']['euler_angles'][2]:.2f}°")
        print(f"  Facing Wall: rx={ho['facing_wall']['euler_angles'][0]:.2f}°, "
              f"ry={ho['facing_wall']['euler_angles'][1]:.2f}°, "
              f"rz={ho['facing_wall']['euler_angles'][2]:.2f}°")
        
        print("\n" + "=" * 60)
        print("Next steps:")
        print("1. Load transformation: world_coords = load_world_transform('world_coord_transform.json')")
        print("2. Set world reference: robot.set_world_reference(world_coords.get_world_reference_params())")
        print("3. Use world coordinates directly in robot.send_coords()")
        print("=" * 60)


if __name__ == "__main__":
    robot = MyCobot("COM11")  # Adjust port as needed
    calibrate = CalibrateWorldCoordSystem(robot)
    try:
        transform_data = calibrate.calibrate()
    except KeyboardInterrupt:
        print("\n\nCalibration cancelled by user")
    except Exception as e:
        print(f"\n\nError during calibration: {e}")
        import traceback
        traceback.print_exc()
