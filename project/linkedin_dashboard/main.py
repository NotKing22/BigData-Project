import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

import dash
from project.linkedin_dashboard.settings.settings import get_settings
from project.linkedin_dashboard.callbacks.charts import create_callbacks
from linkedin_dashboard.layout.dashboard_layout import layout

app = dash.Dash(__name__)
create_callbacks(app)
settings = get_settings()
app.layout = layout

if __name__ == '__main__':
    app.run_server(debug=True if settings.env_settings.environment == 'DEV' else False)

