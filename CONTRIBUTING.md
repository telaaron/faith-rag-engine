# Contributing to Spiritual Companion MVP

Danke, dass du bei diesem Projekt mithelfen möchtest! 🙏 Wir freuen uns über deine Beiträge.

## 🤝 Wie kannst du beitragen?

### 1. **Bugs melden**
Falls du einen Bug findest:
- Öffne ein Issue auf GitHub
- Beschreibe das Problem klar und gib Steps zur Reproduktion an
- Gib deine Python-Version und deinen Browser an

### 2. **Features vorschlagen**
Du hast eine gute Idee?
- Öffne ein Issue mit dem Label "enhancement"
- Erkläre die Idee und warum sie wertvoll für das Projekt ist
- Diskutiere mit der Community

### 3. **Code beitragen**

#### Setup für die lokale Entwicklung:
```bash
# Repository klonen
git clone https://github.com/telaaron/spiritual-companion-mvp.git
cd spiritual-companion-mvp

# Virtual Environment erstellen
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
# oder
.venv\Scripts\activate  # Windows

# Dependencies installieren
pip install -r backend/requirements.txt

# Backend starten
uvicorn backend.app.main:app --reload
```

#### Vor dem Commit:
- Stelle sicher, dass der Code sauber und verständlich ist
- Schreib aussagekräftige Commit-Messages
- Teste deine Änderungen lokal
- Kommentiere komplexe Logik

### 4. **Dokumentation verbessern**
- Grammatik und Tippfehler korrigieren
- Komplexe Konzepte erklären
- Beispiele hinzufügen

## 📋 Contribution Workflow

1. **Fork** das Repository
2. **Erstelle einen Feature-Branch**: `git checkout -b feature/deine-idee`
3. **Commit deine Änderungen**: `git commit -m "feat: aussagekräftige Beschreibung"`
4. **Push zum Branch**: `git push origin feature/deine-idee`
5. **Öffne einen Pull Request**
   - Beschreibe klar, was du geändert hast
   - Verlinke relevante Issues
   - Erkläre, warum diese Änderung wichtig ist

## 💡 Best Practices

### Code Style
- Verwende aussagekräftige Variablen- und Funktionsnamen
- Halte Funktionen klein und fokussiert
- Kommentiere nicht-offensichtliche Logik

### Commits
- Nutze klare, im Präsens verfasste Commit-Messages
- Nutze Prefixes: `feat:`, `fix:`, `docs:`, `refactor:`, etc.
- Ein Commit = eine logische Änderung

### Pull Requests
- Beschreibe deine Änderungen klar
- Gib Kontext: Warum ist diese Änderung nötig?
- Sei offen für Feedback und Verbesserungsvorschläge

## 🛡️ Theological Safety

Da dieses Projekt religiöse Inhalte behandelt:
- Stelle sicher, dass deine Änderungen theologisch kohärent sind
- Respektiere verschiedene theologische Perspektiven
- Verwende nur Quellen mit akademischer Glaubwürdigkeit
- Wenn du bibelbezogene Änderungen machst, beziehe die RAG-Architektur ein

## ❓ Fragen?

- Öffne ein Discussion auf GitHub
- Schreib ein Issue mit dem Label "question"
- Kontaktiere Aaron direkt

## 📝 Code of Conduct

Wir verpflichten uns, ein einladendes und respektvolles Umfeld zu schaffen.
- Behandle alle mit Respekt
- Sei konstruktiv in Feedback
- Hasse niemals die Sache, nicht die Person
- Respektiere unterschiedliche Meinungen und Hintergründe

---

**Vielen Dank dafür, dass du dieses Projekt voranbringst!** ❤️
