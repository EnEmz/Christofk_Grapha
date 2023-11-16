# index.py
# Dash app definition

from app import app, server
from content import create_layout

app.layout = create_layout()

import layout.callbacks

if __name__ == '__main__':
    app.run_server(
        debug=True, 
        use_reloader=True, 
        dev_tools_ui=True
        )