#!/bin/bash
#SBATCH --job-name=sqlbuildquery
#SBATCH --output=output.log
#SBATCH --error=error.log
#SBATCH --time=00:10:00       # max runtime hh:mm:ss
#SBATCH --mem=2G              # RAM pro Node
#SBATCH --cpus-per-task=2     # CPUs
#SBATCH --partition=standard  # Partition / Queue des Clusters

# Optional: Python-Modul laden
module load python

# Optional: virtuelle Umgebung aktivieren
# source venv/bin/activate

# In den Projektordner wechseln
cd $HOME/sqlbuildqueryllm

# Python-Skript starten
python3 main.py