# Changelog - Plugin Confini Amministrativi ISTAT

## Versione 1.1.0

### v1.1.0 (2025) ✨ **AGGIORNAMENTO MAGGIORE**

#### 📊 **Griglia di Popolazione 2021**
- Aggiunto un terzo tab all'interfaccia per selezionare dati aggiuntivi
- Possibilità di scaricare la **Griglia di Popolazione ISTAT 2021** (Censimento)
- Distribuzione popolazione legale su griglia europea (Eurostat) 1 km²
- URL: `https://www.istat.it/wp-content/uploads/2023/07/GrigliaPop2021_Ind_ITA.zip`

#### Caratteristiche della Griglia Popolazione
- **Risoluzione**: 1 km² (griglia regolare europea)
- **Standard**: Regolamento UE 1799/2018
- **Variabili censuarie (13 totali)**:
  - Popolazione totale, maschile, femminile
  - Popolazione per fasce di età (0-14, 15-64, oltre 65 anni)  
  - Popolazione per luogo di nascita (Italia, altro paese EU, extra-EU)
  - Occupati
  - Mobilità residenziale (stessa/altra dimora un anno prima)
- **Formato**: Shapefile in sistema di riferimento ETRS89 / LAEA Europe [EPSG:3035]
- **Vantaggi**: celle uniformi, griglia stabile, aggregazione flessibile, compatibilità europea
- **Dimensione**: ~12 MB (compresso), ~250 MB (estratto)
- **📖 Riferimento**: [Statistiche popolazione per griglia regolare ISTAT](https://www.istat.it/notizia/statistiche-sulla-popolazione-per-griglia-regolare/)
- **📄 Metodologia**: [Nota metodologica griglia 2021 (PDF)](https://www.istat.it/wp-content/uploads/2023/07/NotaMetodologicaGriglia2021-Ind.pdf)

### 🔧 Miglioramenti Tecnici

#### Download Flessibili
- **NUOVO**: Opzione "Nessun confine" per scaricare solo la griglia popolazione
- Implementato sistema di download multipli in coda
- Possibilità di scaricare:
  - Solo confini amministrativi (generalizzati o non generalizzati)
  - Solo griglia popolazione 2021
  - Entrambi i dataset contemporaneamente
- Progress bar aggiornata per mostrare il progresso di ogni download

#### Gestione Flessibile
- L'utente può selezionare:
  - Solo confini amministrativi
  - Solo griglia popolazione  
  - Entrambi i dataset contemporaneamente
  - **NUOVO**: Opzione esplicita "Nessun confine" per chiarire la possibilità di scaricare solo dati aggiuntivi
- Validazione migliorata: almeno un dataset deve essere selezionato
- **NUOVO**: Interfaccia dinamica che disabilita opzioni non pertinenti

#### Interfaccia Migliorata
- Nuovo tab "📊 Griglia di popolazione 2021" con:
  - Checkbox per selezionare la griglia popolazione
  - Descrizione dettagliata del contenuto
  - Note informative sull'utilizzo
- Design coerente con gli altri tab esistenti
- **NUOVO**: Opzione "Elimina file ZIP dopo estrazione" nel tab Avanzate
- Note informative per guidare l'utente nelle scelte di archiviazione

### 🗂️ Organizzazione File
- I file della griglia popolazione vengono salvati in: `ISTAT_Griglia_Popolazione_2021/`
- Mantenimento della struttura di cartelle esistente per i confini amministrativi
- Gestione automatica di conflitti di nomi cartelle

### ⚡ Ottimizzazioni
- Refactoring del codice per supportare download multipli
- Separazione logica per estrazione confini vs griglia popolazione
- Gestione errori migliorata per identificare il tipo di download fallito
- Messaggi di successo più informativi per download multipli

---

## Utilizzo

1. **Tab Principale**: Seleziona tipo di confine amministrativo e livello di dettaglio
2. **Tab Avanzate & Info**: Configura opzioni di salvataggio e visualizza informazioni sui dati
3. **Tab Dati Aggiuntivi**: ✨ **NUOVO** - Seleziona la griglia popolazione 2021
4. Clicca OK per iniziare i download selezionati

I layer verranno caricati automaticamente in QGIS al termine del download e dell'estrazione.
