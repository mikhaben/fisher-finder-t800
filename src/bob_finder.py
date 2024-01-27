import cv2
import mss
import numpy as np
import time
import pyautogui
import random

def get_center_position(scan_x, scan_y, scan_width, scan_height) -> tuple[int, int]:
    center_x = scan_x + scan_width // 2
    center_y = scan_y + scan_height // 2
    return center_x, center_y

def find_bobber_position(gray_img) -> tuple[int, int, int, int, tuple[int, int]]:
    threshold = 0.6  # Define a threshold for matching
    template = cv2.imread("src/img/bobber.jpg", 0)
    template_w, template_h = template.shape[::-1]

    res = cv2.matchTemplate(gray_img, template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

    # Check if the best match is above the threshold
    if max_val >= threshold:
        scan_x, scan_y = max_loc[0], max_loc[1]
        print("Bobber found at -> ", scan_x, scan_y, template_w, template_h)
        return scan_x, scan_y, template_w, template_h

def splash_detect(scan_x, scan_y, scan_width, scan_height) -> bool:
    white_threshold = 200
    splash_pixel_count = 35

    # Double the scan area
#     scan_width_2x = scan_width * 2
#     scan_height_2x = scan_height * 2
#     x_position = scan_x - scan_width // 2
#     y_position = scan_y - scan_height // 2
#     scan_area = {"top": y_position, "left": x_position, "width": scan_width_2x, "height": scan_height_2x}
    scan_area = {"top": scan_y, "left": scan_x, "width": scan_width, "height": scan_height}

    with mss.mss() as sct:
        img = np.array(sct.grab(scan_area))
        gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Draw a rectangle around the area of interest
#         cv2.rectangle(img, (0, 0), (scan_width, scan_height), (0, 255, 0), 2)
#         cv2.imshow("Splash Detection Area", img)

        white_pixels = np.sum(gray_img > white_threshold)
        if white_pixels > splash_pixel_count:
            print("Splash detected!")
            # Splash detected
            return True

        return False

def process_screen():
    # Screen capture size
    monitor = {"top": 0, "left": 0, "width": 2200, "height": 1600}
    # Throttle the loop to 1 FPS
    timeout = 50
    # Bobber search state
    bobber_found = False
    # Cursor position
    cursor_position = None

    with mss.mss() as sct:
        while True:
            if not bobber_found:
                # Capture the screen and search for the bobber
                img = np.array(sct.grab(monitor))
                gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                target = find_bobber_position(gray_img)

                if target:
                    bobber_found = True
                    cursor_position = get_center_position(*target)
                    pyautogui.moveTo(*cursor_position)

            if bobber_found:
                # Perform splash detection around the bobber's position
                if splash_detect(*target):
                    # Generate a random delay between 0.1 and 1 second
                    delay_before_click = random.uniform(0.3, 1.0)
                    time.sleep(delay_before_click)
                    pyautogui.click()
                    print(f"CLICK! (after {delay_before_click:.2f} seconds)")
                    # Reset state to search for bobber again, reset cursor position
                    bobber_found = False
                    cursor_position = None
                    # break the loop
                    break

            # Break the loop if 'q' is pressed
            if cv2.waitKey(timeout) & 0xFF == ord("q"):
                break

        cv2.destroyAllWindows()

