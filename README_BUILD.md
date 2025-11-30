# Galaxy Classifier - Build Instructions

This document explains how to compile your Galaxy Classifier GUI application into a standalone Windows executable (.exe).

## Prerequisites

All dependencies are already installed:
- Python 3.11
- PyInstaller 6.16.0
- TensorFlow 2.20.0
- PySide6 6.7.0
- h5py 3.11.0
- numpy 2.1.0

## Required Files

Ensure these files are in the `GalaxyClassifier` folder:
- ✅ `galaxy_classifier_gui.py` - Main application
- ✅ `final_galaxy_classifier.h5` - Trained model (REQUIRED - please upload if missing)
- ✅ `background.jpg` - UI background image
- ✅ `favicon.ico` - Application icon

## Build Methods

### Method 1: Automated Build Script (Recommended)

Run the automated build script:

```bash
cd GalaxyClassifier
python build_exe.py
```

This script will:
1. Clean previous build artifacts
2. Verify all required files exist
3. Run PyInstaller with optimized settings
4. Create the standalone executable

### Method 2: Manual PyInstaller

If you prefer manual control:

```bash
cd GalaxyClassifier
pyinstaller galaxy_classifier.spec --clean --noconfirm
```

### Method 3: Command Line (Without Spec File)

Build from scratch using command line:

```bash
cd GalaxyClassifier
pyinstaller --onefile --windowed \
    --add-data "final_galaxy_classifier.h5:." \
    --add-data "background.jpg:." \
    --add-data "favicon.ico:." \
    --icon="favicon.ico" \
    --name="GalaxyClassifier" \
    galaxy_classifier_gui.py
```

## Output

After building, you'll find:
- **Executable**: `dist/GalaxyClassifier.exe`
- **Build files**: `build/` (can be deleted)
- **Spec file**: `galaxy_classifier.spec` (for rebuilding)

## File Size

The executable will be approximately:
- **Size**: 500-800 MB (includes TensorFlow, PySide6, and all dependencies)
- **Standalone**: No Python installation required
- **Portable**: Can run on any Windows machine

## Distribution

To share your application:
1. Copy `dist/GalaxyClassifier.exe` to any location
2. Double-click to run (no installation needed)
3. The executable includes everything: Python, libraries, model, and assets

## Troubleshooting

### Build fails with "Missing file" error
- Ensure `final_galaxy_classifier.h5` is uploaded to the GalaxyClassifier folder
- Check all required files are present

### Executable doesn't start
- Try running from command line to see error messages
- Check Windows Defender/Antivirus isn't blocking it

### Application window is blank
- Verify `background.jpg` is bundled correctly
- Check the console for error messages

### Model loading fails
- Ensure `final_galaxy_classifier.h5` is in the same directory as the spec file
- Verify the model file isn't corrupted

## Advanced Options

### Reduce File Size
Edit `galaxy_classifier.spec` and add more excludes:
```python
excludes=['matplotlib', 'scipy', 'pandas', 'IPython', 'jupyter', 'tensorboard'],
```

### Enable Console for Debugging
In `galaxy_classifier.spec`, change:
```python
console=True,  # Change from False to True
```

### UPX Compression
UPX is enabled by default to reduce size. To disable:
```python
upx=False,
```

## Notes

- First build may take 5-10 minutes
- Subsequent builds are faster (2-3 minutes)
- The executable is self-contained with no external dependencies
- Windows may show SmartScreen warning for unsigned executables
