#!/bin/bash
project_path="$HOME/Desktop/Christofk_Grapha"

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
        *)
            echo "Invalid input. Please type 'start' or 'stop'."
            ;;
    esac
done
