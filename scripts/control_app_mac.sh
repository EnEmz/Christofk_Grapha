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
    unzip -o "$zip_file_name" -d "$project_path"

    echo "Replacing old files with new ones..."
    # This will handle nested directories and files correctly
    rsync -av --delete "$project_path/repo-main/" "$project_path/"

    echo "Removing temporary files..."
    rm -r "$project_path/repo-main"
    rm "$zip_file_name"

    echo "Updating Python dependencies..."
    source "$project_path/venv/bin/activate"
    pip install -r "$project_path/requirements.txt"
    deactivate

    echo "Update complete."
}

while true; do
    echo "Please type 'start' to run the app or 'stop' to stop it:"
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
            start_app
            ;;
        *)
            echo "Invalid input. Please type 'start' or 'stop'."
            ;;
    esac
done
