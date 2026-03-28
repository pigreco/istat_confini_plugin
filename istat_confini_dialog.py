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

# ---------------------------------------------------------------------------
# Costanti di compatibilità Qt5/Qt6 (PyQt5 / PyQt6)
# ---------------------------------------------------------------------------
try:
    _HORIZONTAL = QtCore.Qt.Orientation.Horizontal
except AttributeError:
    _HORIZONTAL = QtCore.Qt.Horizontal  # type: ignore[attr-defined]

try:
    _BTN_OK_CANCEL = (QtWidgets.QDialogButtonBox.StandardButton.Cancel
                      | QtWidgets.QDialogButtonBox.StandardButton.Ok)
except AttributeError:
    _BTN_OK_CANCEL = (QtWidgets.QDialogButtonBox.Cancel  # type: ignore[attr-defined]
                      | QtWidgets.QDialogButtonBox.Ok)    # type: ignore[attr-defined]
# ---------------------------------------------------------------------------

# Stili tema-neutri: solo struttura (padding, border-radius, font).
# Nessun background-color / color hardcoded: eredita dalla palette del tema.
_STYLE_FRAME = """
    QFrame {
        border: 1px solid palette(mid);
        border-radius: 8px;
        padding: 6px;
    }
"""
_STYLE_FRAME_ACCENT = """
    QFrame {
        border: 1px solid palette(mid);
        border-radius: 8px;
        padding: 10px;
    }
"""
_STYLE_LABEL_SECTION = "font-weight: bold; font-size: 14px; margin-top: 10px;"
_STYLE_LABEL_TITLE = "font-weight: bold; font-size: 15px; padding-bottom: 8px; border-bottom: 2px solid palette(highlight);"
_STYLE_RADIO = "QRadioButton { font-size: 13px; padding: 4px; }"
_STYLE_CHECKBOX = "QCheckBox { font-size: 13px; padding: 4px; }"
_STYLE_NOTE = """
    QLabel {
        font-size: 11px;
        font-style: italic;
        padding: 6px 8px;
        border-left: 3px solid palette(highlight);
        border-radius: 3px;
    }
"""
_STYLE_NOTE_WARNING = """
    QLabel {
        font-size: 11px;
        font-style: italic;
        padding: 6px 8px;
        border-left: 3px solid palette(mid);
        border-radius: 3px;
    }
"""
_STYLE_LINEEDIT = "QLineEdit { padding: 6px; border: 1px solid palette(mid); border-radius: 4px; font-size: 12px; }"


class IstatConfiniDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setupUi()

    def setupUi(self):
        """Imposta l'interfaccia utente della finestra di dialogo"""
        self.setObjectName("IstatConfiniDialog")
        self.resize(520, 500)
        self.setWindowTitle("Scarica Dati ISTAT")
        self.setModal(True)

        main_layout = QVBoxLayout()
        main_layout.setSpacing(12)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Titolo
        title_label = QLabel("Seleziona i dati ISTAT da scaricare (confini e griglia popolazione 2021)")
        title_label.setStyleSheet(_STYLE_LABEL_TITLE)
        title_label.setWordWrap(True)
        main_layout.addWidget(title_label)

        # Widget a tab — solo struttura, nessun colore fisso
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid palette(mid);
                border-radius: 6px;
            }
            QTabBar::tab {
                padding: 7px 14px;
                margin-right: 2px;
                border: 1px solid palette(mid);
                border-bottom: none;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
            }
            QTabBar::tab:selected {
                border-bottom: 1px solid palette(window);
                font-weight: bold;
            }
        """)

        # ── TAB 1: Confini Amministrativi ──────────────────────────────────
        main_tab = QtWidgets.QWidget()
        main_tab_layout = QVBoxLayout()
        main_tab_layout.setSpacing(12)
        main_tab_layout.setContentsMargins(15, 15, 15, 15)

        # Nota informativa in cima
        info_note = QLabel("💡 Puoi scaricare solo confini amministrativi, solo dati aggiuntivi "
                           "(griglia popolazione), o entrambi contemporaneamente.")
        info_note.setStyleSheet(_STYLE_NOTE)
        info_note.setWordWrap(True)
        main_tab_layout.addWidget(info_note)

        # Sezione tipo di confine
        boundary_label = QLabel("🗺️ Tipo di confine amministrativo (opzionale):")
        boundary_label.setStyleSheet(_STYLE_LABEL_SECTION)
        main_tab_layout.addWidget(boundary_label)

        boundary_container = QtWidgets.QFrame()
        boundary_container.setStyleSheet(_STYLE_FRAME)
        boundary_layout = QVBoxLayout()
        boundary_layout.setSpacing(6)

        self.boundary_group = QButtonGroup()
        self.radio_nessuno    = QRadioButton("❌  Nessun confine (solo dati aggiuntivi)")
        self.radio_regioni    = QRadioButton("🏛️  Regioni")
        self.radio_province   = QRadioButton("🏢  Province e Città metropolitane")
        self.radio_comuni     = QRadioButton("🏘️  Comuni")
        self.radio_ripartizioni = QRadioButton("📍  Ripartizioni geografiche")

        for radio in [self.radio_nessuno, self.radio_regioni, self.radio_province,
                      self.radio_comuni, self.radio_ripartizioni]:
            radio.setStyleSheet(_STYLE_RADIO)
            self.boundary_group.addButton(radio)
            boundary_layout.addWidget(radio)

        self.radio_regioni.setChecked(True)
        boundary_container.setLayout(boundary_layout)
        main_tab_layout.addWidget(boundary_container)

        # Sezione generalizzazione
        generalization_label = QLabel("⚙️ Livello di dettaglio:")
        generalization_label.setStyleSheet(_STYLE_LABEL_SECTION)
        main_tab_layout.addWidget(generalization_label)

        gen_container = QtWidgets.QFrame()
        gen_container.setStyleSheet(_STYLE_FRAME)
        gen_layout = QVBoxLayout()
        gen_layout.setSpacing(6)

        self.generalization_group = QButtonGroup()
        self.radio_generalizzata     = QRadioButton("📦  Versione generalizzata (file più leggero, meno dettaglio)")
        self.radio_non_generalizzata = QRadioButton("🔍  Versione non generalizzata (dettaglio completo, file più pesante)")

        for radio in [self.radio_generalizzata, self.radio_non_generalizzata]:
            radio.setStyleSheet(_STYLE_RADIO)
            self.generalization_group.addButton(radio)
            gen_layout.addWidget(radio)

        self.radio_generalizzata.setChecked(True)
        gen_container.setLayout(gen_layout)
        main_tab_layout.addWidget(gen_container)

        # Sezione cartella di output
        output_label = QLabel("📁 Cartella di destinazione:")
        output_label.setStyleSheet(_STYLE_LABEL_SECTION)
        main_tab_layout.addWidget(output_label)

        output_container = QtWidgets.QFrame()
        output_container.setStyleSheet(_STYLE_FRAME)
        output_layout = QHBoxLayout()
        output_layout.setSpacing(8)

        self.output_path_edit = QLineEdit()
        self.output_path_edit.setPlaceholderText("Seleziona una cartella dove salvare i file...")
        self.output_path_edit.setText(os.path.expanduser("~/Desktop"))
        self.output_path_edit.setStyleSheet(_STYLE_LINEEDIT)

        self.browse_button = QPushButton("Sfoglia...")
        self.browse_button.setStyleSheet("""
            QPushButton {
                background-color: palette(button);
                color: palette(buttonText);
                border: 1px solid palette(mid);
                padding: 6px 14px;
                border-radius: 4px;
                font-weight: bold;
                min-width: 80px;
            }
            QPushButton:hover { background-color: palette(midlight); }
        """)
        self.browse_button.clicked.connect(self.browse_output_folder)

        output_layout.addWidget(self.output_path_edit)
        output_layout.addWidget(self.browse_button)
        output_container.setLayout(output_layout)
        main_tab_layout.addWidget(output_container)

        main_tab_layout.addStretch()
        main_tab.setLayout(main_tab_layout)
        self.tab_widget.addTab(main_tab, "🗺️ Confini Amministrativi")

        # ── TAB 2: Avanzate e Info ─────────────────────────────────────────
        advanced_tab = QtWidgets.QWidget()
        advanced_tab_layout = QVBoxLayout()
        advanced_tab_layout.setSpacing(12)
        advanced_tab_layout.setContentsMargins(15, 15, 15, 15)

        options_label = QLabel("⚙️ Opzioni avanzate:")
        options_label.setStyleSheet(_STYLE_LABEL_SECTION)
        advanced_tab_layout.addWidget(options_label)

        options_container = QtWidgets.QFrame()
        options_container.setStyleSheet(_STYLE_FRAME)
        options_layout = QVBoxLayout()
        options_layout.setSpacing(6)

        self.keep_files_checkbox = QCheckBox("🗃️  Mantieni i file scaricati dopo il caricamento")
        self.keep_files_checkbox.setStyleSheet(_STYLE_CHECKBOX)
        self.keep_files_checkbox.setChecked(True)

        self.open_folder_checkbox = QCheckBox("📂  Apri la cartella di destinazione al termine")
        self.open_folder_checkbox.setStyleSheet(_STYLE_CHECKBOX)
        self.open_folder_checkbox.setChecked(False)

        self.delete_zip_checkbox = QCheckBox("🗑️  Elimina i file ZIP dopo l'estrazione (conserva solo i file estratti)")
        self.delete_zip_checkbox.setStyleSheet(_STYLE_CHECKBOX)
        self.delete_zip_checkbox.setChecked(True)

        options_layout.addWidget(self.keep_files_checkbox)
        options_layout.addWidget(self.open_folder_checkbox)
        options_layout.addWidget(self.delete_zip_checkbox)
        options_container.setLayout(options_layout)
        advanced_tab_layout.addWidget(options_container)

        zip_note = QLabel("💡 Se elimini i file ZIP, conservi solo i dati estratti (shapefile). "
                          "Utile per risparmiare spazio su disco.")
        zip_note.setStyleSheet(_STYLE_NOTE)
        zip_note.setWordWrap(True)
        advanced_tab_layout.addWidget(zip_note)

        # Informazioni
        info_label = QLabel("ℹ️ Informazioni:")
        info_label.setStyleSheet(_STYLE_LABEL_SECTION)
        advanced_tab_layout.addWidget(info_label)

        info_container = QtWidgets.QFrame()
        info_container.setStyleSheet(_STYLE_FRAME_ACCENT)
        info_layout = QVBoxLayout()
        info_layout.setSpacing(8)

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
        info_text.setStyleSheet("font-size: 12px;")
        info_text.setOpenExternalLinks(True)
        info_layout.addWidget(info_text)
        info_container.setLayout(info_layout)
        advanced_tab_layout.addWidget(info_container)

        advanced_tab_layout.addStretch()
        advanced_tab.setLayout(advanced_tab_layout)
        self.tab_widget.addTab(advanced_tab, "⚙️ Avanzate e Info")

        # ── TAB 3: Griglia di Popolazione ─────────────────────────────────
        additional_data_tab = QtWidgets.QWidget()
        additional_data_layout = QVBoxLayout()
        additional_data_layout.setSpacing(12)
        additional_data_layout.setContentsMargins(15, 15, 15, 15)

        griglia_label = QLabel("📊 Dati aggiuntivi disponibili:")
        griglia_label.setStyleSheet(_STYLE_LABEL_SECTION)
        additional_data_layout.addWidget(griglia_label)

        griglia_container = QtWidgets.QFrame()
        griglia_container.setStyleSheet(_STYLE_FRAME_ACCENT)
        griglia_layout = QVBoxLayout()
        griglia_layout.setSpacing(10)

        self.griglia_pop_checkbox = QCheckBox("📊  Griglia di popolazione 2021 - Censimento (1 km²)")
        self.griglia_pop_checkbox.setStyleSheet("QCheckBox { font-size: 13px; font-weight: bold; padding: 6px; }")
        self.griglia_pop_checkbox.setChecked(False)

        griglia_description = QLabel("""
