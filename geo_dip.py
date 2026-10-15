# -*- coding: utf-8 -*-
"""
/***************************************************************************
 GeoDip
                                 A QGIS plugin
 Automatiza el ploteo de medidas estructurales (Dip y Dip-Direction) desde Excel/CSV o ploteo manual.
                              -------------------
        begin                : 2026-09-16
        git sha              : $Format:%H$
        copyright            : (C) 2026 by Pablo Guzman H
        email                : pabloguzmanherr@gmail.com
 ***************************************************************************/
"""
import os
import os.path

from qgis.PyQt.QtCore import QLocale, QTranslator, QCoreApplication, QVariant, QMetaType
from qgis.PyQt.QtGui import QIcon, QColor, QPixmap
from qgis.PyQt.QtWidgets import (
    QAction, QFileDialog, QVBoxLayout, QFormLayout, QCheckBox, QDoubleSpinBox
)
from qgis.core import (
    QgsSettings, QgsProject, QgsVectorLayer, QgsFeature,
    QgsGeometry, QgsPointXY, QgsField, QgsVectorFileWriter,
    QgsMarkerSymbol, QgsSymbolLayer, QgsSingleSymbolRenderer,
    QgsProperty, QgsPalLayerSettings, QgsVectorLayerSimpleLabeling,
    QgsTextFormat, QgsSvgMarkerSymbolLayer, Qgis
)
from qgis.gui import QgsProjectionSelectionWidget, QgsColorButton

from .geo_dip_dialog import GeoDipDialog


