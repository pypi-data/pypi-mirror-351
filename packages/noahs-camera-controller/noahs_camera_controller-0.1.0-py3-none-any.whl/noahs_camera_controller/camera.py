import os
import platform
import cv2
import subprocess
import time

def list_available_cameras(max_devices=10):
    available = []
    for i in range(max_devices):
        cap = cv2.VideoCapture(i)
        if cap.read()[0]:
            available.append(i)
        cap.release()
    return available

def capture_photo(name="last_photo", rotation=None, hflip=False, vflip=False, device_index=0):
    output_path = f"{name}.jpg"

    def use_opencv():
        cap = cv2.VideoCapture(device_index)
        if not cap.isOpened():
            print(f"[OpenCV] Cannot access camera index {device_index}.")
            return False

        ret, frame = cap.read()
        cap.release()

        if not ret:
            print("[OpenCV] Failed to grab frame.")
            return False

        if hflip:
            frame = cv2.flip(frame, 1)
        if vflip:
            frame = cv2.flip(frame, 0)
        if rotation in [90, 180, 270]:
            rotate_code = {
                90: cv2.ROTATE_90_CLOCKWISE,
                180: cv2.ROTATE_180,
                270: cv2.ROTATE_90_COUNTERCLOCKWISE
            }[rotation]
            frame = cv2.rotate(frame, rotate_code)

        cv2.imwrite(output_path, frame)
        print(f"[OpenCV] Photo saved: {output_path}")
        return True

    def use_libcamera():
        command = ["libcamera-still", "-o", output_path, "--timeout", "1", "--nopreview"]
        if rotation in [0, 90, 180, 270]:
            command += ["--rotation", str(rotation)]
        if hflip:
            command.append("--hflip")
        if vflip:
            command.append("--vflip")
        try:
            subprocess.run(command, check=True)
            print(f"[libcamera] Photo saved: {output_path}")
            return True
        except Exception as e:
            print(f"[libcamera] Error: {e}")
            return False

    if platform.system() == "Linux" and "arm" in platform.machine():
        use_libcamera()
    else:
        if not use_opencv():
            use_libcamera()



def capture_video(name="last_video", duration=5, rotation=None, hflip=False, vflip=False, device_index=0):
    output_path = f"{name}.mp4"

    def use_opencv():
        cap = cv2.VideoCapture(device_index)
        if not cap.isOpened():
            print(f"[OpenCV] Cannot access camera index {device_index}.")
            return False

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        fps = 20.0
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        start_time = time.time()

        while time.time() - start_time < duration:
            ret, frame = cap.read()
            if not ret:
                print("[OpenCV] Frame capture failed.")
                break

            if hflip:
                frame = cv2.flip(frame, 1)
            if vflip:
                frame = cv2.flip(frame, 0)
            if rotation in [90, 180, 270]:
                rotate_code = {
                    90: cv2.ROTATE_90_CLOCKWISE,
                    180: cv2.ROTATE_180,
                    270: cv2.ROTATE_90_COUNTERCLOCKWISE
                }[rotation]
                frame = cv2.rotate(frame, rotate_code)

            out.write(frame)

        cap.release()
        out.release()
        print(f"[OpenCV] Video saved: {output_path}")
        return True

    def use_libcamera():
        command = ["libcamera-vid", "-o", output_path, "--duration", str(duration * 1000), "--nopreview"]
        if rotation in [0, 90, 180, 270]:
            command += ["--rotation", str(rotation)]
        if hflip:
            command.append("--hflip")
        if vflip:
            command.append("--vflip")
        try:
            subprocess.run(command, check=True)
            print(f"[libcamera] Video saved: {output_path}")
            return True
        except Exception as e:
            print(f"[libcamera] Error: {e}")
            return False

    if platform.system() == "Linux" and "arm" in platform.machine():
        use_libcamera()
    else:
        if not use_opencv():
            use_libcamera()



