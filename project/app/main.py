import pandas as pd
import dash
from project.app.settings.settings import get_settings

settings = get_settings()

df_position = pd.read_csv('app/data/job_skills.csv', nrows=200)
df_summary = pd.read_csv('app/data/job_summary.csv', nrows=200)
df_skills = pd.read_csv('app/data/job_skills.csv', nrows=200)


app = dash.Dash(__name__)

if __name__ == '__main__':
    app.run_server(debug=True if settings.env_settings.env == 'DEV' else False)
