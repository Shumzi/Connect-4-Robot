#include <SPI.h>
#include <stdint.h>

const int load_pin = 3;     //165 - read
const int latch_pin = 4;    //595 - write
const int btn_pin = 5;      //The start button
const int btn_ms_time = 1;  //Time for button to register a press
const int pump_pin = 7;
const int valve_pin = 6;

byte solenoid_state = 0;

// Timing variables
unsigned long pumpStartTime = 0;
const unsigned long pumpTimeout = 30000UL;  // 30 seconds in ms
bool pumpRunning = false;

//binary protocol cmd section prefixes
typedef enum {
  PUMP_CMD = 0b1,
  DISC_CMD = 0b10,
  BTN_CMD = 0b11,
  SOLENOID_CMD = 0b100
} CMDS;


void setup() {
  Serial.begin(115200);
  pinMode(latch_pin, OUTPUT);
  pinMode(load_pin, OUTPUT);
  pinMode(btn_pin, INPUT);

  digitalWrite(pump_pin, HIGH);  // OFF (active-low)
  digitalWrite(valve_pin, LOW);  // exhaust OPEN

  digitalWrite(pump_pin, LOW);
  digitalWrite(valve_pin, LOW);

  digitalWrite(load_pin, HIGH);
  digitalWrite(latch_pin, HIGH);


  SPI.begin();
  SPI.beginTransaction(SPISettings(1000000, MSBFIRST, SPI_MODE0));

  writeToSr(solenoid_state);
}
void loop() {
  handleDiscDetection();
  handleButtonPress();
  handlePump();
  if (Serial.available()) {
    handle_cmd(Serial.read());
  }
  delay(1);
}
void handlePump() {
  if (pumpRunning && (millis() - pumpStartTime >= pumpTimeout)) {
    shutOffPump();

    // //Transmit that the pump has been turned off
    // byte msg = build_message_byte(PUMP_CMD, 0, 0);
    // Serial.write(msg);


  }
}
void turnOnPump() {
  digitalWrite(pump_pin, LOW);
  digitalWrite(valve_pin, HIGH);
  pumpStartTime = millis();
  pumpRunning = true;
}

void shutOffPump() {
  digitalWrite(pump_pin, HIGH);
  digitalWrite(valve_pin, LOW);
  pumpRunning = false;
}
void update165() {
  // Latch the inputs into the shift register
  digitalWrite(load_pin, LOW);
  delayMicroseconds(5);
  digitalWrite(load_pin, HIGH);
  delayMicroseconds(5);
}

void handleDiscDetection() {
  static byte last_data = 0;

  update165();
  byte data = SPI.transfer(solenoid_state);

  //we have a rising edge
  if (data != 0 && last_data == 0) {
    byte msg = build_message_byte(DISC_CMD, bit_index(data), 0);
    Serial.write(msg);
  }

  last_data = data;
}

//cmd - What are we sending? (3 bits)
//val - Value we send (4 bits)
//is_ack - Are we answering or initiating (1 bit)
uint8_t build_message_byte(CMDS cmd, byte val, byte is_ack) {
  byte msg = 0;
  msg |= (is_ack & 0b1) << 7;
  msg |= (cmd & 0b111) << 4;
  msg |= (val & 0b1111);
  return msg;
}

int bit_index(byte x) {
  // int i = 0;
  // while (x >>= 1) i++;
  // return i;

  //Like the code above, but apparently native, counts trailing zeros
  return __builtin_ctz(x);
}




void handleButtonPress() {
  static int prevPressed = LOW;
  static unsigned long pressStart = 0;

  int pressed = digitalRead(btn_pin);

  if (pressed != prevPressed) {
    prevPressed = pressed;

    if (pressed == HIGH) {
      pressStart = millis();
    } else if (millis() - pressStart >= btn_ms_time) {
      byte msg = build_message_byte(BTN_CMD, 1, 0);
      Serial.write(msg);
    }
  }
}

void ack(byte msg) {
  Serial.write(msg | (0b1 << 7));
}
void handle_cmd(byte msg) {
  CMDS cmd = (msg >> 4) & 0b111;
  int val = msg & 0b1111;
  int success = 0;
  switch (cmd) {
    case SOLENOID_CMD:
      if (val < 0 || val > 7) break;

      if (val == 0) {
        solenoid_state = 0;
        writeToSr(0);
      } else {
        writeToSr(1 << (val - 1));
        solenoid_state = 1 << (val - 1);
      }
      success = 1;
      break;
    case PUMP_CMD:
      if (val == 1) {
        turnOnPump();
      } else if (val ==  0) {
        shutOffPump();
      }
      break;
  }
  if (success == 1)
    ack(msg);
}


void writeToSr(byte data) {
  digitalWrite(latch_pin, LOW);
  SPI.transfer(data);             // Send output byte
  digitalWrite(latch_pin, HIGH);  // Latch output
}
