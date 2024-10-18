import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash.dependencies import Input, Output
from linkedin_dashboard.process.process_data import (
    add_global_dataset, filter_by_skills, get_global_dataset,
    get_remote_distribution, get_salary_means, load_geolocation_data,
    merge_geolocation_with_jobs, predict_job_postings_2025,
    process_job_postings)

from project.linkedin_dashboard.Enums.dataset_enum import DatasetName
from project.linkedin_dashboard.settings.settings import get_settings


def create_callbacks(app):

    @app.callback(Output('remote-job-pie-chart', 'figure'), [
        Input('skill-dropdown', 'value'),
    ])
    def update_pie_chart(selected_skills):
        if (df := get_global_dataset(DatasetName.JOB_POSTINGS)) is None:
            df = process_job_postings()

        filtered_df = filter_by_skills(df, selected_skills)
        remote_counts = get_remote_distribution(filtered_df)
        fig = px.pie(remote_counts,
                     values='Contagem',
                     names='Tipo',
                     title='Distribuição de Vagas Remotas e Não Remotas')
        return fig

    @app.callback(Output('salary-bar-chart', 'figure'), [
        Input('skill-dropdown', 'value'),
    ])
    def update_salary_bar_chart(selected_skills):
        if (df := get_global_dataset(DatasetName.JOB_POSTINGS)) is None:
            df = process_job_postings()

        filtered_df = filter_by_skills(df, selected_skills)
        salary_means = get_salary_means(filtered_df)
        fig = px.bar(salary_means,
                     x='Tipo',
                     y='Média Salarial',
                     title='Média Salarial: Vagas Remotas vs Não Remotas')
        return fig

    @app.callback(Output("graph", "figure"), [
        Input("dropdown", "value"),
        Input('skill-dropdown', 'value'),
    ])
    def display_position(cargo, selected_skills):
        if (df := get_global_dataset(DatasetName.JOB_POSTINGS)) is None:
            df = process_job_postings()
        df = filter_by_skills(df, selected_skills)
        df = df[df["title"].str.contains(cargo, case=False, na=False)]
        median_salaries = df[[
            "formatted_experience_level", "med_salary"
        ]].groupby("formatted_experience_level").median().reset_index()

        fig = go.Figure(
            data=go.Bar(x=median_salaries["formatted_experience_level"],
                        y=median_salaries["med_salary"],
                        textposition='outside'))
        return fig

    @app.callback(Output('job-postings-2025-map', 'figure'),
                  [Input('skill-dropdown', 'value')])
    def update_map(selected_skills):
        settings = get_settings()
        geolocation_gdf = load_geolocation_data(
            settings.geo_settings.united_states_geo)

        if (predict_job_df := get_global_dataset(
                DatasetName.PREDICT_JOB_POSTINGS_2025)) is None:

            if (job_postings_df :=
                    get_global_dataset(DatasetName.JOB_POSTINGS)) is None:
                job_postings_df = process_job_postings()

            df_2025 = predict_job_postings_2025(job_postings_df)

            predict_job_df = merge_geolocation_with_jobs(
                df_2025, geolocation_gdf)
            add_global_dataset(DatasetName.PREDICT_JOB_POSTINGS_2025,
                               pd.DataFrame(predict_job_df))

        predict_job_df = filter_by_skills(predict_job_df, selected_skills)

        fig = px.choropleth(
            predict_job_df,
            locations='state',
            geojson=geolocation_gdf,
            featureidkey='properties.name',
            color='predicted_postings',
            hover_name='state',
            color_continuous_scale='PuBu',
            labels={'predicted_postings': 'Vagas Previstas'},
            title='Previsão de Vagas em 2025 por Estado nos EUA',
            range_color=(min(predict_job_df['predicted_postings'])
                         or 0, max(predict_job_df['predicted_postings'])))

        fig.update_geos(fitbounds="locations",
                        visible=False,
                        center={
                            "lat": 37.1,
                            "lon": -95.7
                        },
                        projection_type="albers usa",
                        projection_scale=2)

        fig.update_layout(coloraxis_colorbar=dict(
            titleside='right',
            ticks='outside',
        ),
                          template=None)

        return fig

    # @app.callback(Output('job-postings-2025-map', 'figure'),
    #           [Input('interval-component', 'n_intervals')])
    # def update_map(n_intervals):
    #     if (df := get_global_dataset(DatasetName.JOB_POSTINGS)) is None:
    #         df = process_job_postings()

    #     # Adiciona latitude e longitude
    #     df = add_geolocation_to_jobs(df)

    #     print(df.columns.to_list())
    #     settings = get_settings()
    #     model = train_job_posting_model(df)
    #     df_2025 = predict_job_postings_2025(model, df)

    #     # Adiciona latitude e longitude a df_2025 também
    #     df_2025 = add_geolocation_to_jobs(df_2025)

    #     # Agora você pode criar um gráfico baseado em df_2025 e as novas colunas latitude/longitude
    #     fig = px.scatter_mapbox(
    #         df_2025,
    #         lat='latitude',
    #         lon='longitude',
    #         color='predicted_postings',
    #         hover_name='location',
    #         color_continuous_scale=px.colors.sequential.Viridis,
    #         title='Previsão de Vagas em 2025 por Localização',
    #         mapbox_style='carto-positron',
    #         zoom=3,
    #         center={"lat": 37.1, "lon": -95.7}
    #     )

    #     fig.update_layout(coloraxis_colorbar=dict(
    #         titleside='right',
    #         ticks='outside',
    #     ),
    #     template=None)

    #     return fig
