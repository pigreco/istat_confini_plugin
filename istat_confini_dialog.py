# -*- coding: utf-8 -*-
"""
/***************************************************************************
 IstatConfiniDialog
                                 A QGIS plugin
 Plugin per scaricare i confini amministrativi ISTAT e griglia km popolazione 2021
                             -------------------
        begin                : 2025-01-01
        git sha              : $Format:%H$
        copyright            : (C) 2025
        email                : pigrecoinfinito@gmail.com
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
        self.resize(520, 480)  # Larghezza aumentata per migliori proporzioni
        self.setWindowTitle("Scarica Dati ISTAT")
        self.setModal(True)
        
        # Layout principale
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Titolo
        title_label = QLabel("Seleziona i dati ISTAT da scaricare (confini e griglia popolazione 2021)")
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
        boundary_label = QLabel("🗺️ Tipo di confine amministrativo (opzionale):")
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
        
        self.radio_nessuno = QRadioButton("❌  Nessun confine (solo dati aggiuntivi)")
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
        
        for radio in [self.radio_nessuno, self.radio_regioni, self.radio_province, self.radio_comuni, self.radio_ripartizioni]:
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
        self.tab_widget.addTab(main_tab, "�️ Confini Amministrativi")
        
        # Aggiungi nota informativa
        info_note = QLabel("💡 Puoi scaricare solo confini amministrativi, solo dati aggiuntivi (griglia popolazione), o entrambi contemporaneamente.")
        info_note.setStyleSheet("""
            QLabel {
                font-size: 11px;
                color: #6c757d;
                font-style: italic;
                margin-top: 5px;
                padding: 8px;
                background-color: #f8f9fa;
                border-left: 3px solid #17a2b8;
                border-radius: 4px;
            }
        """)
        info_note.setWordWrap(True)
        main_tab_layout.insertWidget(0, info_note)  # Inserisci all'inizio del layout
        
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
        
        self.keep_files_checkbox = QCheckBox("🗃️  Mantieni i file scaricati dopo il caricamento (altrimenti alla chiusura perdi i file)")
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
        
        self.delete_zip_checkbox = QCheckBox("🗑️  Elimina i file ZIP dopo l'estrazione (conserva solo i file estratti)")
        self.delete_zip_checkbox.setStyleSheet(self.keep_files_checkbox.styleSheet())
        self.delete_zip_checkbox.setChecked(True)
        
        options_layout.addWidget(self.keep_files_checkbox)
        options_layout.addWidget(self.open_folder_checkbox)
        options_layout.addWidget(self.delete_zip_checkbox)
        
        options_container.setLayout(options_layout)
        advanced_tab_layout.addWidget(options_container)
        
        # Nota per l'opzione elimina ZIP
        zip_note = QLabel("💡 Nota: Se elimini i file ZIP, conservi solo i dati estratti (shapefile e file associati). Utile per risparmiare spazio su disco.")
        zip_note.setStyleSheet("""
            QLabel {
                font-size: 11px;
                color: #6c757d;
                font-style: italic;
                margin: 5px 0px;
                padding: 6px;
                background-color: #e3f2fd;
                border-left: 3px solid #2196f3;
                border-radius: 4px;
            }
        """)
        zip_note.setWordWrap(True)
        advanced_tab_layout.addWidget(zip_note)
        
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
⚖️ <b>Licenza:</b> Creative Commons Attribution 3.0 IT<br>
📖 <b>Info confini:</b> <a href="https://www.istat.it/notizia/confini-delle-unita-amministrative-a-fini-statistici-al-1-gennaio-2018-2/">Confini delle unità amministrative a fini statistici</a><br><br>
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
        self.tab_widget.addTab(advanced_tab, "⚙️ Avanzate e Info")
        
        # Tab dati aggiuntivi
        additional_data_tab = QtWidgets.QWidget()
        additional_data_layout = QVBoxLayout()
        additional_data_layout.setSpacing(15)
        additional_data_layout.setContentsMargins(15, 15, 15, 15)
        
        # Sezione griglia popolazione
        griglia_label = QLabel("📊 Dati aggiuntivi disponibili:")
        griglia_label.setStyleSheet("font-weight: bold; font-size: 14px; margin-top: 10px; color: #34495e;")
        additional_data_layout.addWidget(griglia_label)
        
        griglia_container = QtWidgets.QFrame()
        griglia_container.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        griglia_layout = QVBoxLayout()
        griglia_layout.setSpacing(10)
        
        # Checkbox per la griglia popolazione
        self.griglia_pop_checkbox = QCheckBox("📊  Griglia di popolazione 2021 - Censimento (1 km²)")
        self.griglia_pop_checkbox.setStyleSheet("""
            QCheckBox {
                font-size: 13px;
                font-weight: bold;
                padding: 8px;
                color: #2c3e50;
            }
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
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
        self.griglia_pop_checkbox.setChecked(False)
        
        # Descrizione dettagliata
        griglia_description = QLabel("""
<b>Descrizione:</b><br>
Distribuzione della popolazione legale del Censimento 2021 su griglia regolare europea (Eurostat) con celle di 1 km².<br><br>
<b>Variabili censuarie disponibili (Reg. UE 1799/2018):</b><br>
• Popolazione totale, maschile e femminile<br>
• Popolazione per fasce di età (0-14, 15-64, oltre 65 anni)<br>
• Popolazione per luogo di nascita (Italia, altro paese EU, extra-EU)<br>
• Occupati<br>
• Mobilità residenziale (stessa/altra dimora un anno prima)<br><br>
<b>Caratteristiche della griglia:</b><br>
• Celle uniformi facilmente confrontabili<br>
• Griglia stabile nel tempo e compatibile con standard europei<br>
• Aggregazione/suddivisione indipendente dai confini amministrativi<br><br>
<b>Formato:</b> Shapefile in sistema di riferimento ETRS89 / LAEA Europe [EPSG:3035]<br>
<b>Dimensione:</b> ~12 MB (compresso), ~250 MB (estratto)<br><br>
<b>📖 Info:</b> <a href="https://www.istat.it/notizia/statistiche-sulla-popolazione-per-griglia-regolare/">Statistiche popolazione per griglia regolare</a><br>
<b>📄 Metodologia:</b> <a href="https://www.istat.it/wp-content/uploads/2023/07/NotaMetodologicaGriglia2021-Ind.pdf">Nota metodologica (PDF)</a>
        """)
        griglia_description.setWordWrap(True)
        griglia_description.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #495057;
                line-height: 1.4;
                background-color: #e8f4fd;
                border: 1px solid #bee5eb;
                border-radius: 6px;
                padding: 12px;
            }
        """)
        
        griglia_layout.addWidget(self.griglia_pop_checkbox)
        griglia_layout.addWidget(griglia_description)
        
        griglia_container.setLayout(griglia_layout)
        additional_data_layout.addWidget(griglia_container)
        
        # Note importanti
        note_label = QLabel("⚠️ Note importanti:")
        note_label.setStyleSheet("font-weight: bold; font-size: 14px; margin-top: 15px; color: #e74c3c;")
        additional_data_layout.addWidget(note_label)
        
        note_container = QtWidgets.QFrame()
        note_container.setStyleSheet("""
            QFrame {
                background-color: #fef9e7;
                border: 1px solid #f6e05e;
                border-radius: 8px;
                padding: 12px;
            }
        """)
        note_layout = QVBoxLayout()
        
        note_text = QLabel("""
