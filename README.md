# Connect 4 Robot

A robotic Connect 4 game where a MyCobot 280 robot arm plays against a human player. The system uses computer vision-free drop detection via LED strip sensors, automated puck dispensing with solenoids, and AI-powered gameplay.

## System Overview

```
┌─────────────────────────────────────────────┐
│                PC MAIN CONTROLLER           │
│  ┌────────────┬────────────┐               │
│  │   Robot    │   Arduino  │               │
│  │ Interface  │ Interface  │               │
│  └────────────┴────────────┘               │
└─────────────┬──────┬───────────────────────┘
              │      │
        USB Serial   USB Serial
              │      │
     ┌────────▼─┐ ┌───▼─────────────┐
     │  Robot   │ │   Arduino       │
     │  Arm     │ │ - LED Strip     │
     │ (MyCobot)│ │ - Solenoids     │
     │          │ │ - Sensors       │
     └──────────┘ └────────────────┘
```

## Architecture

The system consists of three main controllers:

1. **PC Main Controller** - Orchestrates gameplay, runs AI, manages state
2. **Arduino Controller** - Handles LED strip, solenoid puck release, drop detection sensors
3. **MyCobot 280 Robot Arm** - Picks and places pucks, delivers pucks to player

### Design Philosophy

- **Event-Driven Architecture**: Hardware events trigger game logic responses
- **Physical Safety**: Robot hands puck to player, preventing simultaneous moves
- **Simulation-First**: Mock hardware layer enables development without physical components
- **Clear Ownership**: Game logic owns board state, hardware interfaces handle I/O only

## Project Structure

```
connect4-robot/
│
├── requirements.txt           # Python dependencies
├── config.yaml                # Hardware ports, AI settings, simulation flags
│
├── pc_controller/             # Main PC application
│   ├── main.py                # Entry point, orchestration
│   ├── game.py                # Game logic (event-driven)
│   │
│   ├── core/                  # Pure game logic
│   │   ├── board.py           # Board state, win detection
│   │   └── ai.py              # Minimax AI engine
│   │
│   ├── hardware/              # Hardware interfaces
│   │   ├── arduino.py         # Serial communication with Arduino
│   │   ├── robot.py           # Robot arm control (wraps legacy code)
│   │   └── mock.py            # Simulation layer
│   │
│   └── utils/
│       └── logger.py          # Centralized logging
│
├── legacy/                    # Original robot interface code
│   └── ArmInterface.py        # Existing pymycobot wrapper (reused)
│
├── arduino_controller/        # Arduino firmware
│   └── arduino_main/
│       ├── arduino_main.ino   # Main sketch
│       ├── config.h           # Pin definitions
│       ├── led_control.h/.cpp # LED strip management
│       ├── solenoid_control.h/.cpp # Puck release system
│       └── sensor_handler.h/.cpp   # Drop detection
│
├── robot_arm/                 # Robot-specific files
│   ├── positions.json         # Calibrated arm positions
│   └── calibrate_robot.py     # Interactive calibration script
│
├── simulation/                # Testing without hardware
│   └── test_game_flow.py      # Automated game flow tests
│
└── docs/
    ├── architecture.md        # Detailed design documentation
    ├── serial_protocol.md     # Arduino ↔ PC communication spec
    └── setup_guide.md         # First-time setup instructions
```

## Key Components

### Game Logic (`game.py`)
- **Responsibilities**: Orchestrate turns, check win/draw, trigger robot moves
- **Event Handler**: `on_player_drop(column)` - called when Arduino detects puck
- **Flow**: Player drops → Update board → Check win → Calculate AI move → Execute robot → Repeat

### Board (`core/board.py`)
- **Responsibilities**: Store state, validate moves, detect wins
- **Pure Logic**: No hardware dependencies, easily testable
- **API**: `drop_piece()`, `is_valid_move()`, `check_win()`, `is_draw()`, `get_state()`

### AI Engine (`core/ai.py`)
- **Algorithm**: Minimax with alpha-beta pruning
- **Input**: Board state as 2D array
- **Output**: Best column to play (0-6)
- **Configurable**: Search depth adjustable via `config.yaml`

### Arduino Interface (`hardware/arduino.py`)
- **Responsibilities**: Serial communication, command sending, event callbacks
- **Commands**: `RELEASE:<col>`, `LED:<col>:<R,G,B>`, `RESET`, `STATUS`
- **Events**: `DROP:<col>` (puck detected), `READY`, `ERROR:<msg>`
- **Thread Model**: Background listener thread for async event handling

### Robot Interface (`hardware/robot.py`)
- **Wrapper**: Clean API around legacy `ArmInterface.py`
- **Methods**: `place_puck_at_column(col)`, `give_player_puck()`, `move_to_home()`
- **Position Management**: Loads calibrated positions from `positions.json`

### Mock Hardware (`hardware/mock.py`)
- **Purpose**: Enable development/testing without physical hardware
- **Classes**: `MockArduino`, `MockRobot`
- **Usage**: Set `simulation: true` in `config.yaml`

## Setup

### Prerequisites

- **Hardware** (for production use):
  - MyCobot 280 robot arm (M5 Stack version)
  - Arduino with custom PCB (LED strip + solenoid drivers + sensors)
  - USB connections for both
  
- **Software**:
  - Python 3.8+
  - Arduino IDE (for firmware upload)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd connect4-robot
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure hardware ports**
   
   Edit `config.yaml`:
   ```yaml
   simulation:
     robot: false      # Set true to use mock
     arduino: false    # Set true to use mock
   
   hardware:
     robot:
       port: "/dev/ttyUSB0"  # Adjust for your system
       baudrate: 115200
     arduino:
       port: "/dev/ttyUSB1"  # Adjust for your system
       baudrate: 9600
   
   game:
     ai_depth: 4  # Minimax search depth (4 = good balance)
   ```

