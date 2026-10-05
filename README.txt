# TMeasure

**Version:** 1.1.3  
**Author:** Otonkart  
**Compatibility:** Blender 4.2.0 and later  

TMeasure is a streamlined Blender add-on designed to calculate the total length of selected edges or the total area of selected faces dynamically. It provides bounding box dimensions, a one-click scale apply feature, and a measurement history log to accelerate your 3D modeling workflow.

## Features

* **Smart Auto-Detection:** Automatically detects your active mesh selection mode. Calculates total **Length** in Edge Selection Mode and total **Area** in Face Selection Mode seamlessly.
* **Object Dimensions & Scale Check:** View real-time X, Y, Z bounding box dimensions. Instantly alerts you if the object's scale is not applied (1.0) and provides a non-destructive "Apply Scale" button.
* **Multi-Unit Support:** Switch between Meters (m), Centimeters (cm), Millimeters (mm), Feet (ft), and Inches (in) on the fly.
* **Measurement History:** Keeps a log of your last 5 measurements, including the object name, value, and unit for easy tracking.
* **Clipboard Integration:** One-click copy button to export the exact measurement value to your clipboard.

## Installation

1. Download the `tmeasure.zip` release file. (Ensure `blender_manifest.toml` and `tmeasure.py` are inside the zip).
2. Open Blender and navigate to `Edit > Preferences > Get Extensions`.
3. Click the drop-down menu in the top right and select `Install from Disk`.
4. Select the `tmeasure.zip` file.
5. The add-on will be installed and enabled automatically.

## Usage

1. Open the **3D Viewport**.
2. Press `N` to open the Sidebar and navigate to the **Measure** tab. You will see the **tmeasure** panel.
3. Select your mesh and enter **Edit Mode** (`Tab`).
4. Choose your selection mode (`2` for Edges, `3` for Faces).
5. Select the geometry you want to measure.
6. Click **Calculate**.
7. Use the **Copy** icon next to the total to copy the result, or check the **History** section for past measurements.

## License

This project is licensed under the [SPDX:GPL-3.0-or-later] license.