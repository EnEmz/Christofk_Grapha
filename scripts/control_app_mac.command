#!/bin/bash
scripts_path="$HOME/Desktop/Christofk_Grapha/scripts"
project_path="$HOME/Desktop/Christofk_Grapha"
repo_url="https://github.com/EnEmz/Christofk_Grapha"
zip_file_name="repo.zip"

start_app() {
    echo "Activating the virtual environment..."
    source "$project_path/venv/bin/activate"

    echo "Starting the Dash app..."
    python3 "$project_path/index.py" &

    echo "Opening the Dash app in the web browser..."
    sleep 10
    open http://127.0.0.1:8050/
}

stop_app() {
    echo "Shutting down the Dash app..."
    lsof -i tcp:8050 | awk 'NR!=1 {print $2}' | xargs kill
    echo "Server shut down."

    echo "Terminating all Python processes..."
    pkill -f python
}

update_app() {
    echo "Backing up the current application..."
    # Add backup code here if needed

    echo "Downloading the latest version of the app..."
    curl -L "${repo_url}/archive/main.zip" -o "$zip_file_name"

    echo "Unzipping the repository..."
    temp_dir="$project_path/temp_repo"
    mkdir -p "$temp_dir"
    unzip -o "$zip_file_name" -d "$temp_dir"

    extracted_dir=$(ls "$temp_dir" | head -1)
    full_extracted_path="$temp_dir/$extracted_dir"

    echo "Replacing old files with new ones from the repository..."
    rsync -av --exclude='.git' --exclude='venv' --exclude='scripts' "$full_extracted_path/" "$project_path/"

    echo "Removing temporary files..."
    rm -rf "$temp_dir"
    rm "$zip_file_name"

    echo "Updating Python dependencies..."
    source "$project_path/venv/bin/activate"
    pip install --upgrade pip  # Upgrading pip to the latest version
    pip install --upgrade setuptools
    pip install -r "$project_path/requirements.txt"
    deactivate

    echo "Update complete."
}

while true; do
    echo "-------------------------------------"
    echo "Please type 'start' to run the app."
    echo "Please type 'stop' to stop the app."
    echo "Please type 'update' to update the app."
    echo "-------------------------------------"

    read action

    case "$action" in 
        start)
            start_app
            ;;
        stop)
            stop_app
            break
            ;;
        update)
            stop_app
            update_app
            ;;
        *)
            echo "Invalid input. Please type 'start' or 'stop'."
            ;;
    esac
done
