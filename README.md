# GeoDip - Structural Geology Plotter for QGIS 

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23382530.svg)](https://doi.org/10.5281/zenodo.23382530)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![QGIS Compatibility](https://img.shields.io/badge/QGIS-3.30%20%7C%204.x-green.svg)](https://qgis.org)

**GeoDip** is an open-source QGIS plugin designed to automate and standardize the visual representation of structural geological measurements (**Dip** and **Dip-Direction**). It saves geologists time and prevents manual configuration errors when plotting field data from Excel or CSV files, applying dynamic SVG symbology and smart quadrant labeling automatically.

---

##  Key Features

* **Direct CSV & Excel Import:** Load `.csv`, `.xlsx`, and `.xls` structural datasets seamlessly without intermediate conversions.
* **Smart Column Auto-Detection:** Automatically scans and selects matching columns for *X/Easting*, *Y/Northing*, *Dip*, and *Dip-Direction* (supports both English and Spanish field headers).
* **Dynamic Structural Symbology:** Rotates geological strike/dip SVG symbols dynamically based on Dip-Direction values and allows custom symbol sizing and coloring.
* **8-Quadrant Smart Labeling:** Automatically positions Dip angle labels around the symbol tip so text never overlaps the strike line or tick mark.
* **GeoPackage (`.gpkg`) & Shapefile (`.shp`) Export:** Choose your preferred output format while preserving all original field attributes (lithology, station ID, notes, etc.).
* **Embedded Database Styling:** When exporting to GeoPackage, GeoDip saves the dynamic SVG rotation and labeling rules directly inside the `.gpkg` database (`saveStyleToDatabase`), allowing you to share fully styled layers in a single file.
* **Universal Compatibility:** Built on the `qgis.PyQt` bridge for full compatibility across **QGIS 3 (PyQt5)** and **QGIS 4 (PyQt6)**.

---

##  Installation

### Option 1: From the Official QGIS Plugin Repository (Recommended)
1. Open **QGIS**.
2. Go to **Plugins > Manage and Install Plugins...**
3. Search for **`GeoDip`** and click **Install Plugin**.

### Option 2: Install from ZIP
1. Download the latest **`geo_dip.zip`** from the [Releases](https://github.com/GuzPab/GeoDip/releases) page.
2. In QGIS, go to **Plugins > Manage and Install Plugins > Install from ZIP**.
3. Select the downloaded `.zip` file and click **Install Plugin**.

---

##  How to Use

1. Open **GeoDip** from the QGIS toolbar or the **Plugins** menu.
2. Click **Load CSV/Excel File** and select your structural measurements dataset.
3. Verify the auto-detected columns for **X Coordinate**, **Y Coordinate**, **Dip Column**, and **Dip-Direction Column**.
4. Select the Coordinate Reference System (**CRS**) of your coordinates.
5. *(Optional)* Check **Keep all original columns (lithology, notes, etc.)** to preserve your complete attribute table, and customize the **Symbol Size**, **Text Size**, and **Symbol Color**.
6. Click **Plot Measurements** and choose whether to save your output layer as a **GeoPackage (`.gpkg`)** or **ESRI Shapefile (`.shp`)**.

---

##  How to Cite

If you use **GeoDip** in your scientific research, thesis, technical reports, or geological mapping projects, please cite it using its official Zenodo DOI:

**APA Style:**
> Guzmán H., P. (2026). *GeoDip: A QGIS plugin for automated structural measurements plotting* (Version 1.1.1) [Computer software]. Zenodo. https://doi.org/10.5281/zenodo.23382530

**BibTeX:**
```bibtex
@software{Guzman_GeoDip_2026,
  author       = {Guzmán H., Pablo},
  title        = {{GeoDip: Automated structural measurements plotter for QGIS}},
  year         = {2026},
  publisher    = {Zenodo},
  version      = {1.1.1},
  doi          = {10.5281/zenodo.23382530},
  url          = {[https://doi.org/10.5281/zenodo.23382530](https://doi.org/10.5281/zenodo.23382530)}
}
```

---

## 📄 License & Author

* **Author:** Pablo Guzmán H. (`pabloguzmanherr@gmail.com`)
* **License:** This project is licensed under the **GNU General Public License v3.0 (GPL-3.0)** - see the [LICENSE](LICENSE) file for details.
* **Issues & Feedback:** Please report bugs or feature requests on the [GitHub Issues](https://github.com/GuzPab/GeoDip/issues) page.
