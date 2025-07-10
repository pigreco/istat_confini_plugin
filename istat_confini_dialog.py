# -*- coding: utf-8 -*-
"""
/***************************************************************************
 IstatConfiniDialog
                                 A QGIS plugin
 Plugin per scaricare i confini amministrativi ISTAT
                             -------------------
        begin                : 2025-01-01
        git sha              : $Format:%H$
        copyright            : (C) 2025
        email                : tua@email.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import os
from qgis.PyQt import QtCore, QtGui, QtWidgets
from qgis.PyQt.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QRadioButton, 
                                QCheckBox, QPushButton, QLabel, QButtonGroup, 
                                QLineEdit, QFileDialog, QGroupBox, QTabWidget)


class IstatConfiniDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setupUi()

    def setupUi(self):
        """Imposta l'interfaccia utente della finestra di dialogo"""
        self.setObjectName("IstatConfiniDialog")
        self.resize(450, 450)  # Aumentata l'altezza per le tab
        self.setWindowTitle("Scarica Confini Amministrativi ISTAT")
        self.setModal(True)
        
        # Layout principale
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Titolo
        title_label = QLabel("Seleziona i confini amministrativi da scaricare")
        title_label.setStyleSheet("""
            font-weight: bold; 
            font-size: 16px; 
            color: #2c3e50;
            margin-bottom: 10px;
            padding-bottom: 10px;
            border-bottom: 2px solid #3498db;
        """)
        main_layout.addWidget(title_label)
        
        # Widget a tab
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #dee2e6;
                border-radius: 8px;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #f8f9fa;
                padding: 8px 16px;
                margin-right: 2px;
                border: 1px solid #dee2e6;
                border-bottom: none;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom: 1px solid white;
            }
            QTabBar::tab:hover {
                background-color: #e9ecef;
            }
        """)
        
        # Tab principale
        main_tab = QtWidgets.QWidget()
        main_tab_layout = QVBoxLayout()
        main_tab_layout.setSpacing(15)
        main_tab_layout.setContentsMargins(15, 15, 15, 15)
        
        # Sezione tipo di confine
        boundary_label = QLabel("🗺️ Tipo di confine amministrativo:")
        boundary_label.setStyleSheet("font-weight: bold; font-size: 14px; margin-top: 10px; color: #34495e;")
        main_tab_layout.addWidget(boundary_label)
        
        # Contenitore per i radio buttons dei confini
        boundary_container = QtWidgets.QFrame()
        boundary_container.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        boundary_layout = QVBoxLayout()
        boundary_layout.setSpacing(8)
        
        # Radio buttons per i tipi di confine
        self.boundary_group = QButtonGroup()
        
        self.radio_regioni = QRadioButton("🏛️  Regioni")
        self.radio_province = QRadioButton("🏢  Province e Città metropolitane")
        self.radio_comuni = QRadioButton("🏘️  Comuni")
        self.radio_ripartizioni = QRadioButton("📍  Ripartizioni geografiche")
        
        # Stile per i radio buttons
        radio_style = """
            QRadioButton {
                font-size: 13px;
                padding: 5px;
                color: #495057;
            }
            QRadioButton::indicator {
                width: 18px;
                height: 18px;
            }
            QRadioButton::indicator:checked {
                background-color: #3498db;
                border: 2px solid #2980b9;
                border-radius: 9px;
            }
            QRadioButton::indicator:unchecked {
                background-color: white;
                border: 2px solid #bdc3c7;
                border-radius: 9px;
            }
        """
        
        for radio in [self.radio_regioni, self.radio_province, self.radio_comuni, self.radio_ripartizioni]:
            radio.setStyleSheet(radio_style)
            self.boundary_group.addButton(radio)
            boundary_layout.addWidget(radio)
        
        # Seleziona regioni di default
        self.radio_regioni.setChecked(True)
        
        boundary_container.setLayout(boundary_layout)
        main_tab_layout.addWidget(boundary_container)
        
        # Sezione generalizzazione
        generalization_label = QLabel("⚙️ Livello di dettaglio:")
        generalization_label.setStyleSheet("font-weight: bold; font-size: 14px; margin-top: 15px; color: #34495e;")
        main_tab_layout.addWidget(generalization_label)
        
        # Contenitore per la generalizzazione
        gen_container = QtWidgets.QFrame()
        gen_container.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        gen_layout = QVBoxLayout()
        gen_layout.setSpacing(8)
        
        self.generalization_group = QButtonGroup()
        
        self.radio_generalizzata = QRadioButton("📦  Versione generalizzata (file più leggero, meno dettaglio)")
        self.radio_non_generalizzata = QRadioButton("🔍  Versione non generalizzata (dettaglio completo, file più pesante)")
        
        for radio in [self.radio_generalizzata, self.radio_non_generalizzata]:
            radio.setStyleSheet(radio_style)
            self.generalization_group.addButton(radio)
            gen_layout.addWidget(radio)
        
        # Seleziona generalizzata di default
        self.radio_generalizzata.setChecked(True)
        
        gen_container.setLayout(gen_layout)
        main_tab_layout.addWidget(gen_container)
        
        # Sezione cartella di output
        output_label = QLabel("📁 Cartella di destinazione:")
        output_label.setStyleSheet("font-weight: bold; font-size: 14px; margin-top: 15px; color: #34495e;")
        main_tab_layout.addWidget(output_label)
        
        # Contenitore per la selezione cartella
        output_container = QtWidgets.QFrame()
        output_container.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        output_layout = QHBoxLayout()
        output_layout.setSpacing(8)
        
        self.output_path_edit = QLineEdit()
        self.output_path_edit.setPlaceholderText("Seleziona una cartella dove salvare i file...")
        self.output_path_edit.setText(os.path.expanduser("~/Desktop"))  # Default: Desktop
        self.output_path_edit.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #ced4da;
                border-radius: 4px;
                font-size: 12px;
            }
        """)
        
        self.browse_button = QPushButton("Sfoglia...")
        self.browse_button.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 4px;
                font-weight: bold;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)
        self.browse_button.clicked.connect(self.browse_output_folder)
        
        output_layout.addWidget(self.output_path_edit)
        output_layout.addWidget(self.browse_button)
        
        output_container.setLayout(output_layout)
        main_tab_layout.addWidget(output_container)
        
        main_tab.setLayout(main_tab_layout)
        self.tab_widget.addTab(main_tab, "📋 Principale")
        
        # Tab opzioni avanzate e info
        advanced_tab = QtWidgets.QWidget()
        advanced_tab_layout = QVBoxLayout()
        advanced_tab_layout.setSpacing(15)
        advanced_tab_layout.setContentsMargins(15, 15, 15, 15)
        
        # Opzioni avanzate
        options_label = QLabel("⚙️ Opzioni avanzate:")
        options_label.setStyleSheet("font-weight: bold; font-size: 14px; margin-top: 10px; color: #34495e;")
        advanced_tab_layout.addWidget(options_label)
        
        options_container = QtWidgets.QFrame()
        options_container.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        options_layout = QVBoxLayout()
        options_layout.setSpacing(8)
        
        self.keep_files_checkbox = QCheckBox("🗃️  Mantieni i file scaricati dopo il caricamento")
        self.keep_files_checkbox.setStyleSheet("""
            QCheckBox {
                font-size: 13px;
                padding: 5px;
                color: #495057;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
            }
            QCheckBox::indicator:checked {
                background-color: #28a745;
                border: 2px solid #1e7e34;
                border-radius: 3px;
            }
            QCheckBox::indicator:unchecked {
                background-color: white;
                border: 2px solid #bdc3c7;
                border-radius: 3px;
            }
        """)
        self.keep_files_checkbox.setChecked(True)
        
        self.open_folder_checkbox = QCheckBox("📂  Apri la cartella di destinazione al termine")
        self.open_folder_checkbox.setStyleSheet(self.keep_files_checkbox.styleSheet())
        self.open_folder_checkbox.setChecked(False)
        
        options_layout.addWidget(self.keep_files_checkbox)
        options_layout.addWidget(self.open_folder_checkbox)
        
        options_container.setLayout(options_layout)
        advanced_tab_layout.addWidget(options_container)
        
        # Sezione informazioni
        info_label = QLabel("ℹ️ Informazioni:")
        info_label.setStyleSheet("font-weight: bold; font-size: 14px; margin-top: 15px; color: #34495e;")
        advanced_tab_layout.addWidget(info_label)
        
        info_container = QtWidgets.QFrame()
        info_container.setStyleSheet("""
            QFrame {
                background-color: #e8f4fd;
                border: 1px solid #bee5eb;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        info_layout = QVBoxLayout()
        info_layout.setSpacing(10)
        
        info_text = QLabel("""
📊 <b>Fonte dati:</b> Istituto Nazionale di Statistica (ISTAT)<br>
🗓️ <b>Aggiornamento:</b> Dati più recenti disponibili<br>
🌍 <b>Sistema di riferimento:</b> WGS84 / UTM zone 32N (EPSG:32632)<br>
📁 <b>Formato:</b> Shapefile (.shp)<br>
⚖️ <b>Licenza:</b> Creative Commons Attribution 3.0 IT<br><br>
<i>I dati sono forniti dall'ISTAT e sono utilizzabili secondo i termini della licenza CC BY 3.0 IT.</i>
        """)
        info_text.setWordWrap(True)
        info_text.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #495057;
                line-height: 1.4;
            }
        """)
        
        info_layout.addWidget(info_text)
        info_container.setLayout(info_layout)
        advanced_tab_layout.addWidget(info_container)
        
        # Aggiunge spazio flessibile alla fine
        advanced_tab_layout.addStretch()
        
        advanced_tab.setLayout(advanced_tab_layout)
        self.tab_widget.addTab(advanced_tab, "⚙️ Avanzate & Info")
        
        main_layout.addWidget(self.tab_widget)
        
        # Bottoni OK e Cancel
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        self.button_box = QtWidgets.QDialogButtonBox()
        self.button_box.setOrientation(QtCore.Qt.Horizontal)
        self.button_box.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Ok)
        
        # Stile per i bottoni
        self.button_box.setStyleSheet("""
            QPushButton {
                font-size: 13px;
                font-weight: bold;
                padding: 8px 20px;
                border-radius: 6px;
                min-width: 80px;
            }
            QPushButton[text="OK"] {
                background-color: #3498db;
                color: white;
                border: 2px solid #2980b9;
            }
            QPushButton[text="OK"]:hover {
                background-color: #2980b9;
            }
            QPushButton[text="Cancel"] {
                background-color: #95a5a6;
                color: white;
                border: 2px solid #7f8c8d;
            }
            QPushButton[text="Cancel"]:hover {
                background-color: #7f8c8d;
            }
        """)
        
        button_layout.addWidget(self.button_box)
        main_layout.addLayout(button_layout)
        
        self.setLayout(main_layout)
        
        # Connetti i segnali
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
    
    def browse_output_folder(self):
        """Apre la finestra di dialogo per selezionare la cartella di output"""
        folder = QFileDialog.getExistingDirectory(
            self, 
            "Seleziona cartella di destinazione",
            self.output_path_edit.text()
        )
        if folder:
            self.output_path_edit.setText(folder)

    def get_selected_boundary(self):
        """Restituisce il tipo di confine selezionato"""
        if self.radio_regioni.isChecked():
            return "regioni"
        elif self.radio_province.isChecked():
            return "province"
        elif self.radio_comuni.isChecked():
            return "comuni"
        elif self.radio_ripartizioni.isChecked():
            return "ripartizioni"
        return None
    
    def get_output_path(self):
        """Restituisce la cartella di output selezionata"""
        return self.output_path_edit.text()
    
    def should_keep_files(self):
        """Restituisce True se i file devono essere mantenuti"""
        return self.keep_files_checkbox.isChecked()
    
    def should_open_folder(self):
        """Restituisce True se la cartella deve essere aperta al termine"""
        return self.open_folder_checkbox.isChecked()