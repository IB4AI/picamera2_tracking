import cv2
import picamera2

# Initialize the Picamera2 object
picam2 = picamera2.Picamera2()
picam2.preview_configuration.main.size = (640, 480)
picam2.preview_configuration.main.format = "RGB888"
picam2.preview_configuration.controls.FrameRate = 30
picam2.preview_configuration.align()
picam2.configure("preview")

# Start the camera
picam2.start()

# Create a named window for displaying the frames
cv2.namedWindow('Frame', cv2.WINDOW_GUI_NORMAL)

# Initialize variables for Region of Interest (ROI) selection
p1, p2 = None, None
state = 0

# Define a bounding box for the tracker
bbox = (0, 50, 50, 100)

# Set up the CSRT tracker
tracker = cv2.legacy.TrackerCSRT_create()

# Mouse callback function to handle mouse events
def on_mouse(event, x, y, flags, userdata):
    global state, p1, p2, bbox, tracker, frame

    # Left mouse button released
    if event == cv2.EVENT_LBUTTONUP:
        # Select the first point
        if state == 0:
            p1 = (x, y)
            state += 1
        # Select the second point
        elif state == 1:
            p2 = (x, y)
            state += 1
            width = p2[0] - p1[0]
            height = p2[1] - p1[1]
            bbox = (p1[0], p1[1], width, height)

            # Initialize the tracker with the first frame and bounding box
            tracker = cv2.legacy.TrackerCSRT_create()
            tracker.init(frame, bbox)

    # Right mouse button released (erase current ROI)
    if event == cv2.EVENT_RBUTTONUP:
        p1, p2 = None, None
        state = 0

# Register the mouse callback function
cv2.setMouseCallback('Frame', on_mouse)

while True:
    # Capture a frame from the camera
    frame = picam2.capture_array()
    
    if state > 1:
        # Update the tracker with the current frame
        success, bbox = tracker.update(frame)
        
        if success:
            # Draw a rectangle around the tracked object
            p1 = (int(bbox[0]), int(bbox[1]))
            p2 = (int(bbox[0] + bbox[2]), int(bbox[1] + bbox[3]))
            cv2.rectangle(frame, p1, p2, (0, 255, 0), 2, 1)
            cv2.putText(frame, "Tracking", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (150, 25, 150), 2)
        else:
            # Indicate tracking failure
            cv2.putText(frame, "Tracking Lost", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 2)

    # Display the frame
    cv2.imshow('Frame', frame)

    # Wait for 30 ms and check if the ESC key is pressed
    key = cv2.waitKey(30)
    if key == 27:
        cv2.destroyAllWindows()
        break
