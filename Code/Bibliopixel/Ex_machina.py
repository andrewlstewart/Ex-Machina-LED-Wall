import os
import random

import bibliopixel
# causes frame timing information to be output
bibliopixel.log.setLogLevel(bibliopixel.log.DEBUG)

# Load driver for the AllPixel
from bibliopixel.drivers.serial import *
# set number of pixels & LED type here
driverLeft = Serial(num=194, ledtype=LEDTYPE.LPD8806,
                    device_id=1, spi_speed=1)
driverRight = Serial(num=194, ledtype=LEDTYPE.LPD8806,
                     device_id=2, spi_speed=1)

# load the LEDStrip class
from bibliopixel.layout import *
led = Strip([driverLeft, driverRight], brightness=4)

from bibliopixel.animation import BaseStripAnim
from bibliopixel.colors import color_scale

from Frames import FramesCol, individualCol
from Packets import Packets


class StripTest(BaseStripAnim):
    def __init__(self, layout, start=0, end=-1):
        # The base class MUST be initialized by calling super like this
        super(StripTest, self).__init__(layout, start, end)

        # 0 -> Solid colors, 1 -> Red diagonal, 2 -> Red/blue chase # Ex Machine
        # 3 -> Rain
        self._pattern = "Rain"
        # Create a color array to use in the animation
        # Solid colors
        self._solidColors = ((19, 158, 243),  # 'Dark blue'
                             (141, 243, 255),  # 'Light light blue'
                             (13, 141, 234),  # 'Medium dark blue'
                             (94, 96, 206),  # 'Light purple'
                             )

        self._redDiagonalColors = (165, 2, 4)  # Red

        self._redBlueChaseColors = ((142, 120, 195),  # Purple transition
                                    (19, 158, 243),  # Blue
                                    (165, 2, 4))  # Red

        self._redDiagonalCol = []
        self._redDiagonalCol.append([])  # Col 0
        self._redDiagonalCol.append([])  # Col 1
        self._redDiagonalCol.append([])  # Col 2
        self._redDiagonalCol.append([])  # Col 3
        self._redDiagonalCol.append([])  # Col 4
        self._redDiagonalCol.append([])  # Col 5
        self._redDiagonalCol.append([])  # Col 6
        self._redDiagonalCol.append([])  # Col 7
        self._redDiagonalCol.append([])  # Col 8
        self._redDiagonalCol.append([])  # Col 9
        self._redDiagonalCol.append([])  # Col 10

        self._rainTiming = 0
        self._rainColor = (255, 255, 255)
        self._rainCols = [[], [], [], [], [], [], [], [], [], []]

        self.internal_delay = 0.1

    def step(self, amt=1):
        # Fill the strip, with each sucessive color

        if not self._step % 10:
            if os.path.isfile(r'/home/pi/LED_Wall/test_01/state/Rain'):
                if self._pattern != "Rain":
                    self._step = 0
                    self._pattern = "Rain"
            if os.path.isfile(r'/home/pi/LED_Wall/test_01/state/Ex_Machina'):
                if not self._pattern in ('Ex_Flashing', 'Ex_Diagonal', 'Ex_Chase'):
                    self._step = 0
                    self._pattern = 'Ex_Flashing'
            if os.path.isfile(r'/home/pi/LED_Wall/test_01/state/off'):
                if self._pattern != "off":
                    self._step = 0
                    self._pattern = 'off'

        if self._pattern == 'Ex_Flashing':
            if self._step < 2:
                self.layout.all_off()  # Clear any previous patterns on first draw

            self.layout.fill(self._solidColors[(int(self._step / 5.)) % 4], start=0, end=-1)

            if self._step >= int(15. / self.internal_delay):  # About 15 seconds
                self._step = 0
                self._pattern = 'Ex_Diagonal'

        #
        # Draw the diagonal red parts
        #
        if self._pattern == 'Ex_Diagonal':
            if self._step < 2:
                self.layout.all_off()  # Clear any previous pattern on first draw

            self.redDiagonal()

            if self._step >= int(15. / self.internal_delay):  # About 15 seconds
                self._step = 0
                self._pattern = 'Ex_Chase'

        #
        # Draw the up/down chasing red/blue sequence
        #
        if self._pattern == 'Ex_Chase':
            if self._step < 2:
                self.layout.all_off()  # Clear any previous pattern on first draw

            self.redBlueChase()

            if self._step >= int(8. / self.internal_delay):  # About 8 seconds
                self._step = 0
                self._pattern = 'Ex_Flashing'

        #
        # Draw the rain failing randomly sequence
        #
        if self._pattern == "Rain":
            if self._step < 2:
                self.layout.all_off()  # Clear any previous pattern on first draw

            self.rain()

        #
        # Draw off until the pi shuts down
        #
        if self._pattern == "off":
            self.layout.all_off()  # Clear any previous pattern on first draw

        # Increment the internal step by the given amount
        self._step += amt

    def redBlueChase(self):
        addressed = {}

        for packet_idx in range(len(Packets)):
            if (packet_idx < 2) or (9 < packet_idx < 12):
                for point in Packets[(packet_idx + self._step) % 22]:
                    self.layout.set(point, self._redBlueChaseColors[0])
                    addressed[point] = True
            elif 2 <= packet_idx <= 9:
                for point in Packets[(packet_idx + self._step) % 22]:
                    if point in addressed:
                        continue
                    self.layout.set(point, self._redBlueChaseColors[1])
                    addressed[point] = True
            else:
                for point in Packets[(packet_idx + self._step) % 22]:
                    if point in addressed:
                        continue
                    self.layout.set(point, self._redBlueChaseColors[2])

    def redDiagonal(self):
        step = round(self._step / 1.) % 14

        if step == 0:  # Frame 49
            # Off
            self._redDiagonalCol[0] = [False, False, True]
            self._redDiagonalCol[1] = [False, True]
            self._redDiagonalCol[2] = [False, True, False]
            self._redDiagonalCol[3] = [False, True]
            self._redDiagonalCol[4] = [False, True, False]
            self._redDiagonalCol[5] = [True, False]
            self._redDiagonalCol[6] = [False, True, False]
            self._redDiagonalCol[7] = [True, False]
            self._redDiagonalCol[8] = [True, False, False]
            self._redDiagonalCol[9] = [True, False]
            self._redDiagonalCol[10] = [True, False, True]

            self._displayRed()
        elif step == 1:  # Frame 50
            # On
            self._redDiagonalCol[0] = [True, False, True]
            #self._redDiagonalCol[1] = [False, True]
            self._redDiagonalCol[2] = [False, True, True]
            # self._redDiagonalCol[3] = [False, True]
            # self._redDiagonalCol[4] = [False, True, False]
            self._redDiagonalCol[5] = [True, True]
            # self._redDiagonalCol[6] = [False, True, False]
            # self._redDiagonalCol[7] = [True, False]
            self._redDiagonalCol[8] = [True, True, False]
            # self._redDiagonalCol[9] = [True, False]
            # self._redDiagonalCol[10] = [True, False, True]

            self._displayRed()
        elif step == 2:  # Frame 51
            # Off
            # self._redDiagonalCol[0] = [True, False, True]
            #self._redDiagonalCol[1] = [False, True]
            self._redDiagonalCol[2] = [False, False, True]
            # self._redDiagonalCol[3] = [False, True]
            # self._redDiagonalCol[4] = [False, True, False]
            self._redDiagonalCol[5] = [False, True]
            # self._redDiagonalCol[6] = [False, True, False]
            # self._redDiagonalCol[7] = [True, False]
            self._redDiagonalCol[8] = [False, True, False]
            # self._redDiagonalCol[9] = [True, False]
            self._redDiagonalCol[10] = [True, False, False]

            self._displayRed()
        elif step == 3:  # Frame 52
            # On
            # self._redDiagonalCol[0] = [True, False, True]
            # self._redDiagonalCol[1] = [False, True]
            self._redDiagonalCol[2] = [True, False, True]
            # self._redDiagonalCol[3] = [False, True]
            self._redDiagonalCol[4] = [False, True, True]
            # self._redDiagonalCol[5] = [False, True]
            # self._redDiagonalCol[6] = [False, True, False]
            self._redDiagonalCol[7] = [True, True]
            # self._redDiagonalCol[8] = [False, True, False]
            # self._redDiagonalCol[9] = [True, False]
            self._redDiagonalCol[10] = [True, True, False]

            self._displayRed()
        elif step == 4:  # Frame 53
            # Off
            self._redDiagonalCol[0] = [True, False, False]
            self._redDiagonalCol[1] = [True, False]
            self._redDiagonalCol[2] = [True, False, True]
            self._redDiagonalCol[3] = [False, False]
            self._redDiagonalCol[4] = [False, False, True]
            # self._redDiagonalCol[5] = [False, True]
            # self._redDiagonalCol[6] = [False, True, False]
            self._redDiagonalCol[7] = [False, True]
            # self._redDiagonalCol[8] = [False, True, False]
            # self._redDiagonalCol[9] = [True, False]
            self._redDiagonalCol[10] = [False, True, False]

            self._displayRed()

        elif step == 5:  # Frame 54
            # On
            #self._redDiagonalCol[0] = [True, False, False]
            #self._redDiagonalCol[1] = [True, False]
            #self._redDiagonalCol[2] = [True, False, True]
            #self._redDiagonalCol[3] = [False, False]
            self._redDiagonalCol[4] = [True, False, True]
            # self._redDiagonalCol[5] = [False, True]
            self._redDiagonalCol[6] = [False, True, True]
            #self._redDiagonalCol[7] = [False, True]
            # self._redDiagonalCol[8] = [False, True, False]
            self._redDiagonalCol[9] = [True, True]
            #self._redDiagonalCol[10] = [False, True, False]

            self._displayRed()

        elif step == 6:  # Frame 55
            # Off
            self._redDiagonalCol[0] = [True, False, False]
            #self._redDiagonalCol[1] = [True, False]
            #self._redDiagonalCol[2] = [True, False, True]
            self._redDiagonalCol[3] = [False, False]
            #self._redDiagonalCol[4] = [True, False, True]
            # self._redDiagonalCol[5] = [False, True]
            self._redDiagonalCol[6] = [False, False, True]
            #self._redDiagonalCol[7] = [False, True]
            # self._redDiagonalCol[8] = [False, True, False]
            self._redDiagonalCol[9] = [False, True]
            #self._redDiagonalCol[10] = [False, True, False]

            self._displayRed()

        elif step == 7:  # Frame 56
            # On
            self._redDiagonalCol[0] = [True, True, False]
            #self._redDiagonalCol[1] = [True, False]
            #self._redDiagonalCol[2] = [True, False, True]
            self._redDiagonalCol[3] = [True, False]
            #self._redDiagonalCol[4] = [True, False, True]
            # self._redDiagonalCol[5] = [False, True]
            self._redDiagonalCol[6] = [True, False, True]
            #self._redDiagonalCol[7] = [False, True]
            self._redDiagonalCol[8] = [False, True, True]
            #self._redDiagonalCol[9] = [False, True]
            #self._redDiagonalCol[10] = [False, True, False]

            self._displayRed()

        elif step == 8:  # Frame 57
            # Off
            self._redDiagonalCol[0] = [False, True, False]
            #self._redDiagonalCol[1] = [True, False]
            self._redDiagonalCol[2] = [True, False, False]
            #self._redDiagonalCol[3] = [True, False]
            #self._redDiagonalCol[4] = [True, False, True]
            self._redDiagonalCol[5] = [False, False]
            #self._redDiagonalCol[6] = [True, False, True]
            #self._redDiagonalCol[7] = [False, True]
            self._redDiagonalCol[8] = [False, False, True]
            #self._redDiagonalCol[9] = [False, True]
            #self._redDiagonalCol[10] = [False, True, False]

            self._displayRed()

        elif step == 9:  # Frame 58
            # On
            #self._redDiagonalCol[0] = [False, True, False]
            #self._redDiagonalCol[1] = [True, False]
            self._redDiagonalCol[2] = [True, True, False]
            #self._redDiagonalCol[3] = [True, False]
            #self._redDiagonalCol[4] = [True, False, True]
            self._redDiagonalCol[5] = [True, False]
            #self._redDiagonalCol[6] = [True, False, True]
            #self._redDiagonalCol[7] = [False, True]
            self._redDiagonalCol[8] = [True, False, True]
            #self._redDiagonalCol[9] = [False, True]
            self._redDiagonalCol[10] = [False, True, True]

            self._displayRed()

        elif step == 10:  # Frame 59 ~ equiv 45
            # Off
            #self._redDiagonalCol[0] = [False, True, False]
            #self._redDiagonalCol[1] = [True, False]
            self._redDiagonalCol[2] = [False, True, False]
            #self._redDiagonalCol[3] = [True, False]
            self._redDiagonalCol[4] = [True, False, False]
            #self._redDiagonalCol[5] = [True, False]
            #self._redDiagonalCol[6] = [True, False, True]
            self._redDiagonalCol[7] = [False, False]
            #self._redDiagonalCol[8] = [True, False, True]
            #self._redDiagonalCol[9] = [False, True]
            self._redDiagonalCol[10] = [False, False, True]

            self._displayRed()

        elif step == 11:  # Frame 46
            # Off
            #self._redDiagonalCol[0] = [False, True, False]
            self._redDiagonalCol[1] = [True, True]
            #self._redDiagonalCol[2] = [False, True, False]
            #self._redDiagonalCol[3] = [True, False]
            self._redDiagonalCol[4] = [True, True, False]
            #self._redDiagonalCol[5] = [True, False]
            #self._redDiagonalCol[6] = [True, False, True]
            self._redDiagonalCol[7] = [True, False]
            #self._redDiagonalCol[8] = [True, False, True]
            #self._redDiagonalCol[9] = [False, True]
            self._redDiagonalCol[10] = [True, False, True]

            self._displayRed()

        elif step == 12:  # Frame 47
            # Off
            #self._redDiagonalCol[0] = [False, True, False]
            self._redDiagonalCol[1] = [False, True]
            #self._redDiagonalCol[2] = [False, True, False]
            #self._redDiagonalCol[3] = [True, False]
            self._redDiagonalCol[4] = [False, True, False]
            #self._redDiagonalCol[5] = [True, False]
            self._redDiagonalCol[6] = [True, False, False]
            #self._redDiagonalCol[7] = [True, False]
            #self._redDiagonalCol[8] = [True, False, True]
            self._redDiagonalCol[9] = [False, False]
            #self._redDiagonalCol[10] = [True, False, True]

            self._displayRed()

        elif step == 13:  # Frame 48
            # On
            self._redDiagonalCol[0] = [False, True, True]
            #self._redDiagonalCol[1] = [False, True]
            #self._redDiagonalCol[2] = [False, True, False]
            self._redDiagonalCol[3] = [True, True]
            #self._redDiagonalCol[4] = [False, True, False]
            #self._redDiagonalCol[5] = [True, False]
            self._redDiagonalCol[6] = [True, True, False]
            #self._redDiagonalCol[7] = [True, False]
            #self._redDiagonalCol[8] = [True, False, True]
            self._redDiagonalCol[9] = [True, False]
            #self._redDiagonalCol[10] = [True, False, True]

            self._displayRed()

    def _displayRed(self):
        for idx, col in enumerate(self._redDiagonalCol):
            for packetIdx, packet in enumerate(col):
                if packet:
                    for point in FramesCol[idx][packetIdx]:
                        self.layout.set(point, self._redDiagonalColors)
                else:
                    for point in FramesCol[idx][packetIdx]:
                        self.layout.setOff(point)

    def rain(self):

        if not self._rainTiming:
            self._rainTiming = random.randint(1, 5)

            numCols = random.randint(0, 3)
            cols = random.sample([0, 1, 2, 3, 4, 5, 6, 7, 8, 9], numCols)

            for col in cols:
                temp = [0]
                temp.extend(self._rainCols[col])
                self._rainCols[col] = temp

            # self._rainCols[0].append(3)

        for colIdx, col in enumerate(self._rainCols):
            if col:  # Is this column active?
                addressed = {}
                for valIdx, val in enumerate(col):  # Which elements in the column are active?
                    for packetIdx, packet in enumerate(individualCol[colIdx]):
                        if (colIdx == 0 or colIdx == 9) and 0 <= val - packetIdx <= 3:
                            addressed[packetIdx] = True
                            color = color_scale(self._rainColor, int(255 - 63 * (val - packetIdx)))
                            for point in packet:
                                self.layout.set(point, color)
                        elif packetIdx <= val and 0 <= val - packetIdx <= 3:
                            addressed[packetIdx] = True
                            color = color_scale(self._rainColor, int(255 - 63 * (val - packetIdx)))
                            for point in packet:
                                self.layout.set(point, color)
                        else:
                            if not packetIdx in addressed:
                                for point in packet:
                                    self.layout.setOff(point)

                    if (colIdx == 0 or colIdx == 9) and self._rainCols[colIdx][valIdx] == 9:
                        self._rainCols[colIdx].remove(9)  # First and last column only have 4 elements
                    elif self._rainCols[colIdx][valIdx] == 10:
                        self._rainCols[colIdx].remove(10)  # Every other column has 5 elements
                    else:
                        self._rainCols[colIdx][valIdx] += 1

        self._rainTiming -= 1


anim = StripTest(led)


try:
    # run the animation
    anim.run()
except KeyboardInterrupt:
    # Ctrl+C will exit the animation and turn the LEDs offs
    led.all_off()
    led.update()
