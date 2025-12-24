import json
from time import sleep
from pymycobot import MyCobot280 as MyCobot

class TestCalibration:
    def __init__(self, robot: MyCobot, calibration_file: str = "robot_angles.json"):
        self.robot = robot
        self.calibration_file = calibration_file
        self.calibration_data = {}
        self.load_calibration_data()

    def load_calibration_data(self):
        with open(self.calibration_file, 'r') as f:
            self.calibration_data = json.load(f)

    def loop_over_locations(self):
        print("looping over locations...")
        print("press Enter to move to next location")
        print("press Ctrl+C to stop")
        input()
        try:
            for location in self.calibration_data:
                print(f"Moving to {location}")
                self.robot.sync_send_angles(self.calibration_data[location], 50)
                input()
                sleep(1)
        except KeyboardInterrupt:
            print("Stopping loop")
            self.robot.release_all_servos()
            return
    
if __name__ == "__main__":
    robot = MyCobot("COM11")
    test_calibration = TestCalibration(robot)
    test_calibration.loop_over_locations()