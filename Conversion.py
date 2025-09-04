import cv2
import math

def get_pixel_to_meter_ratio(video_path, real_world_distance):
    """Prompts user to click two points on the first frame to determine pixel-to-meter ratio."""
    
    if(str(real_world_distance).lower() == "keep"):
        file = open("pixelToMeter.txt", 'r')
        ratio = float(file.readline())
        file.close()
    else:
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            print("Error: Could not open video.")
            return None
        
        ret, frame = cap.read()
        cap.release()
        
        if not ret:
            print("Error: Could not read the first frame.")
            return None
        
        points = []
        
        def click_event(event, x, y, flags, param):
            if event == cv2.EVENT_LBUTTONDOWN:
                points.append((x, y))
                cv2.circle(frame, (x, y), 5, (0, 0, 255), -1)
                cv2.imshow("Select Reference Points", frame)
                
                if len(points) == 2:
                    cv2.destroyAllWindows()
        
        cv2.imshow("Select Reference Points", frame)
        cv2.setMouseCallback("Select Reference Points", click_event)
        cv2.waitKey(0)
        
        if len(points) < 2:
            print("Error: Two points were not selected.")
            return None
    
        real_world_distance = float(real_world_distance)
        pixel_distance = math.dist(points[0], points[1])
        ratio = real_world_distance / pixel_distance
        
        print(f"Pixel Distance: {pixel_distance:.2f} pixels")
        print(f"Pixel-to-Meter Ratio: {ratio:.6f} meters per pixel")

    return ratio

def main():
    from Track import returnPath
    path = returnPath
    #print(path)
    #Track.video_path
    video_path = "/users/lucst/videos/captures/halistoneTest.mp4"  # Ensure this is the correct video file

    real_world_distance = (input("Enter the real-world distance (meters) between the two selected points, Type 'keep' to continue with current data: "))
    ratio = get_pixel_to_meter_ratio(video_path, real_world_distance)
    
    if ratio is not None:  # Only save if ratio is valid
        with open("pixelToMeter.txt", "w") as file:
            file.write(str(ratio))
        print("Ratio saved to pixelToMeter.txt")
    else:
        print("Error: No valid ratio obtained. Plese run the script again.")
