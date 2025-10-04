# Istruzioni per Test Manuale del Plugin

## Prerequisiti

1. QGIS 3.0 o superiore
2. Connessione internet attiva
3. Plugin installato e attivato

## Test Base

### 1. Test Apertura Plugin
- Aprire QGIS
- Cercare l'icona del plugin nella toolbar
- Cliccare per aprire la finestra di dialogo
- **Risultato atteso**: Si apre la finestra con 3 tab

### 2. Test Interface
- Verificare che tutti e 3 i tab siano accessibili:
  - 🗺️ Confini Amministrativi  
  - ⚙️ Avanzate e Info
  - 📊 Griglia di popolazione 2021
- **Risultato atteso**: Interfaccia completa e responsive

### 3. Test Download Singolo - Regioni
- Tab "Confini Amministrativi"
- Selezionare "🏛️ Regioni"  
- Scegliere "📦 Versione generalizzata"
- Impostare cartella di destinazione (es: Desktop)
- Cliccare "OK"
- **Risultato atteso**: 
  - Barra di progresso visibile
  - Download completato
  - Layer "ISTAT_Regioni_2025_generalizzata" caricato in QGIS

### 4. Test Download Multiplo
- Selezionare sia confini che griglia popolazione
- Tab "Confini": scegliere "🏢 Province"
- Tab "Griglia popolazione": selezionare checkbox
- Avviare download
- **Risultato atteso**: 
  - Due download sequenziali
  - Entrambi i layer caricati

### 5. Test Opzioni Avanzate
- Tab "Avanzate e Info"
- Testare opzioni:
  - ✅ Mantieni file scaricati
  - ✅ Elimina file ZIP
  - ✅ Apri cartella al termine
- **Risultato atteso**: Comportamento coerente con selezioni

## Test di Robustezza

### 1. Test Connessione
- Disconnettere internet durante download
- **Risultato atteso**: Messaggio di errore chiaro

### 2. Test Cartella Non Valida
- Inserire percorso inesistente
- **Risultato atteso**: Messaggio di validazione

### 3. Test Annullamento
- Avviare download e premere "Annulla"
- **Risultato atteso**: Download interrotto, file temporanei puliti

## Test Specifici QGIS

### 1. Test Layer Properties
- Caricare layer regioni
- Verificare sistema di riferimento (EPSG:32632)
- Controllare tabella attributi
- **Risultato atteso**: Dati ISTAT corretti e completi

### 2. Test Griglia Popolazione
- Caricare griglia popolazione
- Verificare sistema di riferimento (EPSG:3035)
- Controllare presenza 13 variabili censuarie
- **Risultato atteso**: Griglia europea standard con attributi corretti

## Checklist Finale

- [ ] Plugin si apre correttamente
- [ ] Tutti i tipi di confini scaricabili
- [ ] Griglia popolazione funzionante  
- [ ] Download multipli gestiti
- [ ] Gestione errori appropriata
- [ ] File salvati nella cartella corretta
- [ ] Layer caricati con attributi corretti
- [ ] Pulizia automatica file temporanei
- [ ] Opzioni avanzate funzionanti

## Risoluzione Problemi Comuni

1. **Errore SSL**: Il plugin prova prima con verifica SSL completa, poi chiede se disabilitare temporaneamente
2. **Download lento**: Dipende dalla connessione, server ISTAT può essere lento
3. **Layer non caricato**: Verificare che il download sia completato correttamente
4. **Cartella non accessibile**: Verificare permessi di scrittura sulla destinazione

## Report Bug

Se si trovano problemi, riportare su: https://github.com/pigreco/istat_confini_plugin/issues

Includere:
- Versione QGIS
- Sistema operativo  
- Messaggio di errore completo
- Passi per riprodurre il problema