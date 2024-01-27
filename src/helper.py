import cv2
import pyautogui

def right_click(x, y):
    pyautogui.moveTo(x, y)
    pyautogui.rightClick()
