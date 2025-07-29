# MED-YOLO: Medical Image Segmentation with YOLO

MED-YOLO is a powerful tool for medical image segmentation using YOLO (You Only Look Once) architecture. It provides an easy-to-use interface for segmenting various medical structures including organs, tumors, vessels, and bones.

## Features

- Zero-shot medical image segmentation
- Support for multiple medical image formats (DICOM, NIfTI, TIFF)
- Pre-trained models for common medical structures
- Interactive web interface using Streamlit
- Batch processing capabilities
- Post-processing tools for medical image analysis

## Installation

```bash
pip install med-yolo
```

## Quick Start

```python
from m_yolo import predict_yolo

# Load and process a medical image
results = predict_yolo.process_image(
    image_path="path/to/your/image.dcm",
    model_type="organ",  # or "tumor", "vessel", "bone"
    confidence=0.5
)

# Visualize results
results.show()
```

## Web Interface

Run the interactive web interface:

```bash
med-yolo
```

This will start a Streamlit server where you can:
- Upload medical images
- Select segmentation models
- Adjust parameters
- View and export results

## Supported Image Formats

- DICOM (.dcm)
- NIfTI (.nii, .nii.gz)
- TIFF (.tif, .tiff)
- PNG (.png)
- JPEG (.jpg, .jpeg)

## Supported Segmentation Types

- Organs
- Tumors
- Blood Vessels
- Bones
- Other Medical Structures

## Requirements

- Python >= 3.11
- CUDA-capable GPU (recommended)
- See `setup.py` for full list of dependencies

## Citation

If you use MED-YOLO in your research, please cite:

```bibtex
@software{med_yolo2024,
  author = {Sumit Pandey},
  title = {MED-YOLO: Medical Image Segmentation with YOLO},
  year = {2024},
  publisher = {GitHub},
  url = {https://github.com/sumit-ai-ml/MED-YOLO}
}
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Contact

For questions and support, please open an issue on GitHub or contact:
- Author: Sumit Pandey
- Email: supa@di.ku.dk
- GitHub: [sumit-ai-ml](https://github.com/sumit-ai-ml)
