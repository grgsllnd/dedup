

# 🧠 Dedup – Application de gestion intelligente des doublons
#
## Présentation générale
 
**Dedup** est une application graphique multiplateforme développée en **Python avec PySide6**, conçue pour faciliter la gestion et l'élimination de fichiers en double dans un système de fichiers. Elle permet aux utilisateurs de définir facilement des dossiers source et un dossier de destination, de sauvegarder leurs configurations, et de restaurer rapidement des scénarios courants via un système de favoris intégré.
 
L’interface est épurée, réactive, et pensée pour une utilisation simple mais puissante. Elle fonctionne parfaitement sur macOS avec intégration dans la barre de menu système.
 
---
 
## Fonctionnalités détaillées
 
### 🗂 Interface utilisateur
- **Dossiers source** :
  - Zone avec **glisser-déposer** ou ajout via bouton.
  - Chaque entrée comprend :
    - ✅ une **case à cocher** pour activer/désactiver le dossier
    - 🗑️ un **bouton de suppression** par ligne
  - Le tout dans une **scroll area compacte**, sans fioritures.
  
- **Dossier de destination** :
  - Un seul dossier sélectionnable via un bouton.
  - Il possède également un état actif (à venir dans l’UI).
  
- **Barre supérieure** :
  - Titre de l’application
  - Bouton ★ **Favoris** pour accès rapide aux configurations enregistrées
 
- **Menu macOS** :
  - Entrée unique **"Favoris"** dans la barre système
  - Ouvre la même fenêtre que le bouton Favoris
 
---
 
### 🌟 Système de favoris
 
Les favoris sont gérés dans un fichier `dedup.settings` (format JSON) :
 
```json
{
  "favorites": {
    "last_used": {
      "sources": [{ "path": "...", "active": true }],
      "destination": { "path": "...", "active": true }
    },
    "nom_du_favori": {
      "sources": [{ "path": "...", "active": true }],
      "destination": { "path": "...", "active": true }
    }
  }
}
```
 
#### Popup des favoris :
- 📋 Liste des favoris, avec `"📌 Dernier utilisé"` en premier et un séparateur
- 📄 Aperçu : dossier de destination + liste des sources
- 🔘 Boutons :
  - **Charger**
  - **Supprimer**
  - **Sauvegarder actuel**
 
L'app met automatiquement à jour `"last_used"` à chaque modification.
 
---
 
### 🔒 Stockage & Persistance
 
- Le fichier `dedup.settings` est toujours synchronisé :
  - lors de l'ajout ou suppression de dossiers source
  - lors de la sélection du dossier de destination
  - lors de toute modification de checkbox `active`
- Le dernier état est rechargé à chaque lancement
 
---
 
## À venir
 
- Moteur de détection et suppression de doublons
- Aperçu et comparaison de fichiers identiques
- Paramètres supplémentaires sur les sources et la destination (ex: priorité, filtrage)
- Export CSV ou HTML des doublons trouvés
- Analyse récursive configurable
 
---
 
## Technologies
 
- [Python 3.x](https://www.python.org/)
- [PySide6](https://doc.qt.io/qtforpython/)
- Compatible macOS, Windows, Linux
 
---
 
## Lancement
 
```bash
pip install -r requirements.txt
python main.py
```
 
---
 
## Auteur
 
Grégoire Sailland  
🧠 Fait pour aller plus loin avec ses fichiers, sans perdre de temps.