• La griglia di popolazione è un dataset separato dai confini amministrativi<br>
• Il download avverrà solo se questa opzione è selezionata<br>
• Il file verrà salvato nella stessa cartella di destinazione scelta nel tab principale<br>
• È possibile scaricare sia i confini amministrativi che la griglia popolazione contemporaneamente
        """)
        note_text.setWordWrap(True)
        note_text.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #8b5a2b;
                line-height: 1.4;
            }
        """)
        
        note_layout.addWidget(note_text)
        note_container.setLayout(note_layout)
        additional_data_layout.addWidget(note_container)
        
        # Aggiunge spazio flessibile alla fine
        additional_data_layout.addStretch()
        
        additional_data_tab.setLayout(additional_data_layout)
        self.tab_widget.addTab(additional_data_tab, "📊 Griglia di popolazione 2021")
        
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
        
        # Connetti segnale per aggiornare UI quando cambia selezione confine
        self.radio_nessuno.toggled.connect(self.update_boundary_ui)
    
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
        if self.radio_nessuno.isChecked():
            return None
        elif self.radio_regioni.isChecked():
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
    
    def should_download_griglia_pop(self):
        """Restituisce True se la griglia popolazione deve essere scaricata"""
        return self.griglia_pop_checkbox.isChecked()
    
    def should_delete_zip(self):
        """Restituisce True se i file ZIP devono essere eliminati dopo l'estrazione"""
        return self.delete_zip_checkbox.isChecked()
    
    def update_boundary_ui(self):
        """Aggiorna l'interfaccia quando cambia la selezione del confine"""
        is_no_boundary = self.radio_nessuno.isChecked()
        
        # Disabilita le opzioni di generalizzazione se non è selezionato nessun confine
        self.radio_generalizzata.setEnabled(not is_no_boundary)
        self.radio_non_generalizzata.setEnabled(not is_no_boundary)
        
        # Se non è selezionato nessun confine, suggerisci di selezionare la griglia
        if is_no_boundary and not self.griglia_pop_checkbox.isChecked():
            # Mostra un suggerimento visivo (cambia lo stile del tab)
            self.tab_widget.setTabText(2, "📊 Griglia di popolazione 2021 ⚠️")
        else:
            self.tab_widget.setTabText(2, "📊 Griglia di popolazione 2021")