import mss
import numpy as np
import cv2
import time

print("🎥 StreamBlur - Screen Capture Test")
print("Press 'Q' to quit\n")

# Create screen capture object
sct = mss.mss()

# Get main monitor info
monitor = sct.monitors[1]  # 0 = all monitors, 1 = primary
print(f"📺 Capturing: {monitor['width']}x{monitor['height']}")

# FPS calculation variables
fps = 0
frame_count = 0
start_time = time.time()

while True:
    # Capture screen
    screenshot = sct.grab(monitor)
    
    # Convert to numpy array
    frame = np.array(screenshot)
    
    # Convert BGRA to BGR (OpenCV format)
    frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
    
    # Calculate FPS
    frame_count += 1
    elapsed = time.time() - start_time
    if elapsed > 1:  # Update FPS every second
        fps = frame_count / elapsed
        frame_count = 0
        start_time = time.time()
    
    # Draw FPS on frame
    cv2.putText(frame, f'FPS: {fps:.1f}', (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    
    # Show frame
    cv2.imshow('Screen Capture - Press Q to quit', frame)
    
    # Exit on 'Q' key
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
print("\n✅ Capture stopped!")