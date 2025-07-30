# KIC-AI Assistant v1.3.0 - 3 Interaction Modes

## 🆕 What's New

### 3 AI Interaction Modes

De plugin heeft nu 3 verschillende interactie-niveaus:

#### 🔍 Analysis Mode (Veilig)
- **Wat het doet**: Analyseert je ontwerp en geeft aanbevelingen
- **Veiligheid**: Geen wijzigingen aan je project
- **Voor wie**: Alle gebruikers, leren, design inzichten krijgen
- **Voorbeeld**: "Je voeding heeft goede ontkoppeling, maar overweeg een ferriet kraal op de ingang"

#### 📋 Advisory Mode (Begeleiding)
- **Wat het doet**: Geeft stap-voor-stap instructies met gebruikersbevestiging  
- **Veiligheid**: Begeleidt je door wijzigingen met duidelijke stappen
- **Voor wie**: Gebruikers die gedetailleerde begeleiding willen
- **Voorbeeld**: "Om dit circuit te verbeteren: 1) Selecteer R14 2) Wijzig waarde naar 10kΩ 3) Update het schema. Zal ik je hierdoor begeleiden?"

#### 🤖 Assistant Mode (Interactief)
- **Wat het doet**: Interactieve design aanbevelingen en toekomstige automatisering
- **Veiligheid**: Geavanceerde functies voor ervaren gebruikers
- **Voor wie**: Power users, complexe design taken
- **Voorbeeld**: "Ik kan je power routing optimaliseren. In toekomstige versies kan ik mogelijk enkele plaatsingstaken automatiseren."

### Nieuwe UI Features

- **Mode Selector**: Dropdown om je gewenste interactie niveau te kiezen
- **Mode Help**: "?" knop met uitleg van alle modi
- **Status Updates**: Toont huidige mode in status balk
- **Context Awareness**: AI past antwoorden aan op basis van gekozen mode

### Verbeterde AI Responses

- **Mode-Specific Instructions**: AI krijgt verschillende instructies per mode
- **Safety Warnings**: Advisory mode voegt waarschuwingen toe bij modificaties
- **Interactive Guidance**: Assistant mode kondigt toekomstige automatisering aan
- **Conversation Memory**: Verbeterde context awareness

## 🔧 Technical Changes

### Code Structure
- Nieuwe `interaction_mode` property in AIAssistantDialog
- `get_mode_instructions()` method voor mode-specifieke AI instructies
- Enhanced `process_user_message()` met mode-specifieke handling
- UI uitbreiding met mode selector en help

### AI Integration
- Mode instructions worden toegevoegd aan AI system prompt
- Context-aware responses gebaseerd op gekozen mode
- Improved conversation history management

## 🚀 Usage

1. Open PCB Editor
2. Klik KIC-AI robot icon
3. **NIEUW**: Kies je AI interaction mode
4. Klik "?" voor mode uitleg
5. Start chatten of analyseren

## 🎯 Future Plans

- **Assistant Mode**: Implementatie van semi-automatische wijzigingen
- **Component Management**: Direct component wijzigingen met bevestiging
- **Advanced Automation**: Intelligente design optimalisaties
- **Multi-language**: Nederlandse interface optie

## 📝 Migration Notes

- Bestaande gebruikers starten automatisch in Analysis Mode (veiligste optie)
- Alle bestaande functionaliteit blijft beschikbaar
- Nieuwe modes voegen functionaliteit toe zonder bestaande workflows te verstoren

---

**Veiligheid eerst**: Begin met Analysis Mode om de nieuwe features te verkennen!
