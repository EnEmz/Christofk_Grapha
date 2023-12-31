#!/bin/bash
project_path="$HOME/Desktop/Christofk_Grapha"

echo "Checking if Python is installed..."
if ! command -v python3 &> /dev/null
then
  echo "Python is not installed. Please install Python and rerun this script."
  exit
fi

echo "Creating a virtual environment..."
cd "$project_path"
python3 -m venv venv

echo "Activating the virtual environment..."
source "$project_path/venv/bin/activate"

echo "Installing dependencies from requirements.txt..."
pip install -r requirements.txt

echo "Deativating the virtual environment..."
source "$project_path/venv/bin/deactivate"

echo "Setup is complete!"
read -p "Press any key to continue..."