class GeoDip:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        locale = QgsSettings().value('locale/userLocale', QLocale().name())[0:2]
        locale_path = os.path.join(self.plugin_dir, 'i18n', '{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        self.actions = []
        self.menu = self.tr(u'&GeoDip')
        self.first_start = None
        self.ruta_actual = None

    def tr(self, message):
        return QCoreApplication.translate('GeoDip', message)

    def add_action(
        self, icon_path, text, callback, enabled_flag=True,
        add_to_menu=True, add_to_toolbar=True, status_tip=None,
        whats_this=None, parent=None
    ):
        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)
        if whats_this is not None:
            action.setWhatsThis(whats_this)
        if add_to_toolbar:
            self.iface.addToolBarIcon(action)
        if add_to_menu:
            self.iface.addPluginToMenu(self.menu, action)

        self.actions.append(action)
        return action

    def initGui(self):
        icon_path = os.path.join(os.path.dirname(__file__), 'icon.png')
        self.add_action(
            icon_path,
            text=self.tr(u'GeoDip'),
            callback=self.run,
            parent=self.iface.mainWindow()
        )
        self.first_start = True

    def unload(self):
        for action in self.actions:
            self.iface.removePluginMenu(self.tr(u'&GeoDip'), action)
            self.iface.removeToolBarIcon(action)

    def run(self):
        if self.first_start is True:
            self.first_start = False
            self.dlg = GeoDipDialog()

            ruta_logo = os.path.join(self.plugin_dir, 'icon.png')
            if os.path.exists(ruta_logo) and hasattr(self.dlg, 'lbl_logo'):
                self.dlg.lbl_logo.setPixmap(QPixmap(ruta_logo))

            self.dlg.btn_cargar.clicked.connect(self.cargar_archivo)
            self.dlg.btn_plotear.clicked.connect(self.plotear_medidas)

            self.dlg.crs_selector = QgsProjectionSelectionWidget(self.dlg.contenedor_crs)

            layout = QVBoxLayout(self.dlg.contenedor_crs)
            layout.setContentsMargins(5, 5, 5, 5)
            layout.setSpacing(10)

            layout.addWidget(self.dlg.crs_selector)

            self.dlg.chk_atributos = QCheckBox("Keep all original columns (lithology, notes, etc.)")
            self.dlg.chk_atributos.setChecked(True)
            layout.addWidget(self.dlg.chk_atributos)

            # --- FORMULARIO DE ESTILOS (TAMAÑOS Y COLOR) ---
            layout_estilos = QFormLayout()

            # 1. Tamaño del SVG
            self.dlg.spin_tamano_simbolo = QDoubleSpinBox()
            self.dlg.spin_tamano_simbolo.setValue(10.0)
            self.dlg.spin_tamano_simbolo.setMinimum(1.0)
            self.dlg.spin_tamano_simbolo.setDecimals(1)
            self.dlg.spin_tamano_simbolo.setSingleStep(1.0)

            # 2. Tamaño del Texto
            self.dlg.spin_tamano_texto = QDoubleSpinBox()
            self.dlg.spin_tamano_texto.setValue(10.0)
            self.dlg.spin_tamano_texto.setMinimum(1.0)
            self.dlg.spin_tamano_texto.setDecimals(1)
            self.dlg.spin_tamano_texto.setSingleStep(1.0)

            # 3. Selector de Color (Nativo de QGIS)
            self.dlg.btn_color = QgsColorButton()
            self.dlg.btn_color.setColor(QColor("black"))
            self.dlg.btn_color.setWindowTitle("Select Symbol Color")
            self.dlg.btn_color.setAllowOpacity(True)

            layout_estilos.addRow("Symbol Size:", self.dlg.spin_tamano_simbolo)
            layout_estilos.addRow("Text Size:", self.dlg.spin_tamano_texto)
            layout_estilos.addRow("Symbol Color:", self.dlg.btn_color)

            layout.addLayout(layout_estilos)

            crs_actual = QgsProject.instance().crs()
            self.dlg.crs_selector.setCrs(crs_actual)

        self.dlg.show()
        # Compatible con PyQt5 y PyQt6 (se reemplaza exec_() por exec())
        result = self.dlg.exec()
        if result:
            pass

    def _crear_campo_doble(self, nombre):
        """Crea un QgsField tipo Double compatible con QGIS 3 (QVariant) y QGIS 4 (QMetaType)."""
        try:
            return QgsField(nombre, QMetaType.Type.Double, "double")
        except TypeError:
            return QgsField(nombre, getattr(QVariant, "Double"), "double")

    def _autodetectar_columnas(self, columnas):
        """Detecta y selecciona automáticamente las columnas X, Y, Dip y Dip-Direction."""
        patrones = {
            self.dlg.combo_dip_dir: [
                'dip_direction', 'dipdirection', 'dip_dir', 'dipdir', 'ddir', 'dd',
                'azimuth', 'azimut', 'direccion', 'direction', 'rumbo', 'strike', 'dir'
            ],
            self.dlg.combo_dip: [
                'dip', 'buzamiento', 'buz', 'inclinacion', 'inclination', 'angulo', 'angle', 'plunge'
            ],
            self.dlg.combo_x: [
                'x', 'este', 'east', 'easting', 'este_x', 'coord_x', 'x_coord',
                'utm_x', 'utmx', 'utm_e', 'lon', 'long', 'longitude', 'longitud', 'e'
            ],
            self.dlg.combo_y: [
                'y', 'norte', 'north', 'northing', 'norte_y', 'coord_y', 'y_coord',
                'utm_y', 'utmy', 'utm_n', 'lat', 'latitude', 'latitud', 'n'
            ]
        }

        columnas_limpias = [
            c.strip().lower().replace(' ', '_').replace('-', '_') for c in columnas
        ]
        usados = set()

        for combo, claves in patrones.items():
            encontrado = None
            # 1ra pasada: Coincidencia exacta
            for clave in claves:
                for idx, col_norm in enumerate(columnas_limpias):
                    if idx not in usados and col_norm == clave:
                        encontrado = idx
                        break
                if encontrado is not None:
                    break

            # 2da pasada: Coincidencia parcial (si contiene la palabra clave)
            if encontrado is None:
                for clave in claves:
                    if len(clave) < 2:
                        continue
                    for idx, col_norm in enumerate(columnas_limpias):
                        if idx not in usados and clave in col_norm:
                            encontrado = idx
                            break
                    if encontrado is not None:
                        break

            if encontrado is not None:
                combo.setCurrentIndex(encontrado)
                usados.add(encontrado)

    def cargar_archivo(self):
        ruta_archivo, _ = QFileDialog.getOpenFileName(
            self.dlg,
            "Select structural measurements file",
            "",
            "Data files (*.csv *.xlsx *.xls);;All files (*)"
        )

        if ruta_archivo:
            self.ruta_actual = ruta_archivo
            self.dlg.btn_cargar.setText(f"Loaded: {os.path.basename(ruta_archivo)}")

            capa_datos = QgsVectorLayer(self.ruta_actual, "datos_temporales", "ogr")
            if not capa_datos.isValid():
                self.iface.messageBar().pushMessage(
                    "Read Error",
                    "Cannot read the file. Please try saving it as .csv",
                    level=Qgis.MessageLevel.Critical
                )
                return

            columnas = [campo.name() for campo in capa_datos.fields()]

            self.dlg.combo_x.clear()
            self.dlg.combo_y.clear()
            self.dlg.combo_dip.clear()
            self.dlg.combo_dip_dir.clear()

            self.dlg.combo_x.addItems(columnas)
            self.dlg.combo_y.addItems(columnas)
            self.dlg.combo_dip.addItems(columnas)
            self.dlg.combo_dip_dir.addItems(columnas)

            # Autodetectar columnas según sus nombres
            self._autodetectar_columnas(columnas)

    def plotear_medidas(self):
        if not hasattr(self, 'ruta_actual') or not self.ruta_actual:
            self.iface.messageBar().pushMessage(
                "Warning",
                "Please load an Excel or CSV file first.",
                level=Qgis.MessageLevel.Warning
            )
            return

        # El usuario elige entre GeoPackage (.gpkg) o Shapefile (.shp) al guardar
        ruta_salida, filtro_elegido = QFileDialog.getSaveFileName(
            self.dlg,
            "Save point layer as...",
            "",
            "GeoPackage (*.gpkg);;ESRI Shapefile (*.shp)"
        )

        if not ruta_salida:
            return

        # Determinar formato y extensión según la elección del usuario
        if ruta_salida.lower().endswith('.shp') or (
            '*.shp' in filtro_elegido and not ruta_salida.lower().endswith('.gpkg')
        ):
            es_gpkg = False
            if not ruta_salida.lower().endswith('.shp'):
                ruta_salida += '.shp'
            driver_ogr = "ESRI Shapefile"
        else:
            es_gpkg = True
            if not ruta_salida.lower().endswith('.gpkg'):
                ruta_salida += '.gpkg'
            driver_ogr = "GPKG"

        try:
            capa_datos = QgsVectorLayer(self.ruta_actual, "datos_temporales", "ogr")
            if not capa_datos.isValid():
                self.iface.messageBar().pushMessage(
                    "Read Error",
                    "Cannot open the file. Ensure it is not being used by another program.",
                    level=Qgis.MessageLevel.Critical
                )
                return

            col_x = self.dlg.combo_x.currentText()
            col_y = self.dlg.combo_y.currentText()
            col_dip = self.dlg.combo_dip.currentText()
            col_dip_dir = self.dlg.combo_dip_dir.currentText()

            epsg = self.dlg.crs_selector.crs().authid()
            mantener_atributos = self.dlg.chk_atributos.isChecked()

            tamano_simbolo = self.dlg.spin_tamano_simbolo.value()
            tamano_texto = self.dlg.spin_tamano_texto.value()
            color_elegido = self.dlg.btn_color.color()

            uri = f"Point?crs={epsg}"
            capa_temp = QgsVectorLayer(uri, "temp", "memory")
            proveedor = capa_temp.dataProvider()

            campos = [
                self._crear_campo_doble("Dip"),
                self._crear_campo_doble("Dip_Dir")
            ]

            columnas_extra = []
            if mantener_atributos:
                for campo in capa_datos.fields():
                    col_str = campo.name()
                    if col_str not in [col_dip, col_dip_dir]:
                        columnas_extra.append(col_str)
                        campo_copia = QgsField(campo)
                        # En GeoPackage 'fid' es un nombre reservado para la clave primaria
                        if es_gpkg and col_str.lower() == 'fid':
                            campo_copia.setName('fid_orig')
                        campos.append(campo_copia)

            proveedor.addAttributes(campos)
            capa_temp.updateFields()

            features = []
            for feat_origen in capa_datos.getFeatures():
                try:
                    x = float(str(feat_origen[col_x]).replace(',', '.'))
                    y = float(str(feat_origen[col_y]).replace(',', '.'))
                except (ValueError, TypeError):
                    continue

                feat_nueva = QgsFeature()
                feat_nueva.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(x, y)))

                try:
                    val_dip = float(str(feat_origen[col_dip]).replace(',', '.'))
                except (ValueError, TypeError):
                    val_dip = 0.0

                try:
                    val_dip_dir = float(str(feat_origen[col_dip_dir]).replace(',', '.'))
                except (ValueError, TypeError):
                    val_dip_dir = 0.0

                atributos = [val_dip, val_dip_dir]

                for col in columnas_extra:
                    val = feat_origen[col]
                    atributos.append(val)

                feat_nueva.setAttributes(atributos)
                features.append(feat_nueva)

            proveedor.addFeatures(features)

            nombre_capa = os.path.splitext(os.path.basename(ruta_salida))[0]

            opciones = QgsVectorFileWriter.SaveVectorOptions()
            opciones.driverName = driver_ogr
            opciones.fileEncoding = "UTF-8"
            if es_gpkg:
                opciones.layerName = nombre_capa

            resultado_guardado = QgsVectorFileWriter.writeAsVectorFormatV3(
                capa_temp, ruta_salida, QgsProject.instance().transformContext(), opciones
            )
            error = resultado_guardado[0]

            if error == QgsVectorFileWriter.WriterError.NoError:
                capa_final = QgsVectorLayer(ruta_salida, nombre_capa, "ogr")

                ruta_svg = os.path.join(self.plugin_dir, 'simbolo_buzamiento.svg')
                rotacion = QgsProperty.fromField("Dip_Dir")

                if os.path.exists(ruta_svg):
                    simbolo = QgsMarkerSymbol.createSimple({
                        'name': 'circle',
                        'color': color_elegido.name()
                    })
                    svg_layer = QgsSvgMarkerSymbolLayer(ruta_svg)

                    svg_layer.setSize(tamano_simbolo)
                    svg_layer.setStrokeWidth(0.6)
                    svg_layer.setFillColor(color_elegido)
                    svg_layer.setStrokeColor(color_elegido)

                    svg_layer.setDataDefinedProperty(
                        QgsSymbolLayer.Property.PropertyAngle, rotacion
                    )
                    simbolo.changeSymbolLayer(0, svg_layer)
                else:
                    simbolo = QgsMarkerSymbol.createSimple({
                        'name': 'arrow',
                        'color': color_elegido.name(),
                        'size': str(tamano_simbolo)
                    })
                    capa_simbolo = simbolo.symbolLayer(0)
                    capa_simbolo.setDataDefinedProperty(
                        QgsSymbolLayer.Property.PropertyAngle, rotacion
                    )

                renderizador = QgsSingleSymbolRenderer(simbolo)
                capa_final.setRenderer(renderizador)

                formato_texto = QgsTextFormat()
                formato_texto.setSize(tamano_texto)
                formato_texto.setColor(QColor("black"))

                config_etiqueta = QgsPalLayerSettings()
                config_etiqueta.fieldName = "Dip"
                config_etiqueta.setFormat(formato_texto)

                config_etiqueta.placement = Qgis.LabelPlacement.AroundPoint
                config_etiqueta.dist = tamano_simbolo * 0.2

                expresion_cuadrante = """
                CASE
                    WHEN "Dip_Dir" >= 337.5 OR "Dip_Dir" < 22.5 THEN 1
                    WHEN "Dip_Dir" >= 22.5 AND "Dip_Dir" < 67.5 THEN 2
                    WHEN "Dip_Dir" >= 67.5 AND "Dip_Dir" < 112.5 THEN 5
                    WHEN "Dip_Dir" >= 112.5 AND "Dip_Dir" < 157.5 THEN 8
                    WHEN "Dip_Dir" >= 157.5 AND "Dip_Dir" < 202.5 THEN 7
                    WHEN "Dip_Dir" >= 202.5 AND "Dip_Dir" < 247.5 THEN 6
                    WHEN "Dip_Dir" >= 247.5 AND "Dip_Dir" < 292.5 THEN 3
                    WHEN "Dip_Dir" >= 292.5 AND "Dip_Dir" < 337.5 THEN 0
                END
                """
                propiedad_cuadrante = QgsProperty.fromExpression(expresion_cuadrante)

                config_etiqueta.dataDefinedProperties().setProperty(
                    QgsPalLayerSettings.Property.OffsetQuad, propiedad_cuadrante
                )

                capa_final.setLabelsEnabled(True)
                capa_final.setLabeling(QgsVectorLayerSimpleLabeling(config_etiqueta))

                # Si es GeoPackage, guardamos el estilo directamente dentro del archivo .gpkg
                if es_gpkg:
                    capa_final.saveStyleToDatabase(
                        nombre_capa,
                        "GeoDip default structural style",
                        True,
                        ""
                    )

                QgsProject.instance().addMapLayer(capa_final)
                self.dlg.close()
                self.iface.messageBar().pushMessage(
                    "GeoDip",
                    "Measurements processed and styled successfully.",
                    level=Qgis.MessageLevel.Success
                )

            else:
                self.iface.messageBar().pushMessage(
                    "Error",
                    f"Could not save the layer. Error Code: {error}",
                    level=Qgis.MessageLevel.Critical
                )

        except Exception as e:
            self.iface.messageBar().pushMessage(
                "Python Error",
                f"Failed to process data: {str(e)}",
                level=Qgis.MessageLevel.Critical
            )