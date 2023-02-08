# ////////////////////////////////////////////////////////////////
# //                     IMPORT STATEMENTS                      //
# ////////////////////////////////////////////////////////////////

import math
import sys
import time

from kivy.app import App
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import *
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.slider import Slider
from kivy.uix.image import Image
from kivy.uix.behaviors import ButtonBehavior
from kivy.clock import Clock
from kivy.animation import Animation
from functools import partial
from kivy.config import Config
from kivy.core.window import Window
from pidev.kivy import DPEAButton
from pidev.kivy import PauseScreen
from time import sleep
import RPi.GPIO as GPIO
from dpeaDPi.DPiComputer import DPiComputer
from dpeaDPi.DPiStepper import *

# ////////////////////////////////////////////////////////////////
# //                      GLOBAL VARIABLES                      //
# //                         CONSTANTS                          //
# ////////////////////////////////////////////////////////////////
START = True
STOP = False
UP = False
DOWN = True
ON = True
OFF = False
YELLOW = .180, 0.188, 0.980, 1
BLUE = 0.917, 0.796, 0.380, 1
CLOCKWISE = 0
COUNTERCLOCKWISE = 1
ARM_SLEEP = 2.5
DEBOUNCE = 0.10

lowerTowerPosition = 60
upperTowerPosition = 76

dpiStepper = DPiStepper()
dpiStepper.setBoardNumber(0)
dpiComputer = DPiComputer()
dpiComputer.initialize()

microstepping = 8
dpiStepper.setMicrostepping(microstepping)

speed_steps_per_second = 400 * microstepping
accel_steps_per_second_per_second = speed_steps_per_second
dpiStepper.setSpeedInStepsPerSecond(0, speed_steps_per_second)
dpiStepper.setSpeedInStepsPerSecond(1, speed_steps_per_second)
dpiStepper.setAccelerationInStepsPerSecondPerSecond(0, accel_steps_per_second_per_second)
dpiStepper.setAccelerationInStepsPerSecondPerSecond(1, accel_steps_per_second_per_second)
# ////////////////////////////////////////////////////////////////
# //            DECLARE APP CLASS AND SCREENMANAGER             //
# //                     LOAD KIVY FILE                         //
# ////////////////////////////////////////////////////////////////
global position_int
class MyApp(App):

    def build(self):
        self.title = "Robotic Arm"
        return sm


Builder.load_file('main.kv')
Window.clearcolor = (.7, .2, .4, .1)  # (WHITE)


# ////////////////////////////////////////////////////////////////
# //                    SLUSH/HARDWARE SETUP                    //
# ////////////////////////////////////////////////////////////////

sm = ScreenManager()


# ////////////////////////////////////////////////////////////////
# //                       MAIN FUNCTIONS                       //
# //             SHOULD INTERACT DIRECTLY WITH HARDWARE         //
# ////////////////////////////////////////////////////////////////


class MainScreen(Screen):
    lastClick = time.clock()
    armPosition = 0
    magnetstate = "Magnet On"

    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        self.initialize()

    def debounce(self):
        processInput = False
        currentTime = time.clock()
        if ((currentTime - self.lastClick) > DEBOUNCE):
            processInput = True
        self.lastClick = currentTime
        return processInput


    def toggleMagnet(self):
        print("Process magnet here")

    def auto(self):
        dpiStepper.enableMotors(True)
        dpiStepper.setSpeedInStepsPerSecond(0, 600)
        if (dpiComputer.readDigitalIn(dpiComputer.IN_CONNECTOR__IN_0)) == 1:
            dpiStepper.moveToRelativePositionInSteps(0, 1340, True)
            dpiComputer.writeServo(1, 180)
            dpiComputer.writeServo(0, 0)
            sleep(1.75)
            dpiComputer.writeServo(0, 90)
            dpiStepper.moveToRelativePositionInSteps(0, -540, True)
            dpiComputer.writeServo(0, 0)
            sleep(1.5)
            dpiComputer.writeServo(1, 90)
            dpiComputer.writeServo(0, 90)
        else:
            dpiStepper.moveToRelativePositionInSteps(0, 830, True)
            dpiComputer.writeServo(1, 180)
            dpiComputer.writeServo(0, 0)
            sleep(1.5)
            dpiComputer.writeServo(0, 90)
            dpiStepper.moveToRelativePositionInSteps(0, 500, True)
            dpiComputer.writeServo(0, 0)
            sleep(1.5)
            dpiComputer.writeServo(1, 90)
            dpiComputer.writeServo(0, 90)
        return

    def setArmPosition(self, armPosition):
        self.armPosition = armPosition
        global position_int
        position_int = int(armPosition)
        return

    def moveArmDown(self):
        dpiComputer.writeServo(0, 0)
        sleep(1.5)
        dpiComputer.writeServo(0, 90)
        return

    def toggleArm(self):
        dpiStepper.enableMotors(True)
        dpiStepper.moveToRelativePositionInSteps(0, position_int, True)
        dpiStepper.enableMotors(False)
        return
    def togglemagnet(self, magnetstate):
        if magnetstate == "Magnet On":
            magnetstate = "Magnet Off"
            dpiComputer.writeServo(1, 180)
        else:
            magnetstate = "Magnet On"
            dpiComputer.writeServo(1, 90)
        return(magnetstate)
    def homeArm(self):
        dpiStepper.enableMotors(True)
        dpiStepper.moveToHomeInSteps(0, 1, 1600, 3200)
        dpiStepper.enableMotors(False)
        return

    def isBallOnTallTower(self):
        if (dpiComputer.readDigitalIn(dpiComputer.IN_CONNECTOR__IN_0)):
            if dpiComputer.readDigitalIn(dpiComputer.IN_CONNECTOR__IN_0):
                return
        if dpiComputer.readDigitalIn(dpiComputer.IN_CONNECTOR__IN_0) == 0:
           dpiStepper.moveToRelativePositionInSteps(0, 1600, True)
        return

    def isBallOnShortTower(self):
        print("Determine if ball is on the bottom tower")

    def initialize(self):
        dpiStepper.enableMotors(True)
        dpiStepper.moveToHomeInSteps(0, -1, 1600, 3200)
        dpiStepper.enableMotors(False)
        return

    def resetColors(self):
        self.ids.armControl.color = YELLOW
        self.ids.magnetControl.color = YELLOW
        self.ids.auto.color = BLUE

    def quit(self):
        MyApp().stop()


sm.add_widget(MainScreen(name='main'))

# ////////////////////////////////////////////////////////////////
# //                          RUN APP                           //
# ////////////////////////////////////////////////////////////////

MyApp().run()