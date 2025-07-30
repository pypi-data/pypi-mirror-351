# MMLLM Face Refinement

This project implements a novel approach to face detection by combining traditional face detection methods with multimodal large language models (MMLLM) for refinement and false positive elimination.

## Approach

1. **Initial Detection**: Use YOLOv11-Face to detect potential faces in images
2. **Refinement**: Each detected face is then analyzed using multimodal LLMs:
   - Gemini API for cloud-based analysis
   - LLaVA-NeXT (local model) for on-device analysis
3. **False Positive Elimination**: The LLMs determine if the detection is actually a face
4. **Bounding Box Refinement**: The LLMs can suggest refinements to the bounding boxes

## Requirements

- Python 3.8+
- See `requirements.txt` for all dependencies
- YOLOv11-Face model file (yolov11l-face.pt) in the models directory

## Installation

### Automatic Installation

#### Linux/macOS

```bash
# Clone the repository
git clone https://github.com/JonathanLehner/mmllm-face-refinement.git
cd mmllm-face-refinement

# Run the installation script
chmod +x install.sh
./install.sh
```

#### Windows

```cmd
# Clone the repository
git clone https://github.com/yourusername/mmllm-face-refinement.git
cd mmllm-face-refinement

# Run the installation script
install.bat
```

### Manual Installation

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate.bat
   ```

2. Install the package:
   ```bash
   pip install -e .
   ```

3. Download the YOLOv11-Face model:
   - Get the model from [akanametov/yolo-face](https://github.com/akanametov/yolo-face)
   - Place it in the `models` directory as `yolov11l-face.pt`

4. Set up API keys:
   ```bash
   cp .env.example .env
   # Edit .env file with your API keys
   ```

## Usage

1. Place input images in the `input` folder
2. Run the main script: `python main.py`
3. Results will be saved in the `output` folder

For debugging purposes, you can run the test script with debug enabled:
```
python test.py --image input/your_image.jpg --debug
```

## Configuration

You can adjust parameters in `config.yaml`:
- YOLO confidence threshold
- Bounding box padding
- LLM endpoint selection
- Output formatting options
- Debug settings

### Debug Mode

The system includes a debug mode that saves intermediate results:

```yaml
debug:
  enabled: true  # Enable debug mode
  save_raw_detections: true  # Save initial YOLO detections
  save_intermediate_steps: true  # Save cropped faces before LLM analysis
```

When debug mode is enabled, the following files are saved to the `output/debug` directory:
- Images with YOLO detections visualized
- JSON files with detection coordinates
- Cropped face images before LLM processing
- JSON files with detection metadata

## References

This project utilizes the following models and repositories:

- **YOLOv11-Face**: State-of-the-art face detection model from [akanametov/yolo-face](https://github.com/akanametov/yolo-face)
- **LLaVA-NeXT**: Local multimodal LLM from [LLaVA-VL/LLaVA-NeXT](https://github.com/LLaVA-VL/LLaVA-NeXT)
- **Gemini API**: Google's multimodal generative AI model

## Upload to pipy
- python -m build
- pip install dist/mmllm_face_refinement-0.1.0-py3-none-any.whl
- python -m twine upload dist/*

## Note

This is a research project demonstrating the use of multimodal LLMs for improving traditional computer vision tasks. 
