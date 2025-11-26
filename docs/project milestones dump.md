**Connect 4 Robot - Project Milestones & Issues**

**Milestone 1: Project Setup & Code Extraction**

**Goal:** Set up clean project structure and extract reusable code from old repo  
**Duration:** 3-5 days  
**Dependencies:** None

**Issues**

Issue 1.1: Create Project Structure

- \[ \] Create all directories as per architecture design
- \[ \] Initialize git repository
- \[ \] Create .gitignore for Python projects
- \[ \] Add [README.md](http://README.md) with project overview

**Deliverable:** Empty but organized folder structure

Issue 1.2: Extract Game Logic from Old Repo

- \[ \] Copy board.py logic (board state representation, move validation)
- \[ \] Copy ai.py logic (minimax algorithm, evaluation function)
- \[ \] Remove all camera/CV dependencies from extracted code
- \[ \] Test extracted board logic in isolation (unit tests)
- \[ \] Test extracted AI logic with sample board states

**Deliverable:** Working core/board.py and core/ai.py with unit tests

Issue 1.3: Copy Legacy Robot Code

- \[ \] Copy ArmInterface.py to legacy/ folder
- \[ \] Document what pymycobot version it uses
- \[ \] Test connection to robot arm with legacy code
- \[ \] Document any issues or quirks discovered

**Deliverable:** Working legacy robot code as reference

Issue 1.4: Create requirements.txt and config.yaml

- \[ \] Pin pymycobot version (3.6.3 or working version)
- \[ \] Add pyserial, pyyaml dependencies
- \[ \] Create config.yaml with hardware ports and simulation flags
- \[ \] Document how to edit config for different setups

**Deliverable:** Installable dependencies and configuration template

**Milestone 2: Mock Hardware & Simulation Layer**

**Goal:** Build simulation layer to enable development without hardware  
**Duration:** 2-3 days  
**Dependencies:** Milestone 1 complete

**Issues**

Issue 2.1: Implement Mock Arduino

- \[ \] Create hw/mock.py with MockArduino class
- \[ \] Implement connect(), send_command(), register_callback()
- \[ \] Add simulate_player_drop(column) method for manual testing
- \[ \] Test callback mechanism works correctly

**Deliverable:** Functioning MockArduino that simulates serial communication

Issue 2.2: Implement Mock Robot

- \[ \] Create MockRobot class in hw/mock.py
- \[ \] Implement connect(), place_puck_at_column(), give_player_puck()
- \[ \] Add time delays to simulate real movement duration
- \[ \] Add print statements for visibility during testing

**Deliverable:** Functioning MockRobot that simulates arm movements

Issue 2.3: Create Test Game Flow Script

- \[ \] Create simulation/test_game_flow.py
- \[ \] Script initializes game with mock hardware
- \[ \] Script simulates full game (player moves, robot responses)
- \[ \] Verify win detection works correctly
- \[ \] Verify game reset works

**Deliverable:** Automated test demonstrating full game flow with mocks

**Milestone 3: PC Controller Core Logic**

**Goal:** Implement main game orchestration and logic  
**Duration:** 4-6 days  
**Dependencies:** Milestone 2 complete

**Issues**

Issue 3.1: Implement Board Class

- \[ \] Create core/board.py with Board class
- \[ \] Implement drop_piece(column, player) method
- \[ \] Implement is_valid_move(column) method
- \[ \] Implement check_win(player) method (all 4 directions)
- \[ \] Implement is_draw() method
- \[ \] Implement get_state() method for AI
- \[ \] Write unit tests for all methods

**Deliverable:** Fully tested Board class

Issue 3.2: Implement AI Engine

- \[ \] Create core/ai.py with AIEngine class
- \[ \] Implement get_best_move(state, player) using minimax
- \[ \] Add alpha-beta pruning for performance
- \[ \] Make AI depth configurable
- \[ \] Test AI makes reasonable moves
- \[ \] Test AI detects winning moves
- \[ \] Test AI blocks opponent winning moves

**Deliverable:** Functioning AI that plays competently

Issue 3.3: Implement Game Controller

- \[ \] Create game.py with Connect4Game class
- \[ \] Implement \__init__ (takes robot, arduino, config)
- \[ \] Implement start() method (initialize hardware, reset board)
- \[ \] Implement on_player_drop(column) callback
- \[ \] Implement robot turn sequence (calculate move, execute, update board)
- \[ \] Implement win/draw detection and game over handling
- \[ \] Add optional phase variable for debugging/logging
- \[ \] Test with mock hardware

**Deliverable:** Complete game orchestration logic tested with mocks

Issue 3.4: Implement Main Entry Point

- \[ \] Create main.py
- [ ] create config.yaml for entry + robot etc.
- \[ \] Load configuration from config.yaml
- \[ \] Create hardware objects based on simulation flags
- \[ \] Wire up callbacks between arduino and game
- \[ \] Start game loop
- \[ \] Handle graceful shutdown (Ctrl+C)

**Deliverable:** Runnable [main.py](http://main.py) that plays full game with mocks

Issue 3.5: Add Logging System

- \[ \] Create utils/logger.py with setup function
- \[ \] Add logging to [game.py](http://game.py) (player moves, robot moves, wins)
- \[ \] Add logging to [board.py](http://board.py) (state changes)
- \[ \] Add logging to hardware interfaces (commands sent/received)
- \[ \] Test log file is created and populated correctly

**Deliverable:** Comprehensive logging for debugging

**Milestone 4: Arduino Interface**

**Goal:** Implement PC-side Arduino communication  
**Duration:** 3-4 days  
**Dependencies:** Milestone 3 complete

**Issues**

Issue 4.1: Define Serial Protocol

- \[ \] Document command format (PC → Arduino)
- \[ \] Document response format (Arduino → PC)
- \[ \] Document error codes
- \[ \] Create docs/serial_protocol.md

**Deliverable:** Complete protocol specification document

Issue 4.2: Implement Arduino Interface

- \[ \] Create hw/arduino.py with ArduinoInterface class
- \[ \] Implement serial connection management
- \[ \] Implement command sending (release_puck, set_led, reset_game)
- \[ \] Implement background listener thread
- \[ \] Implement message parsing and callback triggering
- \[ \] Add connection health check (ping/pong)
- \[ \] Add error handling for disconnection

**Deliverable:** Working ArduinoInterface that communicates over serial

Issue 4.3: Test Arduino Interface with Mock Serial

- \[ \] Create mock serial port for testing
- \[ \] Test all command types are sent correctly
- \[ \] Test callbacks fire when messages received
- \[ \] Test error handling (invalid messages, disconnection)

**Deliverable:** Tested [arduino.py](http://arduino.py) without real hardware

**Milestone 5: Robot Interface**

**Goal:** Wrap legacy robot code and implement movement sequences  
**Duration:** 3-4 days  
**Dependencies:** Milestone 3 complete

**Issues**

Issue 5.1: Wrap Legacy Robot Code

- \[ \] Create hw/robot.py with RobotController class
- \[ \] Wrap legacy ArmInterface in clean API
- \[ \] Implement connect() method
- \[ \] Implement place_puck_at_column(column) method
- \[ \] Implement give_player_puck() method
- \[ \] Implement move_to_home() method
- \[ \] Add error handling for movement failures

**Deliverable:** Clean robot interface wrapping legacy code

Issue 5.2: Create Calibration Script

- \[ \] Create scripts/calibrate_robot.py
- \[ \] Interactive prompts to move arm to each position
- \[ \] Save positions to robot_arm/positions.json
- \[ \] Test loading positions from JSON
- \[ \] Document calibration procedure

**Deliverable:** Calibration tool and saved positions file

Issue 5.3: Test Robot Movements

- \[ \] Test connection to real robot arm
- \[ \] Test pick puck from red holder
- \[ \] Test drop puck at each column (0-6)
- \[ \] Test give puck to player
- \[ \] Test return to home position
- \[ \] Verify vacuum on/off works correctly

**Deliverable:** Verified robot movements with real hardware

**Milestone 6: Arduino Firmware**

**Goal:** Implement Arduino controller firmware  
**Duration:** 4-5 days  
**Dependencies:** Milestone 4 complete (protocol defined)

**Issues**

Issue 6.1: Get PCB Pin Mappings

- \[ \] Contact PCB designer for exact pin assignments
- \[ \] Document pins for LED strip, solenoids, sensors
- \[ \] Create arduino_controller/config.h with pin definitions

**Deliverable:** Documented pin mappings

Issue 6.2: Implement Arduino Main Sketch

- \[ \] Create arduino_main.ino with main loop
- \[ \] Implement serial command parser
- \[ \] Implement command handler (dispatch to correct function)
- \[ \] Test serial communication with PC

**Deliverable:** Basic Arduino sketch with serial communication

Issue 6.3: Implement LED Control

- \[ \] Create led_control.h/cpp
- \[ \] Initialize LED strip (FastLED or Adafruit_NeoPixel)
- \[ \] Implement set column color function
- \[ \] Implement predefined patterns (READY, WIN, LOSE)
- \[ \] Test LED commands from PC

**Deliverable:** Working LED control via serial commands

Issue 6.4: Implement Solenoid Control

- \[ \] Create solenoid_control.h/cpp
- \[ \] Initialize solenoid pins (via relay/MOSFET drivers)
- \[ \] Implement release puck function with timed pulse
- \[ \] Add safety checks (prevent multiple simultaneous releases)
- \[ \] Test solenoid commands from PC

**Deliverable:** Working solenoid control via serial commands

Issue 6.5: Implement Sensor Reading

- \[ \] Create sensor_handler.h/cpp
- \[ \] Initialize sensor pins (photoresistors)
- \[ \] Implement debounced sensor reading
- \[ \] Send DROP event to PC when puck detected
- \[ \] Test sensor detection with physical pucks

**Deliverable:** Working drop detection with event reporting

Issue 6.6: Integrate and Test Arduino Firmware

- \[ \] Test all components together
- \[ \] Test reset game command
- \[ \] Test full game sequence (LEDs, solenoids, sensors)
- \[ \] Fix any timing or synchronization issues

**Deliverable:** Complete working Arduino firmware

**Milestone 7: Integration & Testing**

**Goal:** Integrate all components and test full system  
**Duration:** 3-4 days  
**Dependencies:** Milestones 5 & 6 complete

**Issues**

Issue 7.1: Test PC ↔ Arduino Communication

- \[ \] Connect Arduino to PC via USB
- \[ \] Test all command types work
- \[ \] Test Arduino events reach PC correctly
- \[ \] Test error handling (unplug/replug)
- \[ \] Verify no message loss or corruption

**Deliverable:** Verified bidirectional communication

Issue 7.2: Test PC ↔ Robot Communication

- \[ \] Connect robot to PC via USB
- \[ \] Test all movement commands work
- \[ \] Test position accuracy
- \[ \] Test error recovery (if movement fails)
- \[ \] Verify vacuum control works reliably

**Deliverable:** Verified robot control from PC

Issue 7.3: Integration Test - Single Turn

- \[ \] Place puck in player position
- \[ \] Player drops puck
- \[ \] Verify Arduino detects drop
- \[ \] Verify PC receives event
- \[ \] Verify board updates correctly
- \[ \] Verify AI calculates move
- \[ \] Verify robot executes move correctly
- \[ \] Verify robot gives next puck to player

**Deliverable:** One complete turn working end-to-end

Issue 7.4: Integration Test - Full Game

- \[ \] Play complete game to win condition
- \[ \] Verify win detection works
- \[ \] Verify LED patterns display correctly
- \[ \] Verify game can reset and replay
- \[ \] Test edge cases (column full, board full draw)

**Deliverable:** Full game playable from start to finish

Issue 7.5: Performance & Reliability Testing

- \[ \] Play 10+ games and track failures
- \[ \] Measure average turn time (player wait)
- \[ \] Test recovery from common errors
- \[ \] Fix any reliability issues discovered
- \[ \] Document known limitations

**Deliverable:** Stable, reliable system

Milestone 8: Polish & Documentation

**Goal:** Final polish, documentation, and deployment  
**Duration:** 2-3 days  
**Dependencies:** Milestone 7 complete

**Issues**

Issue 8.1: Update Documentation

- \[ \] Update [README.md](http://README.md) with setup instructions + troubleshooting
- \[ \] Create docs/setup_guide.md for first-time setup
- \[ \] Document calibration procedure
- \[ \] Document troubleshooting common issues
- \[ \] Add wiring diagrams or photos

**Deliverable:** Complete user documentation

Issue 8.2: Code Cleanup

- \[ \] Remove debug print statements
- \[ \] Add docstrings to all classes/methods
- \[ \] Run code formatter (black/autopep8)
- \[ \] Remove unused imports
- \[ \] Add type hints where helpful

**Deliverable:** Clean, professional codebase

Issue 8.3: Create Demo Video

- \[ \] Record full game playthrough
- \[ \] Show robot movements
- \[ \] Show Arduino LED feedback
- \[ \] Show PC terminal output
- \[ \] Edit into short demo video

**Deliverable:** Demo video for presentation

Issue 8.4: Final Testing & Handoff

- \[ \] Test complete setup from scratch (fresh install)
- \[ \] Verify all documentation is accurate
- \[ \] Create deployment checklist
- \[ \] Train others on system operation

**Deliverable:** Production-ready system

**Summary Timeline**

| Milestone | Duration | Cumulative |
| --- | --- | --- |
| M1: Setup & Extraction | 3-5 days | 5 days |
| M2: Mock Layer | 2-3 days | 8 days |
| M3: PC Core Logic | 4-6 days | 14 days |
| M4: Arduino Interface | 3-4 days | 18 days |
| M5: Robot Interface | 3-4 days | 22 days |
| M6: Arduino Firmware | 4-5 days | 27 days |
| M7: Integration & Testing | 3-4 days | 31 days |
| M8: Polish & Documentation | 2-3 days | **~34 days** |

**Total estimated time: 5-7 weeks** (assuming full-time work)

**Critical Path**

M1 (Setup) → M2 (Mocks) → M3 (PC Logic) → M7 (Integration)  
↓  
M4 (Arduino PC) → M6 (Arduino FW) → M7  
↓  
M5 (Robot) → M7

**Parallel work opportunities:**

- M4, M5 can be done in parallel after M3
- M6 can start once M4 protocol is defined
- M8 can overlap with M7

**Risk Mitigation**

**High Risk Items:**

- **Arduino firmware bugs** - Mitigated by early mock testing
- **Robot calibration drift** - Mitigated by calibration script
- **Serial communication reliability** - Mitigated by error handling
- **Hardware availability** - Mitigated by simulation layer

**Recommended approach:**

- Build simulation layer FIRST (M2) before hardware
- Test each component in isolation before integration
- Keep legacy code as fallback
- Log everything for debugging