<b>Descrizione:</b><br>
Distribuzione della popolazione legale del Censimento 2021 su griglia regolare europea (Eurostat) con celle di 1 km².<br><br>
<b>Variabili censuarie disponibili (Reg. UE 1799/2018):</b><br>
• Popolazione totale, maschile e femminile<br>
• Popolazione per fasce di età (0-14, 15-64, oltre 65 anni)<br>
• Popolazione per luogo di nascita (Italia, altro paese EU, extra-EU)<br>
• Occupati • Mobilità residenziale<br><br>
<b>Formato:</b> Shapefile — ETRS89 / LAEA Europe [EPSG:3035]<br>
<b>Dimensione:</b> ~12 MB (compresso), ~250 MB (estratto)<br><br>
<b>📖 Info:</b> <a href="https://www.istat.it/notizia/statistiche-sulla-popolazione-per-griglia-regolare/">Statistiche popolazione per griglia regolare</a><br>
<b>📄 Metodologia:</b> <a href="https://www.istat.it/wp-content/uploads/2023/07/NotaMetodologicaGriglia2021-Ind.pdf">Nota metodologica (PDF)</a>
        """)
        griglia_description.setWordWrap(True)
        griglia_description.setStyleSheet("font-size: 12px; padding: 8px; border: 1px solid palette(mid); border-radius: 5px;")
        griglia_description.setOpenExternalLinks(True)

        griglia_layout.addWidget(self.griglia_pop_checkbox)
        griglia_layout.addWidget(griglia_description)
        griglia_container.setLayout(griglia_layout)
        additional_data_layout.addWidget(griglia_container)

        note_label = QLabel("⚠️ Note importanti:")
        note_label.setStyleSheet(_STYLE_LABEL_SECTION + " font-size: 13px;")
        additional_data_layout.addWidget(note_label)

        note_container = QtWidgets.QFrame()
        note_container.setStyleSheet(_STYLE_FRAME)
        note_layout = QVBoxLayout()

        note_text = QLabel("""
