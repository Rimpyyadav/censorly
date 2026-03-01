import mss
import numpy as np
import cv2
import time

print("🎥 StreamBlur - Screen Blur Test")
print("Press 'B' to toggle blur")
print("Press 'Q' to quit\n")

# Screen capture object
sct = mss.mss()
monitor = sct.monitors[1]

# Settings
blur_enabled = False
fps = 0
frame_count = 0
start_time = time.time()

print(f"📺 Capturing: {monitor['width']}x{monitor['height']}")
print(f"🔵 Blur: {'ON' if blur_enabled else 'OFF'}")

while True:
    # Capture
    screenshot = sct.grab(monitor)
    frame = np.array(screenshot)
    frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
    
    # Apply blur if enabled
    if blur_enabled:
        frame = cv2.GaussianBlur(frame, (21, 21), 0)
    
    # Calculate FPS
    frame_count += 1
    elapsed = time.time() - start_time
    if elapsed > 1:
        fps = frame_count / elapsed
        frame_count = 0
        start_time = time.time()
    
    # Draw info on screen
    status = "BLUR: ON" if blur_enabled else "BLUR: OFF"
    status_color = (0, 255, 0) if blur_enabled else (0, 0, 255)
    
    cv2.putText(frame, f'FPS: {fps:.1f}', (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.putText(frame, status, (10, 70),
                cv2.FONT_HERSHEY_SIMPLEX, 1, status_color, 2)
    cv2.putText(frame, "Press 'B' to toggle | 'Q' to quit", (10, 110),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
    
    # Show frame
    cv2.imshow('StreamBlur - Screen Capture', frame)
    
    # Handle keys
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key == ord('b'):
        blur_enabled = not blur_enabled
        print(f"🔵 Blur: {'ON' if blur_enabled else 'OFF'}")

cv2.destroyAllWindows()
print("\n✅ Done!")