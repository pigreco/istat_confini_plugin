# -*- coding: utf-8 -*-
"""
/***************************************************************************
 IstatConfiniPlugin
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
import tempfile
import zipfile
import shutil
import subprocess
import platform
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication, Qt, QThread, pyqtSignal, QUrl, QEventLoop
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QMessageBox, QProgressDialog
from qgis.PyQt.QtNetwork import QNetworkRequest, QNetworkReply, QSslConfiguration
from qgis.core import QgsProject, QgsVectorLayer, QgsMessageLog, Qgis, QgsNetworkAccessManager
from .istat_confini_dialog import IstatConfiniDialog

class DownloadThread(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(str)
    error = pyqtSignal(str)
    
    def __init__(self, url, output_path, ignore_ssl_errors=False):
        super().__init__()
        self.url = url
        self.output_path = output_path
        self.ignore_ssl_errors = ignore_ssl_errors
        self.network_manager = QgsNetworkAccessManager.instance()
        self.reply = None
        self.output_file = None
        self.downloaded = 0
        self.total_size = 0
    
    def run(self):
        try:
            # Crea la richiesta con QgsNetworkAccessManager
            request = QNetworkRequest(QUrl(self.url))
            request.setRawHeader(b'User-Agent', b'QGIS ISTAT Plugin')
            
            # Configura SSL se richiesto
            if self.ignore_ssl_errors:
                ssl_config = QSslConfiguration.defaultConfiguration()
                ssl_config.setPeerVerifyMode(QSslConfiguration.VerifyNone)
                request.setSslConfiguration(ssl_config)
                QgsMessageLog.logMessage("SSL verification disabled for ISTAT server compatibility", 
                                       "IstatConfiniPlugin", Qgis.Warning)
            
            # Avvia il download
            self.reply = self.network_manager.get(request)
            
            # Ignora errori SSL se richiesto
            if self.ignore_ssl_errors:
                self.reply.sslErrors.connect(lambda errors: self.reply.ignoreSslErrors())
            
            # Connetti i segnali
            self.reply.downloadProgress.connect(self.on_download_progress)
            self.reply.finished.connect(self.on_finished)
            self.reply.readyRead.connect(self.on_ready_read)
            self.reply.error.connect(self.on_error)
            
            # Apri il file di output
            self.output_file = open(self.output_path, 'wb')
            
            # Avvia il loop degli eventi
            loop = QEventLoop()
            self.reply.finished.connect(loop.quit)
            loop.exec_()
            
        except Exception as e:
            self.error.emit(f"Errore durante il download: {str(e)}")
            
    def on_download_progress(self, bytes_received, bytes_total):
        """Gestisce il progresso del download"""
        if bytes_total > 0:
            progress_percent = int((bytes_received / bytes_total) * 100)
            self.progress.emit(progress_percent)
            
    def on_ready_read(self):
        """Legge i dati disponibili e li scrive nel file"""
        if self.output_file and self.reply:
            data = self.reply.readAll()
            self.output_file.write(data.data())
            
    def on_finished(self):
        """Gestisce il completamento del download"""
        try:
            if self.output_file:
                self.output_file.close()
                self.output_file = None
                
            if self.reply and self.reply.error() == QNetworkReply.NoError:
                self.finished.emit(self.output_path)
            elif self.reply:
                error_msg = self.reply.errorString()
                self.error.emit(f"Errore di rete: {error_msg}")
                
        except Exception as e:
            self.error.emit(f"Errore durante il salvataggio: {str(e)}")
            
    def on_error(self, error):
        """Gestisce gli errori di rete"""
        if self.reply:
            error_msg = self.reply.errorString()
            if "SSL" in error_msg or "certificate" in error_msg.lower():
                self.error.emit(f"Errore SSL (certificato potenzialmente scaduto): {error_msg}")
            else:
                self.error.emit(f"Errore di rete: {error_msg}")
        else:
            self.error.emit(f"Errore di rete sconosciuto: {error}")


class IstatConfiniPlugin:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'IstatConfiniPlugin_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Confini Amministrativi ISTAT')

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('IstatConfiniPlugin', message)

    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            # Adds plugin icon to Plugins toolbar
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = os.path.join(self.plugin_dir, 'icon.png')
        self.add_action(
            icon_path,
            text=self.tr(u'Scarica Confini Amministrativi ISTAT'),
            callback=self.run,
            parent=self.iface.mainWindow())

        # will be set False in run()
        self.first_start = True

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        # Pulizia file temporanei al momento della disattivazione
        self.cleanup_temp_files()
        
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Confini Amministrativi ISTAT'),
                action)
            self.iface.removeToolBarIcon(action)

    def run(self):
        """Run method that performs all the real work"""

        # Create the dialog with elements (after translation) and keep reference
        # Only create GUI ONCE in callback, so that it will only load when the plugin is started
        if self.first_start == True:
            self.first_start = False
            self.dlg = IstatConfiniDialog()

        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            self.download_and_load_data()

    def download_and_load_data(self):
        """Scarica i dati ISTAT e li carica in QGIS"""
        # Ottieni le selezioni dell'utente
        is_generalized = self.dlg.radio_generalizzata.isChecked()
        selected_boundary = self.dlg.get_selected_boundary()
        output_path = self.dlg.get_output_path()
        keep_files = self.dlg.should_keep_files()
        open_folder = self.dlg.should_open_folder()
        download_griglia_pop = self.dlg.should_download_griglia_pop()
        delete_zip = self.dlg.should_delete_zip()
        
        # Verifica se almeno una opzione è selezionata
        if not selected_boundary and not download_griglia_pop:
            QMessageBox.warning(self.iface.mainWindow(), 
                              "Attenzione", 
                              "Seleziona almeno un tipo di dato da scaricare (confine amministrativo o griglia popolazione).")
            return
        
        if not output_path or not os.path.exists(output_path):
            QMessageBox.warning(self.iface.mainWindow(), 
                              "Attenzione", 
                              "Seleziona una cartella di destinazione valida.")
            return
        
        # Mostra avviso per SSL
        reply = QMessageBox.question(
            self.iface.mainWindow(),
            "Configurazione SSL",
            "I server ISTAT possono avere certificati SSL problematici.\n\n"
            "Il plugin proverà prima con verifica SSL completa, e in caso di errore "
            "richiederà se disabilitare la verifica SSL temporaneamente.\n\n"
            "Vuoi continuare con il download?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes
        )
        if reply == QMessageBox.No:
            return
        
        # Crea una directory temporanea per il download
        self.temp_dir = tempfile.mkdtemp(prefix="istat_download_")
        
        # Salva le opzioni per usarle dopo il download
        self.user_options = {
            'boundary_type': selected_boundary,
            'output_path': output_path,
            'keep_files': keep_files,
            'open_folder': open_folder,
            'is_generalized': is_generalized,
            'download_griglia_pop': download_griglia_pop,
            'delete_zip': delete_zip
        }
        
        # Opzioni SSL - prova prima con verifica, poi senza se necessario
        self.ssl_retry_mode = False
        
        # Lista dei download da effettuare
        self.download_queue = []
        
        # Aggiungi confini amministrativi se selezionati
        if selected_boundary:
            if is_generalized:
                url = "https://www.istat.it/storage/cartografia/confini_amministrativi/generalizzati/2025/Limiti01012025_g.zip"
                suffix = "_generalizzata"
            else:
                url = "https://www.istat.it/storage/cartografia/confini_amministrativi/non_generalizzati/2025/Limiti01012025.zip"
                suffix = "_completa"
            
            zip_path = os.path.join(self.temp_dir, "confini_istat.zip")
            self.download_queue.append({
                'url': url,
                'path': zip_path,
                'type': 'confini',
                'suffix': suffix
            })
        
        # Aggiungi griglia popolazione se selezionata
        if download_griglia_pop:
            griglia_url = "https://www.istat.it/wp-content/uploads/2023/07/GrigliaPop2021_Ind_ITA.zip"
            griglia_path = os.path.join(self.temp_dir, "griglia_pop_2021.zip")
            self.download_queue.append({
                'url': griglia_url,
                'path': griglia_path,
                'type': 'griglia_pop',
                'suffix': '_2021'
            })
        
        # Mostra la dialog di progresso
        total_downloads = len(self.download_queue)
        self.progress_dialog = QProgressDialog(f"Preparazione download (0/{total_downloads})...", "Annulla", 0, 100, self.iface.mainWindow())
        self.progress_dialog.setWindowModality(Qt.WindowModal)
        self.progress_dialog.show()
        
        # Inizia con il primo download
        self.current_download_index = 0
        self.start_next_download()

    def start_next_download(self):
        """Avvia il prossimo download nella coda"""
        if self.current_download_index >= len(self.download_queue):
            # Tutti i download completati, procedi con l'estrazione
            self.extract_and_load_all()
            return
        
        current_download = self.download_queue[self.current_download_index]
        total_downloads = len(self.download_queue)
        
        # Aggiorna la label di progresso
        if current_download['type'] == 'confini':
            self.progress_dialog.setLabelText(f"Download confini amministrativi ({self.current_download_index + 1}/{total_downloads})...")
        elif current_download['type'] == 'griglia_pop':
            self.progress_dialog.setLabelText(f"Download griglia popolazione ({self.current_download_index + 1}/{total_downloads})...")
        
        # Avvia il download con opzioni SSL
        self.download_thread = DownloadThread(
            current_download['url'], 
            current_download['path'], 
            ignore_ssl_errors=self.ssl_retry_mode
        )
        self.download_thread.progress.connect(self.progress_dialog.setValue)
        self.download_thread.finished.connect(self.download_completed)
        self.download_thread.error.connect(self.download_error)
        self.download_thread.start()
    
    def download_completed(self, zip_path):
        """Gestisce il completamento di un singolo download"""
        self.current_download_index += 1
        self.start_next_download()

    def download_error(self, error_msg):
        """Gestisce gli errori di download con retry SSL"""
        # Determina quale download è fallito
        current_download = self.download_queue[self.current_download_index] if self.current_download_index < len(self.download_queue) else None
        download_type = current_download['type'] if current_download else "sconosciuto"
        
        # Se è un errore SSL e non abbiamo ancora provato senza verifica SSL
        if ("SSL" in error_msg or "certificate" in error_msg.lower() or "certificato" in error_msg.lower()) and not self.ssl_retry_mode:
            # Chiedi all'utente se vuole riprovare senza verifica SSL
            reply = QMessageBox.question(
                self.iface.mainWindow(),
                "Errore certificato SSL",
                f"Errore SSL durante il download ({download_type}):\n{error_msg}\n\n"
                "I server ISTAT hanno spesso certificati SSL problematici.\n"
                "Vuoi riprovare disabilitando temporaneamente la verifica SSL?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )
            
            if reply == QMessageBox.Yes:
                # Abilita modalità SSL disabilitato e riprova
                self.ssl_retry_mode = True
                QgsMessageLog.logMessage("Retry download con SSL disabilitato per compatibilità server ISTAT", 
                                       "IstatConfiniPlugin", Qgis.Info)
                
                # Riavvia il download corrente
                self.start_next_download()
                return
        
        # Se non è un errore SSL o l'utente ha rifiutato il retry, mostra errore finale
        self.cleanup_temp_files()
        self.progress_dialog.close()
        
        if "SSL" in error_msg or "certificate" in error_msg.lower() or "certificato" in error_msg.lower():
            detailed_msg = f"Errore SSL durante il download ({download_type}): {error_msg}\n\n" \
                         f"Il server ISTAT ha problemi con i certificati SSL. " \
                         f"Verifica la connessione internet e riprova."
        else:
            detailed_msg = f"Errore durante il download ({download_type}): {error_msg}"
            
        QMessageBox.critical(self.iface.mainWindow(), 
                           "Errore Download", 
                           detailed_msg)

    def extract_and_load_all(self):
        """Estrae tutti i dati scaricati e li carica in QGIS"""
        try:
            self.progress_dialog.setLabelText("Estrazione in corso...")
            
            loaded_layers = []
            created_folders = []
            
            # Processa ogni download completato
            for download_info in self.download_queue:
                if download_info['type'] == 'confini':
                    layer = self.extract_and_load_confini(download_info)
                    if layer:
                        loaded_layers.append(layer)
                        # Aggiungi la cartella alla lista se i file vengono mantenuti
                        if self.user_options['keep_files']:
                            boundary_type = self.user_options['boundary_type']
                            suffix = download_info['suffix']
                            final_folder_name = f"ISTAT_{boundary_type.capitalize()}_2025{suffix}"
                            final_target_path = os.path.join(self.user_options['output_path'], final_folder_name)
                            created_folders.append(final_target_path)
                
                elif download_info['type'] == 'griglia_pop':
                    layer = self.extract_and_load_griglia_pop(download_info)
                    if layer:
                        loaded_layers.append(layer)
                        # Aggiungi la cartella alla lista se i file vengono mantenuti
                        if self.user_options['keep_files']:
                            final_folder_name = "ISTAT_Griglia_Popolazione_2021"
                            final_target_path = os.path.join(self.user_options['output_path'], final_folder_name)
                            created_folders.append(final_target_path)
            
            # Pulizia file temporanei
            self.cleanup_temp_files()
            
            # Chiudi la dialog di progresso
            self.progress_dialog.close()
            
            # Messaggio di successo
            if loaded_layers:
                layer_names = [layer.name() for layer in loaded_layers]
                if len(layer_names) == 1:
                    message = f"Layer '{layer_names[0]}' caricato con successo!"
                else:
                    message = f"Layers caricati con successo:\n• " + "\n• ".join(layer_names)
                
                if self.user_options['keep_files'] and created_folders:
                    message += f"\n\nFile salvati in:\n• " + "\n• ".join(created_folders)
                    
                    if not self.user_options['open_folder']:
                        message += "\n\nVuoi aprire la cartella di destinazione?"
                        reply = QMessageBox.question(
                            self.iface.mainWindow(),
                            "Successo",
                            message,
                            QMessageBox.Yes | QMessageBox.No,
                            QMessageBox.No
                        )
                        if reply == QMessageBox.Yes:
                            self.user_options['open_folder'] = True
                else:
                    QMessageBox.information(self.iface.mainWindow(), "Successo", message)
                
                # Apri la cartella se richiesto (apri la prima cartella nella lista)
                if self.user_options['open_folder'] and self.user_options['keep_files'] and created_folders:
                    self.open_folder_in_explorer(created_folders[0])
                
                # Log
                for layer in loaded_layers:
                    QgsMessageLog.logMessage(f"Layer ISTAT caricato: {layer.name()}", 
                                           "IstatConfiniPlugin", Qgis.Info)
            else:
                QMessageBox.warning(self.iface.mainWindow(), "Attenzione", "Nessun layer è stato caricato.")
                                   
        except Exception as e:
            self.cleanup_temp_files()
            self.progress_dialog.close()
            QMessageBox.critical(self.iface.mainWindow(), 
                               "Errore", 
                               f"Errore durante l'estrazione o il caricamento: {str(e)}")
            QgsMessageLog.logMessage(f"Errore: {str(e)}", 
                                   "IstatConfiniPlugin", Qgis.Critical)

    def extract_and_load_confini(self, download_info):
        """Estrae e carica i confini amministrativi"""
        try:
            zip_path = download_info['path']
            suffix = download_info['suffix']
            boundary_type = self.user_options['boundary_type']
            output_path = self.user_options['output_path']
            keep_files = self.user_options['keep_files']
            
            # Mapping dei tipi di confine alle cartelle
            if suffix == "_generalizzata":
                folder_mapping = {
                    "regioni": "Reg01012025_g",
                    "province": "ProvCM01012025_g", 
                    "comuni": "Com01012025_g",
                    "ripartizioni": "RipGeo01012025_g"
                }
            else:  # versione non generalizzata
                folder_mapping = {
                    "regioni": "Reg01012025",
                    "province": "ProvCM01012025", 
                    "comuni": "Com01012025",
                    "ripartizioni": "RipGeo01012025"
                }
            
            target_folder = folder_mapping.get(boundary_type)
            if not target_folder:
                raise Exception(f"Tipo di confine non riconosciuto: {boundary_type}")
            
            # Estrai il contenuto nella directory temporanea
            extract_temp_dir = os.path.dirname(zip_path)
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_temp_dir)
            
            # Trova la cartella specifica
            temp_target_path = os.path.join(extract_temp_dir, target_folder)
            if not os.path.exists(temp_target_path):
                extracted_items = os.listdir(extract_temp_dir)
                similar_folders = [f for f in extracted_items if os.path.isdir(os.path.join(extract_temp_dir, f)) and boundary_type.lower() in f.lower()]
                if similar_folders:
                    target_folder = similar_folders[0]
                    temp_target_path = os.path.join(extract_temp_dir, target_folder)
                    QgsMessageLog.logMessage(f"Uso cartella alternativa: {target_folder}", "IstatConfiniPlugin", Qgis.Info)
                else:
                    raise Exception(f"Cartella {target_folder} non trovata nell'archivio.\nCartelle disponibili: {extracted_items}")
            
            # Crea la cartella di destinazione finale se necessario
            if keep_files:
                final_folder_name = f"ISTAT_{boundary_type.capitalize()}_2025{suffix}"
                final_target_path = os.path.join(output_path, final_folder_name)
                
                if os.path.exists(final_target_path):
                    shutil.rmtree(final_target_path)
                
                shutil.copytree(temp_target_path, final_target_path)
                shp_search_path = final_target_path
                
                # Gestione file ZIP: copia o elimina in base alle preferenze utente
                delete_zip = self.user_options.get('delete_zip', True)
                if not delete_zip:
                    # Copia il file ZIP nella cartella finale
                    zip_filename = os.path.basename(zip_path)
                    final_zip_path = os.path.join(final_target_path, zip_filename)
                    shutil.copy2(zip_path, final_zip_path)
                    QgsMessageLog.logMessage(f"File ZIP conservato: {final_zip_path}", "IstatConfiniPlugin", Qgis.Info)
                else:
                    # Elimina il file ZIP dalla cartella finale se presente
                    zip_filename = os.path.basename(zip_path)
                    final_zip_path = os.path.join(final_target_path, zip_filename)
                    if os.path.exists(final_zip_path):
                        os.remove(final_zip_path)
                        QgsMessageLog.logMessage(f"File ZIP eliminato dalla cartella finale: {final_zip_path}", "IstatConfiniPlugin", Qgis.Info)
                    
                    # Elimina anche il file ZIP dalla directory temporanea
                    if os.path.exists(zip_path):
                        os.remove(zip_path)
                        QgsMessageLog.logMessage(f"File ZIP eliminato dalla directory temporanea: {zip_path}", "IstatConfiniPlugin", Qgis.Info)
            else:
                shp_search_path = temp_target_path
            
            # Trova il file shapefile
            shp_files = [f for f in os.listdir(shp_search_path) if f.endswith('.shp')]
            if not shp_files:
                raise Exception(f"Nessun file shapefile trovato in {target_folder}")
            
            shp_path = os.path.join(shp_search_path, shp_files[0])
            
            # Carica il layer in QGIS
            layer_name = f"ISTAT_{boundary_type.capitalize()}_2025{suffix}"
            layer = QgsVectorLayer(shp_path, layer_name, "ogr")
            
            if not layer.isValid():
                raise Exception("Impossibile caricare il layer dei confini amministrativi")
            
            QgsProject.instance().addMapLayer(layer)
            return layer
            
        except Exception as e:
            QgsMessageLog.logMessage(f"Errore estrazione confini: {str(e)}", "IstatConfiniPlugin", Qgis.Critical)
            return None

    def extract_and_load_griglia_pop(self, download_info):
        """Estrae e carica la griglia popolazione"""
        try:
            zip_path = download_info['path']
            output_path = self.user_options['output_path']
            keep_files = self.user_options['keep_files']
            
            # Estrai il contenuto nella directory temporanea
            extract_temp_dir = os.path.dirname(zip_path)
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_temp_dir)
            
            # Cerca file shapefile nella directory estratta (potrebbe essere in sottocartelle)
            shp_files = []
            for root, dirs, files in os.walk(extract_temp_dir):
                for file in files:
                    if file.endswith('.shp'):
                        shp_files.append(os.path.join(root, file))
            
            if not shp_files:
                raise Exception("Nessun file shapefile trovato nell'archivio della griglia popolazione")
            
            # Usa il primo shapefile trovato
            shp_path = shp_files[0]
            shp_dir = os.path.dirname(shp_path)
            
            # Crea la cartella di destinazione finale se necessario
            if keep_files:
                final_folder_name = "ISTAT_Griglia_Popolazione_2021"
                final_target_path = os.path.join(output_path, final_folder_name)
                
                if os.path.exists(final_target_path):
                    shutil.rmtree(final_target_path)
                
                # Copia tutti i file della griglia
                shutil.copytree(shp_dir, final_target_path)
                
                # Gestione file ZIP: copia o elimina in base alle preferenze utente
                delete_zip = self.user_options.get('delete_zip', True)
                if not delete_zip:
                    # Copia il file ZIP nella cartella finale
                    zip_filename = os.path.basename(zip_path)
                    final_zip_path = os.path.join(final_target_path, zip_filename)
                    shutil.copy2(zip_path, final_zip_path)
                    QgsMessageLog.logMessage(f"File ZIP griglia popolazione conservato: {final_zip_path}", "IstatConfiniPlugin", Qgis.Info)
                else:
                    # Elimina il file ZIP dalla cartella finale se presente
                    zip_filename = os.path.basename(zip_path)
                    final_zip_path = os.path.join(final_target_path, zip_filename)
                    if os.path.exists(final_zip_path):
                        os.remove(final_zip_path)
                        QgsMessageLog.logMessage(f"File ZIP eliminato dalla cartella finale: {final_zip_path}", "IstatConfiniPlugin", Qgis.Info)
                    
                    # Elimina anche il file ZIP dalla directory temporanea
                    if os.path.exists(zip_path):
                        os.remove(zip_path)
                        QgsMessageLog.logMessage(f"File ZIP eliminato dalla directory temporanea: {zip_path}", "IstatConfiniPlugin", Qgis.Info)
                
                # Aggiorna il percorso del shapefile
                shp_filename = os.path.basename(shp_path)
                shp_path = os.path.join(final_target_path, shp_filename)
            else:
                # keep_files=False: usa il file temporaneo ma elimina comunque il ZIP se richiesto
                delete_zip = self.user_options.get('delete_zip', True)
                if delete_zip:
                    if os.path.exists(zip_path):
                        os.remove(zip_path)
                        QgsMessageLog.logMessage(f"File ZIP eliminato dalla directory temporanea: {zip_path}", "IstatConfiniPlugin", Qgis.Info)
            
            # Carica il layer in QGIS
            layer_name = "ISTAT_Griglia_Popolazione_2021"
            layer = QgsVectorLayer(shp_path, layer_name, "ogr")
            
            if not layer.isValid():
                raise Exception("Impossibile caricare il layer della griglia popolazione")
            
            QgsProject.instance().addMapLayer(layer)
            return layer
            
        except Exception as e:
            QgsMessageLog.logMessage(f"Errore estrazione griglia popolazione: {str(e)}", "IstatConfiniPlugin", Qgis.Critical)
            return None

    def cleanup_temp_files(self):
        """Pulisce i file temporanei"""
        try:
            if hasattr(self, 'temp_dir') and os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
                QgsMessageLog.logMessage(f"File temporanei rimossi: {self.temp_dir}", 
                                       "IstatConfiniPlugin", Qgis.Info)
        except Exception as e:
            QgsMessageLog.logMessage(f"Errore durante la pulizia file temporanei: {str(e)}", 
                                   "IstatConfiniPlugin", Qgis.Warning)
    
    def open_folder_in_explorer(self, folder_path):
        """Apre la cartella nel file manager del sistema operativo"""
        try:
            system = platform.system()
            if system == "Windows":
                os.startfile(folder_path)
            elif system == "Darwin":  # macOS
                subprocess.run(["open", folder_path])
            else:  # Linux
                subprocess.run(["xdg-open", folder_path])
        except Exception as e:
            QgsMessageLog.logMessage(f"Impossibile aprire la cartella: {str(e)}", 
                                   "IstatConfiniPlugin", Qgis.Warning)