• La griglia di popolazione è un dataset separato dai confini amministrativi<br>
• Il download avverrà solo se questa opzione è selezionata<br>
• Il file verrà salvato nella stessa cartella di destinazione scelta nel tab principale<br>
• È possibile scaricare sia i confini amministrativi che la griglia popolazione contemporaneamente
        """)
        note_text.setWordWrap(True)
        note_text.setStyleSheet("font-size: 12px;")
        note_layout.addWidget(note_text)
        note_container.setLayout(note_layout)
        additional_data_layout.addWidget(note_container)

        additional_data_layout.addStretch()
        additional_data_tab.setLayout(additional_data_layout)
        self.tab_widget.addTab(additional_data_tab, "📊 Griglia di popolazione 2021")

        main_layout.addWidget(self.tab_widget)

        # ── Bottoni OK / Annulla ───────────────────────────────────────────
        self.button_box = QtWidgets.QDialogButtonBox()
        self.button_box.setOrientation(_HORIZONTAL)
        self.button_box.setStandardButtons(_BTN_OK_CANCEL)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        main_layout.addWidget(self.button_box)
        self.setLayout(main_layout)

        # Segnale per aggiornare UI quando cambia selezione confine
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
        return self.output_path_edit.text()

    def should_keep_files(self):
        return self.keep_files_checkbox.isChecked()

    def should_open_folder(self):
        return self.open_folder_checkbox.isChecked()

    def should_download_griglia_pop(self):
        return self.griglia_pop_checkbox.isChecked()

    def should_delete_zip(self):
        return self.delete_zip_checkbox.isChecked()

    def update_boundary_ui(self):
        """Aggiorna l'interfaccia quando cambia la selezione del confine"""
        is_no_boundary = self.radio_nessuno.isChecked()
        self.radio_generalizzata.setEnabled(not is_no_boundary)
        self.radio_non_generalizzata.setEnabled(not is_no_boundary)

        if is_no_boundary and not self.griglia_pop_checkbox.isChecked():
            self.tab_widget.setTabText(2, "📊 Griglia di popolazione 2021 ⚠️")
        else:
            self.tab_widget.setTabText(2, "📊 Griglia di popolazione 2021")
