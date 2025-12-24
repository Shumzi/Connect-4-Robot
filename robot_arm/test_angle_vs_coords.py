"""
Test script to compare angle-based vs coordinate-based robot control.
Tests responsiveness, reliability, and whether angles from get_angles() can be sent back.
"""

import json
from time import sleep, time
from pymycobot import MyCobot280 as MyCobot
import msvcrt
import sys

class AngleVsCoordsTester:
    def __init__(self, robot: MyCobot):
        self.robot = robot
        self.robot.power_on()
        sleep(0.5)
        
    def get_current_state(self):
        """Get current angles and coordinates"""
        try:
            angles_coords = self.robot.get_angles_coords()
            if angles_coords and len(angles_coords) >= 12:
                angles = angles_coords[:6]
                coords = angles_coords[6:]
                return angles, coords
        except Exception as e:
            print(f"Error getting state: {e}")
        return None, None
    
    def test_send_angles_direct(self, angles, speed=50):
        """Test sending angles directly"""
        start_time = time()
        try:
            self.robot.sync_send_angles(angles, speed)
            elapsed = time() - start_time
            return True, elapsed
        except Exception as e:
            elapsed = time() - start_time
            return False, elapsed, str(e)
    
    def test_send_coords_direct(self, coords, speed=50, mode=0):
        """Test sending coordinates directly"""
        start_time = time()
        try:
            # Try sync_send_coords first
            if hasattr(self.robot, 'sync_send_coords'):
                self.robot.sync_send_coords(coords, speed, mode)
            else:
                self.robot.send_coords(coords, speed, mode)
            elapsed = time() - start_time
            return True, elapsed
        except Exception as e:
            elapsed = time() - start_time
            return False, elapsed, str(e)
    
    def test_angle_roundtrip(self):
        """Test if angles from get_angles() can be sent back"""
        print("\n=== Testing Angle Roundtrip ===")
        print("Getting current angles...")
        angles, coords = self.get_current_state()
        
        if not angles:
            print("ERROR: Could not get current angles")
            return False
        
        print(f"Current angles: {angles}")
        print("Attempting to send these angles back...")
        
        success, elapsed, *error = self.test_send_angles_direct(angles, 50)
        
        if success:
            print(f"✓ SUCCESS: Angles sent back successfully in {elapsed:.2f}s")
            # Verify position
            sleep(0.5)
            new_angles, new_coords = self.get_current_state()
            if new_angles:
                angle_diff = [abs(a - b) for a, b in zip(angles, new_angles)]
                max_diff = max(angle_diff)
                print(f"  Angle differences: {[f'{d:.2f}°' for d in angle_diff]}")
                print(f"  Max difference: {max_diff:.2f}°")
                if max_diff < 5:
                    print("  ✓ Position matches (within 5°)")
                    return True
                else:
                    print(f"  ⚠ Position differs significantly ({max_diff:.2f}°)")
                    return False
        else:
            print(f"✗ FAILED: {error[0] if error else 'Unknown error'} (took {elapsed:.2f}s)")
            return False
    
    def test_coord_roundtrip(self):
        """Test if coordinates from get_coords() can be sent back"""
        print("\n=== Testing Coordinate Roundtrip ===")
        print("Getting current coordinates...")
        angles, coords = self.get_current_state()
        
        if not coords:
            print("ERROR: Could not get current coordinates")
            return False
        
        print(f"Current coords: {coords}")
        print("Attempting to send these coordinates back...")
        
        # Try mode 0 first
        success, elapsed, *error = self.test_send_coords_direct(coords, 50, 0)
        
        if not success:
            # Try mode 1
            print("Mode 0 failed, trying mode 1...")
            success, elapsed, *error = self.test_send_coords_direct(coords, 50, 1)
        
        if success:
            print(f"✓ SUCCESS: Coordinates sent back successfully in {elapsed:.2f}s")
            # Verify position
            sleep(0.5)
            new_angles, new_coords = self.get_current_state()
            if new_coords:
                coord_diff = [abs(a - b) for a, b in zip(coords[:3], new_coords[:3])]
                rot_diff = [abs(a - b) for a, b in zip(coords[3:], new_coords[3:])]
                max_pos_diff = max(coord_diff)
                max_rot_diff = max(rot_diff)
                print(f"  Position differences: {[f'{d:.2f}mm' for d in coord_diff]}")
                print(f"  Rotation differences: {[f'{d:.2f}°' for d in rot_diff]}")
                print(f"  Max position diff: {max_pos_diff:.2f}mm")
                print(f"  Max rotation diff: {max_rot_diff:.2f}°")
                if max_pos_diff < 10 and max_rot_diff < 10:
                    print("  ✓ Position matches (within 10mm, 10°)")
                    return True
                else:
                    print(f"  ⚠ Position differs significantly")
                    return False
        else:
            print(f"✗ FAILED: {error[0] if error else 'Unknown error'} (took {elapsed:.2f}s)")
            return False
    
    def test_responsiveness(self, num_tests=5):
        """Test responsiveness of both methods"""
        print("\n=== Testing Responsiveness ===")
        angles, coords = self.get_current_state()
        
        if not angles or not coords:
            print("ERROR: Could not get current state")
            return
        
        # Test angle responsiveness
        print("\nTesting ANGLE sending:")
        angle_times = []
        angle_successes = 0
        
        for i in range(num_tests):
            # Modify first angle slightly
            test_angles = angles.copy()
            test_angles[0] += 5.0 * (1 if i % 2 == 0 else -1)
            
            print(f"  Test {i+1}/{num_tests}: Sending angle {test_angles[0]:.1f}°...", end=" ", flush=True)
            success, elapsed, *error = self.test_send_angles_direct(test_angles, 50)
            
            if success:
                angle_times.append(elapsed)
                angle_successes += 1
                print(f"✓ {elapsed:.2f}s")
            else:
                print(f"✗ Failed: {error[0] if error else 'Unknown'}")
            sleep(0.2)
        
        # Reset to original
        self.test_send_angles_direct(angles, 50)
        sleep(0.5)
        
        # Test coordinate responsiveness
        print("\nTesting COORDINATE sending:")
        coord_times = []
        coord_successes = 0
        
        for i in range(num_tests):
            # Modify x coordinate slightly
            test_coords = coords.copy()
            test_coords[0] += 5.0 * (1 if i % 2 == 0 else -1)
            
            print(f"  Test {i+1}/{num_tests}: Sending x={test_coords[0]:.1f}mm...", end=" ", flush=True)
            success, elapsed, *error = self.test_send_coords_direct(test_coords, 50, 0)
            
            if success:
                coord_times.append(elapsed)
                coord_successes += 1
                print(f"✓ {elapsed:.2f}s")
            else:
                print(f"✗ Failed: {error[0] if error else 'Unknown'}")
            sleep(0.2)
        
        # Reset to original
        self.test_send_coords_direct(coords, 50, 0)
        sleep(0.5)
        
        # Summary
        print("\n=== Responsiveness Summary ===")
        if angle_times:
            avg_angle_time = sum(angle_times) / len(angle_times)
            print(f"Angles:  {angle_successes}/{num_tests} successful, avg {avg_angle_time:.2f}s")
        else:
            print(f"Angles:  0/{num_tests} successful")
        
        if coord_times:
            avg_coord_time = sum(coord_times) / len(coord_times)
            print(f"Coords:  {coord_successes}/{num_tests} successful, avg {avg_coord_time:.2f}s")
        else:
            print(f"Coords:  0/{num_tests} successful")
        
        if angle_times and coord_times:
            if avg_angle_time < avg_coord_time:
                print(f"\n✓ Angles are {avg_coord_time/avg_angle_time:.1f}x faster")
            else:
                print(f"\n✓ Coordinates are {avg_angle_time/avg_coord_time:.1f}x faster")
    
    def interactive_angle_test(self):
        """Interactive keyboard control for angles"""
        print("\n=== Interactive Angle Control ===")
        print("Controls:")
        print("  1-6: Adjust joint 1-6 by +5°")
        print("  q/a: Adjust joint 1 by +/-5°")
        print("  w/s: Adjust joint 2 by +/-5°")
        print("  e/d: Adjust joint 3 by +/-5°")
        print("  r/f: Adjust joint 4 by +/-5°")
        print("  t/g: Adjust joint 5 by +/-5°")
        print("  y/h: Adjust joint 6 by +/-5°")
        print("  p: Print current angles")
        print("  x: Exit")
        print()
        
        angles, coords = self.get_current_state()
        if not angles:
            print("ERROR: Could not get current angles")
            return
        
        print("Ready! Press keys to control the robot...")
        while True:
            try:
                if msvcrt.kbhit():
                    key = msvcrt.getch()
                    # Debug: show what key was pressed
                    # print(f"DEBUG: Key pressed: {key} (type: {type(key)})")
                    
                    moved = False
                    
                    # Handle both bytes and string keys
                    if isinstance(key, bytes):
                        key_str = key.decode('utf-8', errors='ignore').lower()
                    else:
                        key_str = str(key).lower()
                    
                    if key_str == '1' or key == b'1': 
                        angles[0] += 5; moved = True
                        print("Joint 1: +5°", end=" ", flush=True)
                    elif key_str == '2' or key == b'2': 
                        angles[1] += 5; moved = True
                        print("Joint 2: +5°", end=" ", flush=True)
                    elif key_str == '3' or key == b'3': 
                        angles[2] += 5; moved = True
                        print("Joint 3: +5°", end=" ", flush=True)
                    elif key_str == '4' or key == b'4': 
                        angles[3] += 5; moved = True
                        print("Joint 4: +5°", end=" ", flush=True)
                    elif key_str == '5' or key == b'5': 
                        angles[4] += 5; moved = True
                        print("Joint 5: +5°", end=" ", flush=True)
                    elif key_str == '6' or key == b'6': 
                        angles[5] += 5; moved = True
                        print("Joint 6: +5°", end=" ", flush=True)
                    elif key_str == 'q' or key == b'q': 
                        angles[0] += 5; moved = True
                        print("Joint 1: +5°", end=" ", flush=True)
                    elif key_str == 'a' or key == b'a': 
                        angles[0] -= 5; moved = True
                        print("Joint 1: -5°", end=" ", flush=True)
                    elif key_str == 'w' or key == b'w': 
                        angles[1] += 5; moved = True
                        print("Joint 2: +5°", end=" ", flush=True)
                    elif key_str == 's' or key == b's': 
                        angles[1] -= 5; moved = True
                        print("Joint 2: -5°", end=" ", flush=True)
                    elif key_str == 'e' or key == b'e': 
                        angles[2] += 5; moved = True
                        print("Joint 3: +5°", end=" ", flush=True)
                    elif key_str == 'd' or key == b'd': 
                        angles[2] -= 5; moved = True
                        print("Joint 3: -5°", end=" ", flush=True)
                    elif key_str == 'r' or key == b'r': 
                        angles[3] += 5; moved = True
                        print("Joint 4: +5°", end=" ", flush=True)
                    elif key_str == 'f' or key == b'f': 
                        angles[3] -= 5; moved = True
                        print("Joint 4: -5°", end=" ", flush=True)
                    elif key_str == 't' or key == b't': 
                        angles[4] += 5; moved = True
                        print("Joint 5: +5°", end=" ", flush=True)
                    elif key_str == 'g' or key == b'g': 
                        angles[4] -= 5; moved = True
                        print("Joint 5: -5°", end=" ", flush=True)
                    elif key_str == 'y' or key == b'y': 
                        angles[5] += 5; moved = True
                        print("Joint 6: +5°", end=" ", flush=True)
                    elif key_str == 'h' or key == b'h': 
                        angles[5] -= 5; moved = True
                        print("Joint 6: -5°", end=" ", flush=True)
                    elif key_str == 'p' or key == b'p':
                        current_angles, _ = self.get_current_state()
                        if current_angles:
                            print(f"\nCurrent angles: {current_angles}")
                        continue
                    elif key_str == 'x' or key == b'x':
                        break
                    else:
                        # Unknown key - show what was pressed for debugging
                        print(f"\nUnknown key: {key} (press q/a/w/s/e/d/r/f/t/g/y/h or 1-6)")
                        continue
                    
                    if moved:
                        start = time()
                        print(f"→ Sending: {[f'{a:.1f}°' for a in angles]}...", end=" ", flush=True)
                        success, elapsed, *error = self.test_send_angles_direct(angles, 50)
                        if success:
                            print(f"✓ ({elapsed:.2f}s)")
                        else:
                            print(f"✗ Failed: {error[0] if error else 'Unknown'}")
                
                sleep(0.05)
            except KeyboardInterrupt:
                break
        
        print("\nExiting angle control")
    
    def interactive_coord_test(self):
        """Interactive keyboard control for coordinates"""
        print("\n=== Interactive Coordinate Control ===")
        print("Controls:")
        print("  q/a: Move x by -/+5mm")
        print("  w/s: Move y by +/-5mm")
        print("  e/d: Move z by +/-5mm")
        print("  i/k: Adjust rx by +/-5°")
        print("  o/l: Adjust ry by +/-5°")
        print("  u/j: Adjust rz by +/-5°")
        print("  p: Print current coords")
        print("  x: Exit")
        print()
        
        angles, coords = self.get_current_state()
        if not coords:
            print("ERROR: Could not get current coordinates")
            return
        
        print("Ready! Press keys to control the robot...")
        while True:
            try:
                if msvcrt.kbhit():
                    key = msvcrt.getch()
                    
                    moved = False
                    
                    # Handle both bytes and string keys
                    if isinstance(key, bytes):
                        key_str = key.decode('utf-8', errors='ignore').lower()
                    else:
                        key_str = str(key).lower()
                    
                    if key_str == 'q' or key == b'q': 
                        coords[0] -= 5; moved = True
                        print("x: -5mm", end=" ", flush=True)
                    elif key_str == 'a' or key == b'a': 
                        coords[0] += 5; moved = True
                        print("x: +5mm", end=" ", flush=True)
                    elif key_str == 'w' or key == b'w': 
                        coords[1] += 5; moved = True
                        print("y: +5mm", end=" ", flush=True)
                    elif key_str == 's' or key == b's': 
                        coords[1] -= 5; moved = True
                        print("y: -5mm", end=" ", flush=True)
                    elif key_str == 'e' or key == b'e': 
                        coords[2] += 5; moved = True
                        print("z: +5mm", end=" ", flush=True)
                    elif key_str == 'd' or key == b'd': 
                        coords[2] -= 5; moved = True
                        print("z: -5mm", end=" ", flush=True)
                    elif key_str == 'i' or key == b'i': 
                        coords[3] += 5; moved = True
                        print("rx: +5°", end=" ", flush=True)
                    elif key_str == 'k' or key == b'k': 
                        coords[3] -= 5; moved = True
                        print("rx: -5°", end=" ", flush=True)
                    elif key_str == 'o' or key == b'o': 
                        coords[4] += 5; moved = True
                        print("ry: +5°", end=" ", flush=True)
                    elif key_str == 'l' or key == b'l': 
                        coords[4] -= 5; moved = True
                        print("ry: -5°", end=" ", flush=True)
                    elif key_str == 'u' or key == b'u': 
                        coords[5] += 5; moved = True
                        print("rz: +5°", end=" ", flush=True)
                    elif key_str == 'j' or key == b'j': 
                        coords[5] -= 5; moved = True
                        print("rz: -5°", end=" ", flush=True)
                    elif key_str == 'p' or key == b'p':
                        _, current_coords = self.get_current_state()
                        if current_coords:
                            print(f"\nCurrent coords: {current_coords}")
                        continue
                    elif key_str == 'x' or key == b'x':
                        break
                    else:
                        # Unknown key - show what was pressed for debugging
                        print(f"\nUnknown key: {key} (press q/a/w/s/e/d/i/k/o/l/p/; or x to exit)")
                        continue
                    
                    if moved:
                        start = time()
                        print(f"→ Sending: x={coords[0]:.1f}, y={coords[1]:.1f}, z={coords[2]:.1f}...", end=" ", flush=True)
                        success, elapsed, *error = self.test_send_coords_direct(coords, 50, 0)
                        if success:
                            print(f"✓ ({elapsed:.2f}s)")
                        else:
                            print(f"✗ Failed: {error[0] if error else 'Unknown'}")
                
                sleep(0.05)
            except KeyboardInterrupt:
                break
        
        print("\nExiting coordinate control")
    
    def run_all_tests(self):
        """Run all tests"""
        print("=" * 60)
        print("ROBOT ANGLE vs COORDINATE TESTING")
        print("=" * 60)
        
        # Test roundtrips
        angle_roundtrip_ok = self.test_angle_roundtrip()
        coord_roundtrip_ok = self.test_coord_roundtrip()
        
        # Test responsiveness
        self.test_responsiveness(5)
        
        # Summary
        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)
        print(f"Angle roundtrip: {'✓ WORKS' if angle_roundtrip_ok else '✗ FAILED'}")
        print(f"Coord roundtrip: {'✓ WORKS' if coord_roundtrip_ok else '✗ FAILED'}")
        print("\nNext steps:")
        print("  1. Run interactive_angle_test() to test angle control")
        print("  2. Run interactive_coord_test() to test coordinate control")
        print("  3. Compare responsiveness and ease of use")


def main():
    if len(sys.argv) > 1:
        port = sys.argv[1]
    else:
        port = "COM11"  # Default port
    
    print(f"Connecting to robot on {port}...")
    robot = MyCobot(port)
    
    tester = AngleVsCoordsTester(robot)
    
    print("\nChoose test mode:")
    print("  1. Run all automated tests")
    print("  2. Interactive angle control")
    print("  3. Interactive coordinate control")
    print("  4. Both interactive tests")
    
    choice = input("\nEnter choice (1-4): ").strip()
    
    if choice == "1":
        tester.run_all_tests()
    elif choice == "2":
        tester.interactive_angle_test()
    elif choice == "3":
        tester.interactive_coord_test()
    elif choice == "4":
        tester.interactive_angle_test()
        tester.interactive_coord_test()
    else:
        print("Invalid choice, running all tests...")
        tester.run_all_tests()


if __name__ == "__main__":
    main()

