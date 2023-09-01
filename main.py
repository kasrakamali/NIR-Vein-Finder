#!/usr/bin/python
import cv2
import numpy as np

# Create two CLAHE objects with different tile grid sizes
clahe1 = cv2.createCLAHE(clipLimit=24, tileGridSize=(16, 16))
clahe2 = cv2.createCLAHE(clipLimit=24, tileGridSize=(20, 20))

# Create a 3x3 kernel of ones
kernel = np.ones((3, 3), np.uint8)

# Open the default camera
cap = cv2.VideoCapture(0)

# Check if camera was opened successfully
if not cap.isOpened():
    print("Cannot open camera")
    exit()

# Loop until the user presses 'q'
while True:
    # Read a frame from the camera
    ret, frame = cap.read()

    # Extract the green channel from the frame
    frame_gray = frame[:, :, 1]

    # Crop the frame to a specific region of interest
    frame_gray = frame_gray[48:432, 64:576]

    # Threshold the frame to create a binary mask
    _, frame_mask = cv2.threshold(frame_gray, 40, 1, 1)

    # Invert the mask
    frame_mask = 1-frame_mask

    # Apply CLAHE to the gray frame twice
    frame_eq = clahe1.apply(frame_gray)
    frame_eq = clahe2.apply(frame_eq)

    # Combine the original gray frame and the equalized frame horizontally
    output1 = np.hstack([frame_gray, frame_eq])

    # Convert the output to a BGR image
    output1 = cv2.cvtColor(output1, cv2.COLOR_GRAY2BGR)

    # Multiply the equalized frame by the mask, then apply a color map 
    frame_glev = np.uint8(frame_eq/64)*64*frame_mask
    frame_lev = cv2.applyColorMap(frame_glev, cv2.COLORMAP_JET)

    # Apply adaptive thresholding to the masked, equalized frame
    frame_bin = cv2.adaptiveThreshold(
        frame_glev, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 201, 10)

    # Perform morphological closing and opening on the binary frame
    frame_bin = cv2.morphologyEx(frame_bin, cv2.MORPH_CLOSE, kernel)
    frame_bin = cv2.morphologyEx(frame_bin, cv2.MORPH_OPEN, kernel)

    # Convert the binary frame to a BGR image
    frame_bin = cv2.cvtColor(frame_bin, cv2.COLOR_GRAY2BGR)

    # Combine the color-mapped frame and the binary frame horizontally
    output2 = np.hstack([frame_lev, frame_bin])

    # Combine the two outputs vertically
    output = np.vstack([output1, output2])

    # Show the output in a window named "Output"
    cv2.imshow('Output', output)

    # Exit the loop if the user presses 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the camera and destroy all windows
cap.release()
cv2.destroyAllWindows()
