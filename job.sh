#!/bin/bash
#SBATCH --job-name=sqlbuildqueryllm
#SBATCH --output=slurm-%j.out
#SBATCH --error=slurm-%j.err
#SBATCH --constraint="gpu"
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem-per-cpu=2000M
#SBATCH --time=20:00:00

echo "Job gestartet auf $(hostname) um $(date)"

# Module laden
module purge
module load devel/python/3.11.7-gnu-14.2

# Virtuelle Umgebung nutzen oder erstellen, falls noch nicht vorhanden
VENV_DIR="$HOME/sqlbuildqueryllm/venv_sqlbuild"

if [ ! -d "$VENV_DIR" ]; then
    echo "Virtuelle Umgebung wird erstellt..."
    python -m venv "$VENV_DIR"
fi

# Umgebung aktivieren
source "$VENV_DIR/bin/activate"

# Bibliotheken installieren, falls noch nicht vorhanden
pip install --upgrade pip
pip install --upgrade --no-cache-dir -r requirements.txt

# Script ausführen
python -u main.py

echo "Job beendet um $(date)"