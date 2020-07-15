# Freebox Purge Records

Script pour automatiser la suppression de vieux enregistrement sur la Freebox.

# Pré-requis

Ce script nécessite Python 3 et utilise les bibliothèques requests et dateutils.

# Installation

```bash
git clone https://github.com/glops/freebox-purge-records
cd freebox-purge-records
pip install -r requirements.txt
```

# Paramétrage du délais de purge

Ajouter un nom secondaire à l'enregistrement de la forme : 'suppression : n jours|semaines|mois'

Le nom secondaire peut-être ajouter dans le générateur, ou directement sur l'enregistrement terminé.

![Modifier un générateur](https://github.com/glops/freebox-purge-records/blob/master/img/generator.png?raw=true)


# Exécution

```bash
python purge_records.py
```

Lors de la 1ère exécution, un message apparaît sur l'écran du boîtier Freebox serveur pour autoriser l'application à contrôler la Freebox. Appuyer sur OK.

Vous pouvez également ajouter le tag --simulation pour simuler l'exécution, sans rien supprimer.

```bash
python purge_records.py --simulation
```

Une log détaillée apparaît :

```
2020-07-15T22:05:41 - PurgeRecords.PurgeRecords - DEBUG - ##################
2020-07-15T22:05:41 - PurgeRecords.PurgeRecords - DEBUG - id: 4336
2020-07-15T22:05:41 - PurgeRecords.PurgeRecords - DEBUG - name: Le plus beau pays du monde
2020-07-15T22:05:41 - PurgeRecords.PurgeRecords - DEBUG - subname:
2020-07-15T22:05:41 - PurgeRecords.PurgeRecords - DEBUG - end: 2020-04-21 22:47:00
2020-07-15T22:05:41 - PurgeRecords.PurgeRecords - DEBUG - Pas d'instruction de suppression
2020-07-15T22:05:41 - PurgeRecords.PurgeRecords - DEBUG - ##################
2020-07-15T22:05:41 - PurgeRecords.PurgeRecords - DEBUG - id: 4612
2020-07-15T22:05:41 - PurgeRecords.PurgeRecords - DEBUG - name: Journal
2020-07-15T22:05:41 - PurgeRecords.PurgeRecords - DEBUG - subname: delete: 3 days
2020-07-15T22:05:41 - PurgeRecords.PurgeRecords - DEBUG - end: 2020-07-13 21:00:00
2020-07-15T22:05:41 - PurgeRecords.PurgeRecords - DEBUG - number: 3
2020-07-15T22:05:41 - PurgeRecords.PurgeRecords - DEBUG - unit: day
2020-07-15T22:05:41 - PurgeRecords.PurgeRecords - DEBUG - Ne pas supprimer pour le moment
2020-07-15T22:05:41 - PurgeRecords.PurgeRecords - DEBUG - Sera supprimé après 2020-07-16 21:00:00
```


# Erreurs

Si le message "Erreur lors de la récupération du token" apparait dans les logs, vous pouvez essayer de supprimer les 2 fichiers du répertoire conf et relancer le script pour recommencer la procédure d'autorisation.
