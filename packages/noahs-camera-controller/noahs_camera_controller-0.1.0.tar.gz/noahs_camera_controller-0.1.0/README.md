## Usage: `noahs_camera_controller`

This library provides a simple way to do basic photo a video capture.  On most devices, opencv will be used, however, on arm based linux devices like raspberry pi, libcamera-still and libcamera-vid will be used.  Make sure your command line has permission to access your camera before use.

### Getting Started

First, install the library:

```bash
pip install noahs_camera_controller
```

Then run the sample code below.

```python
from noahs_camera_controller import list_available_cameras, capture_photo, capture_video

capture_photo(name="my_photo",rotation=None, hflip=False, vflip=False, device_index=0)
capture_video(name="my_video", duration=5, rotation=None, hflip=False, vflip=False, device_index=0)

```



### Check out Source Code

`https://github.com/jonesnoah45010/camera_controller`




