import math
import re
import subprocess

def read_hailstone_data(file_path):
    """Reads hailstone detection data from the file and returns a list of (frame, x, y, radius)."""
    hailstones = []
    pattern = r"Frame (\d+): X=(\d+), Y=(\d+), Radius=(\d+)"

    with open(file_path, "r") as file:
        for line in file:
            line = line.strip()
            match = re.match(pattern, line)

            if not match:
                print(f"Skipping malformed line: {line}")
                continue  # Skip incorrect lines

            try:
                frame = int(match.group(1))
                x = int(match.group(2))
                y = int(match.group(3))
                radius = int(match.group(4))
                hailstones.append([frame, x, y, radius])
                #print(f"Parsed: Frame={frame}, X={x}, Y={y}, Radius={radius}")  # Debugging output

            except ValueError as e:
                print(f"Skipping invalid line: {line} - Error: {e}")

    return hailstones


def velocity(p1, p2):
    """Calculates velocity between two points."""
    frame_diff = p2[0] - p1[0]
    if frame_diff == 0:
        return None  # Avoid division by zero
    
    #returns magnitude distance
    distance = math.sqrt((p2[1] - p1[1]) ** 2 + (p2[2] - p1[2]) ** 2)

    #time = (frame diff) / (fps)

    distanceVer = p2[2] - p1[1]
    distanceHor = p2[1] - p1[1]

    #Velocity = distance/time
    velVer = distanceVer / frame_diff
    velHor = distanceHor / frame_diff

     #Returns magnitude velocity
    velMag = distance / frame_diff

    return velVer, velHor, velMag

   

def load_pixel_to_meter():
    try:
        with open("pixelToMeter.txt", 'r') as file:
            return float(file.read().strip())
    except Exception as e:
        print(f"Error loading pixel-to-meter ratio: {e}")
        return None

def filter_hailstones(hailstones, pixel_meter_ratio, max_radius_diff=2, max_velocity_deviation=2.0):
    """Filters hailstones by ensuring consistent motion and radius."""
    filtered_hailstones = []
    n = len(hailstones)
    detectionNum = 0

    for i in range(n):
        for j in range(i + 1, n):
            for k in range(j + 1, n):
                d1, d2, d3 = hailstones[i], hailstones[j], hailstones[k]

                #print(f"Checking line: {i}, {j}")


                buffer = 0
                if(d1[1] == 936 and d2[1] == 864 and d1[3] == 60 and d2[3] == 60 and d3[3] == 60 and d3[1] == 792 and buffer == 0):
                    #print(f"{d1}\n{d2}\n{d3}")
                    buffer = 1

                if(d1[2] > d2[2] or d2[2] > d3[2] or d1[2] > d3[2]):
                    #Movement does not make sense
                    continue

                # Ensure frames are increasing (no duplicate-frame detections)
                if not (d1[0] < d2[0] < d3[0]):
                    continue
                

                if(d2[0] - d1[0] > 5 or d3[0] - d2[0] > 5):
                    #Frames are too far apart, even if this is a valid detection (Which it most likely istn't it would not be accurate enougth to track anyways)
                    continue

                # Check radius consistency
                if abs(d1[3] - d2[3]) > max_radius_diff or abs(d2[3] - d3[3]) > max_radius_diff:
                    continue

                # Check velocity consistency
                v1Ver, v1Hor, magVel1 = velocity(d1, d2)
                v2Ver, v2Hor, magVel2 = velocity(d2, d3)

                if v1Ver is None or v1Hor is None or v2Ver is None or v2Hor is None or v1Hor == 0 or v1Ver == 0 or v2Hor == 0 or v2Ver == 0:
                    continue
                
                if abs(magVel1 - magVel2) > max_velocity_deviation:
                    continue


                #At this point we have passed all of the checks we need, this is a valid detection

                #Get velocity in pixels per second
                #Take average between the two

                #print(f"{d1}\n{d2}\n{d3}, n:{detectionNum}")


                velPixelsVer = round(((v1Ver + v2Ver) / 2), 2)
                velMetersVer = round(velPixelsVer * pixel_meter_ratio, 2)

                velPixelsHor = round(((v1Hor + v2Hor) / 2), 2)
                velMetersHor = round(velPixelsHor * pixel_meter_ratio, 2)


                # If all tests pass, consider this a valid hailstone
                filtered_hailstones.append(d1 + [velMetersVer, velMetersHor, detectionNum])
                filtered_hailstones.append(d2 + [velMetersVer, velMetersHor, detectionNum])
                filtered_hailstones.append(d3 + [velMetersVer, velMetersHor, detectionNum])

                detectionNum += 1

    return filtered_hailstones


def save_filtered_hailstones(file_path, hailstones):
    """Saves filtered hailstones to a file."""
    with open(file_path, "w") as file:  # Clears the file before writing
        for hailstone in hailstones:
            frame, x, y, radius, velocityY, VelocityX, detectionNum = hailstone
            file.write(f"Frame {frame}: X={x}, Y={y}, Radius={radius}, VelocityVer={velocityY}, VelocityHor={VelocityX}, DetectionNum={detectionNum}\n")


