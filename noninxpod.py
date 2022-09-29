import serial

def stringAsHex(s):
    return ":".join("{:02x}".format(c) for c in s)

def readFrame():
    while True:
        b1 = sensor.read()
        if len(b1) > 0:
            if int(stringAsHex(b1), 16) == 0b1:
                b2 = sensor.read()
                b3 = sensor.read()
                b4 = sensor.read()
                b5 = sensor.read()
                #print "Byte: ", stringAsHex(b1), stringAsHex(b2), stringAsHex(b3), stringAsHex(b4), stringAsHex(b5)
                return [b1, b2, b3, b4, b5]
                break

# This function will keep running until the frame is valid, by checking the OUT OF TRACK bit.
def readValidFrameSet():
    sensor.reset_input_buffer()
    while True:
        frame1 = readFrame()
        if int(stringAsHex(frame1[1]), 16) & 0b1:
            #print("first frame!")
            frame2 = readFrame()
            frame3 = readFrame()
            # We only care about frame 1 to 3 so far
            hr1 = ((int(stringAsHex(frame1[3]), 16) & 0b11) << 7)
            hr2 = (int(stringAsHex(frame2[3]), 16) & 0b1111111)
            hr = hr1 + hr2
            spo = int(stringAsHex(frame3[3]), 16) & 0b1111111
            #print "HR=", hr, " SPO2=", spo
            if ((int(stringAsHex(frame1[1]), 16) & 0b10000 == 0) & (spo != 0 & hr < 300)):
                # Out of track bit is not set, frame is valid
                #print stringAsHex(frame1[3])
                #print stringAsHex(frame2[3])
                #print stringAsHex(frame3[3])
                sensor.reset_input_buffer()
                return [hr, spo]
            #else:
                # Out of track bit is set, frame is invalid
                #print("OUT OF TRACK")

# should default to 9600, 8 data bits, 1 stop bit, but feel free to use the constructor arguments to configure it
sensor = serial.Serial('/dev/ttyUSB0', timeout=1)
sensor.flushInput()
while True:
    # Run this once if you only want 1 set values. result[0]=heart rate (in BPM), result[1]= spo2%
    result = readValidFrameSet()
    print("HR=", result[0], " SPO2=", result[1])
