# Create_Compressor_Map

Das ist das GitHub Repo zur Überarbeitung des Python-Skripts "Create_Compressor_Map.py"

- Create_Compressor_Map.py: Für SLURM angepasstes Skript. Problem: Kennlinien-Berechnung wird nicht fortgesetzt für nächsten Betriebspunkt
- 220614_stoewer_Create_Compressor_Map.py:
  - folgende Sachen wurden geändert:
  ![1](https://user-images.githubusercontent.com/92665372/173520829-420ff9f7-3975-4b99-bf58-0c6165495b33.png)
  - folgende Fehlermeldung ist aufgetreten:
  - 
- TRACE_entry.input: Datei mit Eintrittsrandbedingungen
- TRACE_job.dat: Dort werden alle Infos von TRACE/GMC reingeschrieben bezüglich des ausgeführten Jobs (beim alten Cluster)
- job_TRACE_alt.sh: Job-Skript für das alte Cluster
- job_TRACE_neu.sh: Job-Skript für das neue Cluster (SLURM)
- log.run: Dort werden alle Infos von TRACE/GMC reingeschrieben bezüglich des ausgeführten Jobs (beim neuen Cluster: SLURM)