def sortFinalDetections(radiusDiff = 2, velZDiff = 5):
    hailstones1 = []
    hailstones2 = []

    with open("filteredHailstones1.txt", 'r') as file:
        for line in file:
            #Extract values using regex
            match = re.match(r"Frame (\d+): X=(\d+), Y=(\d+), Radius=(\d+), VelocityVer=([-.\d]+), VelocityHor=([-.\d]+), DetectionNum=(\d+)", line)
            if match:
                frame, x, y, radius, vel_ver, vel_hor, detection_num = match.groups()
            # Store as nested list
            hailstones1.append([int(frame), int(x), int(y), float(radius), float(vel_ver), float(vel_hor), int(detection_num)])
    
    with open("filteredHailstones2.txt", 'r') as file:
        for line in file:
            #Extract values using regex
            match = re.match(r"Frame (\d+): X=(\d+), Y=(\d+), Radius=(\d+), VelocityVer=([-.\d]+), VelocityHor=([-.\d]+), DetectionNum=(\d+)", line)
            if match:
                frame, x, y, radius, vel_ver, vel_hor, detection_num = match.groups()
            # Store as nested list
            hailstones2.append([int(frame), int(x), int(y), float(radius), float(vel_ver), float(vel_hor), int(detection_num)])

    lastDetectionNum = [-1, -1]
    with open("filteredHailstoneFinal.txt", 'w') as file:
        for frame1, x1, y1, rad1, vVer1, vHor1, detectionNum1 in hailstones1:
            for frame2, x2, y2, rad2, vVer2, vHor2, detectionNum2 in hailstones2:

                if(frame1 == frame2):
                    if(abs(vVer2 - vVer1) < velZDiff):
                        #print(lastWrittenDetection[len(lastWrittenDetection) - 1], [detectionNum1, detectionNum2], rad1)
                        if((lastDetectionNum[0] < detectionNum1) and (lastDetectionNum[1] < detectionNum2)):

                            velocityVertical = (vVer2 + vVer1) / 2

                            file.write(f"Radius: {rad1}, VelZ={velocityVertical}, velX={vHor1}, velY={vHor2}\n")
                            lastDetectionNum = [detectionNum1, detectionNum2]

"""# Example nested loop: iterate over frames and detections
for i in range(len(data)):
    for j in range(i + 1, len(data)):
        # Example: Compare two detections
        if data[i]["Frame"] == data[j]["Frame"]:  # Same frame
            print(f"Comparing Detection {data[i]['DetectionNum']} and {data[j]['DetectionNum']} in Frame {data[i]['Frame']}")
"""


"""    with open("filteredHailstones1.txt", 'r') as file:
        for line in file:
            line = line.strip()
            line.replace(" ", "")
            parts = line.replace("Frame ", "").replace("X=", "").replace("Y=", "").replace("Radius=", "").replace("VelocityVer=", "").replace("VelocityHor=", "").replace("DetectionNum=", "").replace(":", "").split(", ")
            print(parts)
            frame, x, y, radius, vVer, vHor, detectionNum = parts[0].split()[0], *parts[1:]

            hailstones1.append([int(frame), int(x), int(y), float(radius), float(vVer), float(vHor), int(detectionNum)])

    with open("filteredHailstones2.txt", 'r') as file:
        for line in file:
            parts = line.replace("Frame ", "").replace("X=", "").replace("Y=", "").replace("Radius=", "").replace("velocityVer=", "").replace("velocityHor=", "").replace("DetectionNum=", "").replace(":", "").split(", ")
            frame, x, y, radius, vVer, vHor, detectionNum = parts[0].split()[0], *parts[1:]

            hailstones2.append([int(frame), int(x), int(y), float(radius), float(vVer), float(vHor), int(detectionNum)])
        
    for frame1, x1, y1, rad1, vVer1, vHor1, detectionNum1 in hailstones1:
        for frame2, x2, y2, rad2, vVer2, vHor2, detectionNum2 in hailstones2:

            if(frame1 == frame2):
                if(abs(vVer2 = vVer1) < velZDiff):
                    velocityVertical = (vVer2 + vVer1) / 2
                    file = open("filterdHalistoneFinal.txt", 'w')

                    file.write(f"Radius: {rad1}, VelZ={velocityVertical}, velX={vHor1}, velY={vHor2}")

                    file.close()

"""

"""      if(hailstones2.__contains__(hailstones1[i][0])):
            #Check that the radius's are within 1
            h2I = hailstones2.index(hailstones1[i][0])
            if(abs(hailstones2[h2I][3] - hailstones1[i][3]) < radiusDiff):
                #Reasonable assumption that hailstones are the same
                if(abs(hailstones2[h2I][4] - hailstones))
                file = open("FilteredHailstoneFinal.txt", 'w')

                file.write(f"Radius: {hailstones1[i][3]} VelZ: {}")

                file.close()"""


def main():
    """Main execution function."""
    hailstones = read_hailstone_data("hailstoneData.txt")

    if not hailstones:
        print("No valid hailstones found. Check input formatting.")
        return
    
    #run_conversion_script()
    from Conversion import main
    main()
    pixel_to_meter = load_pixel_to_meter()
    if(pixel_to_meter is None):
        print("Pixel-to-meter ratio missing. Run the calibration script first.")
        return

    filtered_hailstones = filter_hailstones(hailstones, pixel_to_meter)

    run = int(input("Is this the first plane, or the second (Enter 1 or 2): "))
    if(run == 1):
        save_filtered_hailstones("filteredHailstones1.txt", filtered_hailstones)
    if(run == 2):
        save_filtered_hailstones("filteredHailstones2.txt", filtered_hailstones)
    else:
        print("Please enter either 1 or 2")

    if filtered_hailstones:
        print(f"Filtered hailstones saved: {len(filtered_hailstones)} entries.")
    else:
        print("No hailstones passed the filtering criteria.")
    
    with open("filteredHailstone.txt", 'w') as file:
        file.write("")

    if(run == 2):
        sortFinalDetections()


if __name__ == "__main__":
    main()
