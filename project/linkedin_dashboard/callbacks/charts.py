from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
from linkedin_dashboard.process.process_data import filter_by_skills, get_global_dataset, get_remote_distribution, get_salary_means, process_job_postings
from project.linkedin_dashboard.Enums.dataset_enum import DatasetName
from project.linkedin_dashboard.process import process_data


def create_callbacks(app):
    @app.callback(
        Output('remote-job-pie-chart', 'figure'),
        [Input('skill-dropdown', 'value'), Input('interval-component', 'n_intervals')]
    )
    def update_pie_chart(selected_skills, n_intervals):
        if (df := get_global_dataset(DatasetName.JOB_POSTINGS)) is None:
            df = process_job_postings()
            
        filtered_df = filter_by_skills(df, selected_skills)
        remote_counts = get_remote_distribution(filtered_df)
        fig = px.pie(remote_counts, values='Contagem', names='Tipo', title='Distribuição de Vagas Remotas e Não Remotas')
        return fig

    @app.callback(
        Output('salary-bar-chart', 'figure'),
        [Input('skill-dropdown', 'value'), Input('interval-component', 'n_intervals')]
    )
    def update_salary_bar_chart(selected_skills, n_intervals):
        if (df := get_global_dataset(DatasetName.JOB_POSTINGS)) is None:
            df = process_job_postings()
            
        filtered_df = filter_by_skills(df, selected_skills)
        salary_means = get_salary_means(filtered_df)
        fig = px.bar(salary_means, x='Tipo', y='Média Salarial', title='Média Salarial: Vagas Remotas vs Não Remotas')
        return fig


    @app.callback(
        Output("graph", "figure"), 
        [Input("dropdown", "value"), Input('skill-dropdown', 'value'), Input('interval-component', 'n_intervals')])
    def display_position(cargo, selected_skills, n_intervals):
        if (df := get_global_dataset(DatasetName.JOB_POSTINGS)) is None:
            df = process_job_postings()
        df = filter_by_skills(df, selected_skills)
        df = df[df["title"].str.contains(cargo, case=False, na=False)]
        median_salaries=df[["formatted_experience_level", "med_salary"]].groupby("formatted_experience_level").median().reset_index()
        fig = go.Figure(
            data=go.Bar(x=median_salaries["formatted_experience_level"],
                        y=median_salaries["med_salary"],
                        textposition='outside'))
        return fig
