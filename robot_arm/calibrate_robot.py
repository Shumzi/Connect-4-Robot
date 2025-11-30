import json
from time import sleep
from pymycobot import MyCobot280 as MyCobot

class Calibration:
    def __init__(self, robot: MyCobot):
        self.robot = robot
        self.calibration_data = {}

    def mark_location(self, name):
        """
        lets user move robot arm to named location then logs location there.
        """
        self.robot.power_on()
        sleep(1)
        angles = self.robot.get_angles()
        self.calibration_data[name] = angles
        print(f"Marked location '{name}': {angles}")

    def free_arm(self):
        """
        lets user move robot arm freely.
        """
        self.robot.release_all_servos()
    
    def save_calibration_data(self, filename="calibration_data.json"):
        """
        saves calibration data to a json file.
        """
        with open(filename, "w") as f:
            json.dump(self.calibration_data, f, indent=4)
    
    def load_calibration_data(self, filename="calibration_data.json"):
        """
        loads calibration data from a json file.
        """
        with open(filename, "r") as f:
            self.calibration_data = json.load(f)
    
    def test_move_to(self, name):
        """
        moves robot arm to a named location.
        """
        if name not in self.calibration_data:
            print(f"Location '{name}' not found in calibration data.")
            return
        angles = self.calibration_data[name]
        print(f"Moving to location '{name}': {angles}")
        self.robot.power_on()
        self.robot.send_angles(angles, 50)

    
    def calibrate(self):

        print("Calibrating robot...")
        print("Move arm to home position and press Enter")
        self.free_arm()
        input()
        self.mark_location("home")

        print("Now marking column positions...")
        for i in range(7):
            print(f"Move arm to column {i} position and press Enter")
            self.free_arm()
            input()
            self.mark_location(f"column_{i}")

        print("Now marking puck stack positions...")
        for color in ["red", "yellow"]:
            print(f"Move arm to {color} puck stack position and press Enter")
            self.free_arm()
            input()
            self.mark_location(color)
            # puck heights can be calculated manually with caliber.
        
        print("marking player dropoff location...")
        print("Move arm to player dropoff position and press Enter")
        self.free_arm()
        input()
        self.mark_location("player_dropoff")
        self.save_calibration_data()
        print("Calibration data saved to calibration_data.json")
    
    def play(self):
        self.load_calibration_data()
        while True:
            try:
                loc = input("Enter location to move to (or 'exit' to quit): ")
                if loc.lower() == 'exit':
                    break
                self.test_move_to(loc)
            except KeyboardInterrupt:
                break

if __name__ == "__main__":
    m = MyCobot("COM11")  # adjust port as needed
    calibration = Calibration(m)
    calibration.calibrate()
    # todo: understand why get_angles() can give you angles that you can't send back to the robot.
    # calibration.play()