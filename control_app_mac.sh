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

    echo "Deactivating the virtual environment..."
    deactivate
}

case "$1" in 
    start)
        start_app
        ;;
    stop)
        stop_app
        ;;
    *)
        echo "Usage: $0 {start|stop}"
        exit 1
esac