# DIVOOM PIXOO 64x64 Controller

A comprehensive Python controller for the DIVOOM PIXOO 64x64 WiFi LED pixel display. This project provides advanced control capabilities including text display, custom pixel matrices, and smooth 30fps animations.

## 🚀 Features

- **🎯 Text Display**: Simple text, clock, and auto-marquee support
- **🎨 Pixel Graphics**: Custom pixel matrices with various patterns
- **🎬 Animations**: 4 built-in smooth animations with configurable FPS
- **⚙️ Configurable FPS**: Real-time FPS adjustment (1-30 fps)
- **🔄 Clean API**: Proper RGB data encoding (no GIF corruption)
- **📱 Interactive Menu**: User-friendly command-line interface

## 🛠️ Installation

### Prerequisites

- Python 3.7+
- DIVOOM PIXOO 64x64 connected to WiFi
- Network access to your PIXOO device

### Setup

1. **Clone/Download the project**
   ```bash
   cd Divoom_Pixoo64
   ```

2. **Create virtual environment**
   ```bash
   python3 -m venv pixoo_env
   source pixoo_env/bin/activate  # Linux/Mac
   # OR
   pixoo_env\Scripts\activate     # Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure your PIXOO IP**
   Edit `pixoo_controller.py` and change the IP address:
   ```python
   PIXOO_IP = "192.168.1.100"  # Replace with your PIXOO's IP
   ```

## 🎮 Usage

Run the controller:
```bash
python pixoo_controller.py
```

### Menu Options

```
📺 PIXOO Controller (FPS: 20)
1 - Reset and prepare device
2 - Send simple text
3 - Show clock
4 - Marquee text
5 - Pixel matrix (gradient)
6 - Pixel matrix (checkerboard)
7 - Pixel matrix (border)
8 - Pixel matrix (test)
9 - Clear display
A - Animation: Spinner
B - Animation: Wave
C - Animation: Plasma
D - Animation: Bouncing Ball
F - Set FPS (current: 20)
0 - Exit
```

## 🎬 Available Animations

### Spinner
- **Description**: Rotating point around a blue ring
- **Best FPS**: 20-25 fps
- **Frames**: 30

### Wave
- **Description**: Animated sine wave moving horizontally
- **Best FPS**: 15-20 fps  
- **Frames**: 25

### Plasma
- **Description**: Psychedelic plasma effect with RGB colors
- **Best FPS**: 18-22 fps
- **Frames**: 35

### Bouncing Ball
- **Description**: Physics-based bouncing yellow ball
- **Best FPS**: 12-18 fps
- **Frames**: 20

## 🔧 Technical Details

### API Format
The PIXOO 64x64 uses **raw RGB data** (not GIF format) for `SendHttpGif` commands:
- **Format**: RGB24 (3 bytes per pixel)
- **Size**: 64×64×3 = 12,288 bytes per frame
- **Encoding**: Base64 encoded RGB data
- **Max Frames**: 40 frames per animation (device limit)

### Command Sequence
```python
# Proper sequence to avoid noise/corruption:
1. Draw/ResetHttpGifId
2. Draw/ClearHttpText  
3. Channel/SetIndex (4)
4. Draw/SendHttpGif (with RGB data)
```

### Frame Rate Control
- **Method**: Controlled via `PicSpeed` parameter (milliseconds)
- **Formula**: `PicSpeed = max(1, int(1000 / fps))`
- **Limitation**: Network latency affects actual FPS
- **Recommended**: 15-25 fps for smooth animations

## 🐛 Troubleshooting

### Common Issues

**1. Noise in first row of pixels**
- **Cause**: Corrupted GIF data or wrong format
- **Solution**: Use raw RGB data format (implemented in this project)

**2. Animation not playing**
- **Cause**: Device not reset or wrong channel
- **Solution**: Always call `reset_device()` before sending animations

**3. Slow/choppy animations**
- **Cause**: High FPS or network issues
- **Solution**: Lower FPS (try 15-20) or check WiFi connection

**4. Device crashes**
- **Cause**: Too many frames (>40) or rapid commands
- **Solution**: Limit to 40 frames, add delays between commands

## 📚 API Reference

### Core Methods

```python
# Initialize controller
pixoo = PixooController("192.168.1.100")

# Text operations
pixoo.send_text("Hello World", x=0, y=20, color="#FFFFFF")
pixoo.send_clock()
pixoo.send_marquee("Long scrolling text...")

# Graphics
pixoo.send_pixel_matrix("gradient")  # gradient, checkerboard, border, test
pixoo.clear_display()

# Animations  
pixoo.send_animation("spinner", total_frames=30, fps=20)
pixoo.set_fps(25)  # Change global FPS setting
```

### Supported Patterns
- `gradient`: Rainbow gradient effect
- `checkerboard`: Black/white checkerboard  
- `border`: Cyan border frame
- `test`: Debug pattern for testing

## 🔗 References and Acknowledgments

This project was developed using insights and code from several excellent open-source projects:

### Primary References
- **[pixoo-rest](https://github.com/4ch1m/pixoo-rest)** by 4ch1m
  - RESTful API wrapper for PIXOO devices
  - Swagger UI implementation reference
  - Command structure insights

- **[pixoo_api](https://github.com/Grayda/pixoo_api)** by Grayda  
  - Comprehensive API documentation and notes
  - Frame limitation discoveries (40 frame max)
  - RGB encoding methodology
  - Animation sequence understanding

- **[divoom](https://github.com/r12f/divoom)** by r12f
  - Rust implementation reference
  - Device discovery methods
  - API command examples

### Additional Resources
- **[SomethingWithComputers/pixoo](https://github.com/SomethingWithComputers/pixoo)** - Python library reference
- **DIVOOM Official Documentation** - http://doc.divoom-gz.com/web/#/12?page_id=196
- **Home Assistant Community** - PIXOO integration discussions and troubleshooting

### Key Insights Borrowed
1. **RGB Data Format**: Understanding that PIXOO uses raw RGB24 data, not GIF format
2. **Frame Limitations**: 40-frame maximum per animation to prevent crashes  
3. **Command Sequencing**: Proper reset and preparation sequence
4. **Error Handling**: Network timeout and device stability considerations

## 📄 License

This project is provided as-is for educational and personal use. Please respect the original licenses of the referenced projects.

## 🤝 Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

## ⚠️ Disclaimer

Use at your own risk. The PIXOO device API lacks official documentation, and excessive use may cause device instability. Always test with lower frame rates first.

---

**Made with ❤️ for the PIXOO community**