4. **Upload Arduino firmware**
   ```bash
   # Open Arduino IDE
   # Load arduino_controller/arduino_main/arduino_main.ino
   # Select your board and port
   # Upload
   ```

5. **Calibrate robot arm** (first time only)
   ```bash
   python robot_arm/calibrate_robot.py
   # Follow interactive prompts to record positions
   # Positions saved to robot_arm/positions.json
   ```

### Running the Game

**With Real Hardware:**
```bash
python pc_controller/main.py
```

**With Mock Hardware (for testing):**
```bash
# Set simulation flags in config.yaml to true
python pc_controller/main.py
```

**Automated Test (mocks):**
```bash
python simulation/test_game_flow.py
```

## How to Play

1. System initializes and robot moves to home position
2. Robot gives yellow puck to player at pickup location
3. Player drops puck in any column (detected by LED strip sensor)
4. PC calculates best move and robot executes (picks red puck, drops in column)
5. Robot returns and gives next yellow puck to player
6. Repeat until someone wins or board is full
7. System displays winner via LED pattern and resets for new game

## Development

### Testing Without Hardware

The simulation layer allows full game testing without physical components:

```python
# config.yaml
simulation:
  robot: true
  arduino: true
```

Run game with mocks:
```bash
python pc_controller/main.py
```

Manually trigger events for testing:
```python
from hardware.mock import MockArduino
arduino = MockArduino()
arduino.simulate_player_drop(3)  # Simulate puck drop in column 3
```

### Adding Features

**To modify AI behavior:**
- Edit `core/ai.py` - adjust evaluation function or search depth

**To change LED patterns:**
- Edit `arduino_controller/arduino_main/led_control.cpp`

**To add new robot positions:**
- Run `python robot_arm/calibrate_robot.py` again

**To modify serial protocol:**
- Update `docs/serial_protocol.md`
- Update `hardware/arduino.py` (PC side)
- Update `arduino_controller/arduino_main.ino` (Arduino side)

### Logging

All components log to both console and `game.log`:

```python
from utils.logger import setup_logger
logger = setup_logger('game')

logger.info("Player dropped puck at column 3")
logger.debug("Board state: ...")
logger.error("Robot movement failed!")
```

View logs:
```bash
tail -f game.log
```

## Troubleshooting

**Robot not connecting:**
- Check USB cable and port in `config.yaml`
- Verify pymycobot version: `pip show pymycobot` (should be 3.6.3)
- Test connection: `python -c "from pymycobot import MyCobot280; mc = MyCobot280('/dev/ttyUSB0', 115200); print(mc.is_controller_connected())"`

**Arduino not responding:**
- Check USB cable and port in `config.yaml`
- Open Arduino Serial Monitor and send test commands manually
- Verify baud rate matches (9600)

**Drop detection not working:**
- Check sensor wiring to Arduino analog pins
- Test sensors with `arduino_controller/test_sketches/test_sensors.ino`
- Adjust debounce timing in `sensor_handler.cpp`

**Robot position drift:**
- Re-run calibration: `python robot_arm/calibrate_robot.py`
- Check vacuum gripper is holding pucks firmly
- Verify arm movements complete before next command

**AI too slow/too fast:**
- Adjust `ai_depth` in `config.yaml` (lower = faster, higher = smarter)
- Typical range: 3-6 (4 is balanced)

## Serial Protocol

### PC → Arduino Commands

```
RELEASE:<col>           # Release puck in column 0-6
LED:<col>:<R,G,B>       # Set LED color for column
LED_ALL:<R,G,B>         # Set all LEDs to color
LED_PATTERN:<pattern>   # Predefined pattern (WIN, LOSE, READY)
STATUS                  # Request sensor states
RESET                   # Reset game
```

### Arduino → PC Responses

```
DROP:<col>              # Puck detected in column
READY                   # Command executed
ERROR:<code>:<msg>      # Error occurred
STATUS:<0101010>        # 7-bit sensor states
```

See `docs/serial_protocol.md` for complete specification.

## Architecture Decisions

### Why Event-Driven (not State Machine)?

- **Physical safety**: Robot gives puck to player, so timing conflicts impossible
- **Simplicity**: Linear flow is easier to understand and debug
- **Flexibility**: Can add phase variable later if needed for logging/debugging

### Why Separate Controllers?

- **Specialization**: PC for compute-heavy AI, Arduino for real-time I/O, robot for movement
- **Modularity**: Each can be tested/replaced independently
- **Scalability**: Can upgrade PC without touching Arduino firmware

### Why Mock Layer?

- **Development**: Work on game logic without hardware
- **Testing**: Automated tests in CI/CD pipeline
- **Portability**: Develop on laptop, deploy to lab machine

## Contributing

1. Create issue describing feature/bug
2. Create branch: `git checkout -b feature/description`
3. Make changes with tests
4. Run tests: `python -m pytest tests/`
5. Create pull request

## License

[Add your license here]

## Credits

- Original codebase: [Shumzi/Connect-4-Elephant-Robotics](https://github.com/Shumzi/Connect-4-Elephant-Robotics)
- Robot arm: Elephant Robotics MyCobot 280
- AI algorithm: Minimax with alpha-beta pruning

## Contact

[Add contact information]

---

**Project Status:** 🚧 In Development

See [Project Milestones](docs/milestones.md) for current progress.
