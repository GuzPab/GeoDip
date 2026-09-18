# GeoDip - QGIS Plugin

**GeoDip** is a QGIS plugin specifically designed for geologists and structural geologists. It allows you to quickly load, plot, and automatically style structural measurements (Dip and Dip-Direction) from Excel (.xlsx, .xls) or CSV files with cartographic quality.

## Key Features
* **Automatic Reading:** Detects and reads CSV and Excel files natively.
* **Integrated Projection:** Automatically assigns the Coordinate Reference System (EPSG) from the active project.
* **Dynamic Symbology:** Renders a custom geological symbol (SVG) automatically rotated towards the dip direction (azimuth).
* **Smart Labeling:** Implements a mathematical quadrant algorithm that dynamically positions the dip value, avoiding overlaps with the symbology.
* **Data Preservation:** Optionally keeps all original attribute columns (lithology, notes, station, etc.) in the output Shapefile.
* **Custom Styling:** Native QGIS color picker and size adjusters to customize your structural map output directly from the plugin menu.

## Requirements
* QGIS 3.x or higher.
* **Zero external dependencies!** GeoDip uses the native QGIS engine to read files, so there is no need to install `pandas` or `openpyxl`. Just install the plugin and start mapping.

## Installation
1. Download this repository as a `.zip` file by clicking the green **Code > Download ZIP** button (or download from the Releases page).
2. Open QGIS.
3. Go to the menu **Plugins > Manage and Install Plugins...**
4. Select the **Install from ZIP** tab.
5. Browse for the downloaded `.zip` file and click **Install Plugin**.

## How to Use GeoDip
1. Click the **GeoDip** icon in the QGIS toolbar.
2. Load your data table (Excel or CSV).
3. Select from the dropdown menus which columns correspond to the X/Y coordinates and the Dip / Dip-Direction values.
4. Set your preferred symbol size, text size, and color.
5. Choose whether to keep the other attributes from your table.
6. Click **Plot Measurements** and choose where to save your new Shapefile.
7. Done! QGIS will automatically plot your points with professional structural symbology.

## Author
Created by **Pablo Guzman H**