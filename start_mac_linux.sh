#!/bin/bash
project_path="$HOME/Desktop/Christofk_Grapha"

echo "Activating the virtual environment..."
source "$project_path/venv/bin/activate"

echo "Starting the Dash app..."
python3 "$project_path/index.py" &

echo "Opening the Dash app in the web browser..."
sleep 10
open http://127.0.0.1:8050/

read -p "Press any key to continue..."