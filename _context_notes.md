
## Progres aktualizace - ZorSpec nástroj

### Aktuální stav
- ✅ InvVzd nástroj kompletně funkční s kroky zpracování
- ✅ UI vylepšení: Home navigace, clickable features, profesionální vzhled
- ✅ Template detekce a folder scanning pro InvVzd

### ZorSpec nástroj - požadavky
1. **Folder scan enhancement**: 
   - Načíst všechny soubory s listem 'Úvod a postup vyplňování'
   - Detekovat verzi (32h/16h) z buňky B1 na tomto listu
   - Zobrazit verzi u každého souboru

2. **Version mixing warning**:
   - Pokud folder obsahuje jak 32h tak 16h soubory → varování uživateli

3. **Auto-save results**:
   - Seznam žáků a result se automaticky uloží do složky se zdroji

### Implementace v dalším kontextovém okně
- Backend: Endpoint pro detekci ZorSpec souborů podle listu
- Frontend: Enhanced folder scanning s version info
- Processing: Auto-save do source folder místo download
- Validation: Mixed version detection a warnings

### Technické body
- Použít openpyxl pro čtení listu 'Úvod a postup vyplňování'
- Parser pro B1 buňku (regex pro '32 hodin'/'16 hodin')
- Enhanced UI pro zobrazení verze každého souboru
- Path utilities pro auto-save do source directory

