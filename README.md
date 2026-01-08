# NTL-SysToolbox

Outil en ligne de commande pour l'exploitation de l'infrastructure de NordTransit Logistics (NTL).

## Objectifs

- Vérifier rapidement l'état des services critiques (AD/DNS, MySQL, utilisation des ressources).
- Automatiser les sauvegardes logiques de la base WMS (export SQL et CSV).
- Réaliser un audit d'obsolescence des systèmes (inventaire réseau + statut EOL des OS).

## Modules

1. **Diagnostic**
   - Vérification des services AD/DNS.
   - Vérification de la base MySQL.
   - Récupération d'informations système (OS, uptime, CPU/RAM/disque) pour Windows Server et Ubuntu.

2. **Sauvegarde WMS**
   - Sauvegarde de la base MySQL au format SQL.
   - Export d'une table au format CSV.

3. **Audit d'obsolescence**
   - Scan d'une plage réseau.
   - Détection de l'OS (dans la mesure du possible).
   - Récupération des dates de fin de vie des OS.
   - Production d'un rapport structuré (JSON + rapport lisible).

## Exécution

```bash
# installer les requirements
pip install -r requirements.txt

# executer le script
python main.py
