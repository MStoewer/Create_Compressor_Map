# Create_Compressor_Map

Das ist das GitHub Repo zur Überarbeitung des Python-Skripts "Create_Compressor_Map.py"

- TRACE_entry.input: Datei mit Eintrittsrandbedingungen
- TRACE_job.dat: Dort werden alle Infos von TRACE/GMC reingeschrieben bezüglich des ausgeführten Jobs (beim alten Cluster)
- job_TRACE_alt.sh: Job-Skript für das alte Cluster
- job_TRACE_neu.sh: Job-Skript für das neue Cluster (SLURM)
- log.run: Dort werden alle Infos von TRACE/GMC reingeschrieben bezüglich des ausgeführten Jobs (beim neuen Cluster: SLURM)
- Create_Compressor_Map_alt.py: Für SLURM angepasstes Skript. Problem: Kennlinien-Berechnung wird nicht fortgesetzt für nächsten Betriebspunkt
- 220614_stoewer_Create_Compressor_Map.py: Versuch die Kennlinienberechnung fortzuführen (Stand: 14.06.22) (noch nicht richtig)



