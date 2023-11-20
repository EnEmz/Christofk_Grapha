#!/bin/bash
echo "Shutting down the Dash app..."
lsof -i tcp:8050 | awk 'NR!=1 {print $2}' | xargs kill
echo "Server shut down."