#define DEBUG 0

int latchPin = 8; //ST_CP
int clockPin = 12; // SH_CP
int dataPin = 11; // DS

long pm[8][8][2] = {
	{{0x2fe, 0x1fe}, {0x8fe, 0x4fe}, {0x20fe, 0x10fe}, {0x80fe, 0x40fe}, {0x200fe, 0x100fe}, {0x800fe, 0x400fe}, {0x2000fe, 0x1000fe}, {0x8000fe, 0x4000fe}}, 
	{{0x2fd, 0x1fd}, {0x8fd, 0x4fd}, {0x20fd, 0x10fd}, {0x80fd, 0x40fd}, {0x200fd, 0x100fd}, {0x800fd, 0x400fd}, {0x2000fd, 0x1000fd}, {0x8000fd, 0x4000fd}}, 
	{{0x2fb, 0x1fb}, {0x8fb, 0x4fb}, {0x20fb, 0x10fb}, {0x80fb, 0x40fb}, {0x200fb, 0x100fb}, {0x800fb, 0x400fb}, {0x2000fb, 0x1000fb}, {0x8000fb, 0x4000fb}}, 
	{{0x2f7, 0x1f7}, {0x8f7, 0x4f7}, {0x20f7, 0x10f7}, {0x80f7, 0x40f7}, {0x200f7, 0x100f7}, {0x800f7, 0x400f7}, {0x2000f7, 0x1000f7}, {0x8000f7, 0x4000f7}}, 
	{{0x2ef, 0x1ef}, {0x8ef, 0x4ef}, {0x20ef, 0x10ef}, {0x80ef, 0x40ef}, {0x200ef, 0x100ef}, {0x800ef, 0x400ef}, {0x2000ef, 0x1000ef}, {0x8000ef, 0x4000ef}}, 
	{{0x2df, 0x1df}, {0x8df, 0x4df}, {0x20df, 0x10df}, {0x80df, 0x40df}, {0x200df, 0x100df}, {0x800df, 0x400df}, {0x2000df, 0x1000df}, {0x8000df, 0x4000df}}, 
	{{0x2bf, 0x1bf}, {0x8bf, 0x4bf}, {0x20bf, 0x10bf}, {0x80bf, 0x40bf}, {0x200bf, 0x100bf}, {0x800bf, 0x400bf}, {0x2000bf, 0x1000bf}, {0x8000bf, 0x4000bf}}, 
	{{0x27f, 0x17f}, {0x87f, 0x47f}, {0x207f, 0x107f}, {0x807f, 0x407f}, {0x2007f, 0x1007f}, {0x8007f, 0x4007f}, {0x20007f, 0x10007f}, {0x80007f, 0x40007f}}
};

long frame[129];
boolean wait = true;
byte buffer[128];
byte lastbytes[3];
byte _cursor = 0;


void setup() {
  pinMode(latchPin, OUTPUT);
  pinMode(clockPin, OUTPUT);
  pinMode(dataPin, OUTPUT);
  Serial.begin(9600);
  for (int i=0; i < 129; i++)
    frame[i] = 0x0000;
}

/*
  Each byte has data for 2 pixels.
  8x8 led = 64/2 = 32

  4bit codes:
  //0x04 off
  //0x01 red
  //0x02 green
  //0x03 orange
*/
void load_bytes(byte* bytes) {
  int pixel = 0;
  int on_pixels = 0;

  for (int i=0; i<32; i++) {
    byte b0 = (bytes[i] >> 4);
    byte b1 = (bytes[i]) & 0x0F;
    if (b0 != 0x04)
      on_pixels++;

    if (b0 == 0x01)
      frame[on_pixels-1] = pm[pixel/8][pixel%8][0];
    else if (b0 == 0x02)
      frame[on_pixels-1] = pm[pixel/8][pixel%8][1];
    else if (b0 == 0x03) {
      frame[on_pixels-1] = pm[pixel/8][pixel%8][0];
      on_pixels++;
      frame[on_pixels-1] = pm[pixel/8][pixel%8][1];
    }

    pixel += 1;    
    if (b1 != 0x04)
      on_pixels++;

    if (b1 == 0x01)
      frame[on_pixels-1] = pm[pixel/8][pixel%8][0];
    else if (b1 == 0x02)
      frame[on_pixels-1] = pm[pixel/8][pixel%8][1];
    else if (b1 == 0x03) {
      frame[on_pixels-1] = pm[pixel/8][pixel%8][0];
      on_pixels++;
      frame[on_pixels-1] = pm[pixel/8][pixel%8][1];
    }
    pixel += 1;
  }

  frame[on_pixels] = 0x0000;
}

void frame_received(byte* bytes, int len, boolean last) {
  if (DEBUG) {
    Serial.print("frame received len: ");
    Serial.println(len, DEC);
  }
  Serial.write(len); 
  if (len != 32)
    return;
  load_bytes(bytes);
}

void iterate_read() {
   while (Serial.available() > 0) { 
    buffer[_cursor] = Serial.read();
    lastbytes[0] = lastbytes[1];
    lastbytes[1] = lastbytes[2];
    lastbytes[2] = buffer[_cursor];
    if (DEBUG) {
      Serial.print("byte received: ");
      Serial.print(buffer[_cursor], HEX);
      Serial.print(" _cursor: ");
      Serial.print(_cursor, DEC);
      Serial.print(" lastbytes: ");
      Serial.print(lastbytes[0], HEX);
      Serial.print(" ");
      Serial.print(lastbytes[1], HEX);
      Serial.print(" ");
      Serial.print(lastbytes[2], HEX);
      Serial.println(" ");
    }

    if (_cursor > 1 && lastbytes[0] == 0xFF && 
      lastbytes[1] == 0xFF && lastbytes[2] == 0xFF) {
      if (!wait) {
        lastbytes[0] = 0x00;
        lastbytes[1] = 0x00;
        lastbytes[2] = 0x00;
        frame_received(buffer, _cursor-2, true);
      }
      _cursor = 0;
      wait = !wait;
      return;
    }

    if (_cursor >= 127) {
      frame_received(buffer, _cursor+1, false);
      _cursor = 0;
    }
    else
      _cursor++;
  }
}

void loop() {  
  iterate_read();
  int i=0;
    while (1) {
      long addr = frame[i];
      digitalWrite(latchPin, 0);
      shiftOut(dataPin, clockPin, MSBFIRST, addr >> 16);
      shiftOut(dataPin, clockPin, MSBFIRST, addr >> 8);
      shiftOut(dataPin, clockPin, MSBFIRST, addr);
      digitalWrite(latchPin, 1);
      i++;

      if (addr == 0x0000) {
          delay(1);
          break;
      }
    }
}
