from functools import lru_cache

import geopandas as gpd
import pandas as pd
from linkedin_dashboard.settings.settings import get_settings
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split

from project.linkedin_dashboard.Enums.dataset_enum import DatasetName

global_datasets = {}


@lru_cache(maxsize=128)
def get_global_dataset(dataset_name: str) -> pd.DataFrame:
    """
    Atualiza a variável global com um dataset tratado.

    :param dataset_name: Nome do dataset (chave) para atualização.
    :param df: DataFrame processado.
    """
    global global_datasets
    return global_datasets.get(dataset_name, None)


def add_global_dataset(dataset_name: str, df: pd.DataFrame):
    """
    Atualiza a variável global com um dataset tratado.

    :param dataset_name: Nome do dataset (chave) para atualização.
    :param df: DataFrame processado.
    """
    global global_datasets
    global_datasets[dataset_name] = df


def get_dataset(csv_path: str) -> pd.DataFrame:
    """
    Loads a dataset from a provided CSV file.

    :param csv_path: Path to the CSV file.
    :return: DataFrame with the content of the CSV file.
    """
    try:
        return pd.read_csv(csv_path, nrows=3000)
    except FileNotFoundError:
        print(f"Error: File not found at the path: {csv_path}")
        raise
    except pd.errors.EmptyDataError:
        print(f"Error: CSV file is empty: {csv_path}")
        raise
    except Exception as e:
        print(f"Error loading the CSV file: {e}")
        raise


def process_job_postings():
    """
    Loads and processes job postings data, merging it with job skills.

    :return: Processed DataFrame of job postings.
    """
    settings = get_settings()

    job_postings_df = get_dataset(settings.dataset_settings.job_postings_path)
    job_skills_df = get_dataset(settings.dataset_settings.job_skills_path)
    company_specialities_df = get_dataset(
        settings.dataset_settings.company_specialities_path)

    job_postings_df = job_postings_df.merge(company_specialities_df,
                                            on="company_id",
                                            how="left")

    job_postings_df = merge_skills_with_jobs(job_postings_df, job_skills_df)

    #job_postings_df = remove_unused_columns(job_postings_df)

    job_postings_df = process_postings_data(job_postings_df)

    geolocation_df = load_geolocation_data(
        settings.geo_settings.united_states_geo)

    job_postings_df[[
        'city', 'state'
    ]] = job_postings_df['location'].apply(split_location).apply(pd.Series)

    job_postings_df = merge_geolocation_with_jobs(job_postings_df,
                                                  geolocation_df)

    add_global_dataset(DatasetName.JOB_POSTINGS, job_postings_df)

    return job_postings_df


def merge_skills_with_jobs(job_postings_df: pd.DataFrame,
                           job_skills_df: pd.DataFrame) -> pd.DataFrame:
    """Merges job skills with job postings."""
    job_skills_df = job_skills_df.groupby('job_id')['skill_abr'].agg(
        lambda x: ', '.join(x)).reset_index()
    job_postings_df = job_postings_df.merge(job_skills_df,
                                            on="job_id",
                                            how="left")
    job_postings_df['skill_abr'] = job_postings_df['skill_abr'].fillna('')
    return job_postings_df


def process_postings_data(job_postings_df: pd.DataFrame) -> pd.DataFrame:
    """Processes job postings data: handling missing values, salary, and adding year."""
    job_postings_df = process_salary(job_postings_df)
    job_postings_df = handle_missing_values(job_postings_df)
    # job_postings_df = process_salary2(job_postings_df)
    job_postings_df['remote_allowed'] = job_postings_df[
        'remote_allowed'].fillna(0)
    job_postings_df['is_remote'] = job_postings_df['remote_allowed'].apply(
        lambda x: 'Remota' if x == 1 else 'Não Remota')

    job_postings_df['listed_time_y_m_d'] = pd.to_datetime(
        job_postings_df['listed_time'] / 1000, unit='s')
    job_postings_df['year'] = job_postings_df['listed_time_y_m_d'].dt.year
    return job_postings_df


def remove_unused_columns(job_postings_df: pd.DataFrame) -> pd.DataFrame:
    """Removes unused columns from the job postings dataframe."""
    cols_to_remove = [
        'At scraping time',
        'job_posting_url',
        'application_url',
        'application_type',
        'expiry',
        'closed_time',
        'posting_domain',
        'sponsored',
        'currency',
        'compensation_type',
        'zip_code',
        'fips',
        'views',
        'description',
    ]
    return job_postings_df.drop(columns=cols_to_remove, errors='ignore')


@lru_cache
def get_skill_dict() -> dict:
    """
    Loads and creates a skill dictionary mapping skill names to their abbreviations.

    :return: Dictionary mapping skill names to abbreviations.
    """
    settings = get_settings()
    df_skills = get_dataset(settings.dataset_settings.skills_path)

    skill_dict = dict(zip(df_skills['skill_name'], df_skills['skill_abr']))

    return skill_dict


@lru_cache
def get_skill_names() -> list:
    """
    Loads the list of skill names.

    :return: List of skill names.
    """
    settings = get_settings()
    df_skills = get_dataset(settings.dataset_settings.skills_path)

    skill_names = df_skills['skill_name'].tolist()

    return skill_names


def handle_missing_values(df: pd.DataFrame) -> None:
    """
    Fills missing values in the job postings DataFrame for specified columns.

    :param df: The DataFrame containing job postings data.
    """
    cols_fill_not_specified = [
        'skills_desc', 'applies', 'formatted_experience_level', 'company_name'
    ]
    cols_fill_zero = ['applies', 'company_id', 'views']

    df[cols_fill_not_specified] = df[cols_fill_not_specified].fillna(
        "Not Specified")
    df[cols_fill_zero] = df[cols_fill_zero].fillna(0)

    df['max_salary'] = df['max_salary'].fillna(df['max_salary'].mean())
    df['med_salary'] = df['med_salary'].fillna(df['med_salary'].median())
    df['min_salary'] = df['min_salary'].fillna(df['min_salary'].min())
    if not df['company_name'].isnull().all():
        df['company_name'] = df['company_name'].fillna(
            df['company_name'].mode()[0])

    return df


def split_location(location: str):
    if ',' in location:
        state = location.split(', ')[-1].strip()
        city = location.split(', ')[0].strip()
    else:
        state = location
        city = None
    return city, state


def process_salary(df: pd.DataFrame):
    df[['max_salary', 'min_salary', 'pay_period']] = df.apply(
        lambda row: (
            # Caso o pay_period seja 'HOURLY'
            ((row['max_salary'] * 44) * 4) * 12,
            ((row['min_salary'] * 44) * 4) * 12,
            'YEARLY') if row['pay_period'] == 'HOURLY' else (
                # Caso o pay_period seja 'MONTHLY'
                row['max_salary'] * 12,
                row['min_salary'] * 12,
                'YEARLY') if row['pay_period'] == 'MONTHLY' else (
                    # Caso contrário, mantenha os valores originais
                    row['max_salary'],
                    row['min_salary'],
                    row['pay_period']),
        axis=1,
        result_type='expand')
    df['calculated_med_salary'] = (df['max_salary'] + df['min_salary']) / 2
    df['med_salary'] = df.apply(lambda row:
                                (row['max_salary'] + row['min_salary']) / 2
                                if row['med_salary'] <= 0 or row['med_salary']
                                is None else row['med_salary'],
                                axis=1)
    df['med_salary'] = df['med_salary'].round(-3)
    return df


def process_salary2(df: pd.DataFrame):
    # Condições para transformar os valores com base no pay_period
    is_hourly = df['pay_period'] == 'HOURLY'
    is_monthly = df['pay_period'] == 'MONTHLY'

    # Cálculos para 'HOURLY' e 'MONTHLY'
    df.loc[is_hourly, ['max_salary', 'min_salary']] = df.loc[
        is_hourly, ['max_salary', 'min_salary']] * 44 * 4 * 12
    df.loc[is_monthly, ['max_salary', 'min_salary']] = df.loc[
        is_monthly, ['max_salary', 'min_salary']] * 12

    # Atualizar 'pay_period' para 'YEARLY' onde for 'HOURLY' ou 'MONTHLY'
    df.loc[is_hourly | is_monthly, 'pay_period'] = 'YEARLY'

    # Calcular média salarial
    df['calculated_med_salary'] = (df['max_salary'] + df['min_salary']) / 2

    # Substituir valores de 'med_salary' se nulo ou menor ou igual a zero
    df['med_salary'] = df['med_salary'].where(df['med_salary'] > 0,
                                              df['calculated_med_salary'])

    # Arredondar 'med_salary' para o milhar mais próximo
    df['med_salary'] = df['med_salary'].round(-3)

    return df


def filter_by_skills(df, selected_skills):
    """
    Filters job postings by selected skills.

    :param df: DataFrame containing job postings data.
    :param selected_skills: List of selected skills to filter by.
    :return: Filtered DataFrame.
    """
    if selected_skills:
        filtered_df = df[df['skill_abr'].apply(
            lambda x: any(skill in x for skill in selected_skills))]
    else:
        filtered_df = df
    return filtered_df


def get_remote_distribution(df: pd.DataFrame) -> list:
    """
    Calculates the distribution of remote and non-remote job postings.

    :param df: DataFrame containing job postings data.
    :return: DataFrame with the count of remote and non-remote postings.
    """
    remote_counts = df['is_remote'].value_counts().reset_index()
    remote_counts.columns = ['Tipo', 'Contagem']
    return remote_counts


def get_salary_means(df: pd.DataFrame) -> list:
    """
    Calculates the average salary for remote and non-remote job postings.

    :param df: DataFrame containing job postings data.
    :return: DataFrame with the average salary for remote and non-remote jobs.
    """
    salary_means = df.groupby('is_remote')['med_salary'].mean().reset_index()
    salary_means.columns = ['Tipo', 'Média Salarial']
    return salary_means


def load_geolocation_data(json_path: str) -> pd.DataFrame:
    """
    Load geolocation data from a JSON file.

    :param json_path: Path to the JSON file containing geolocation data.
    :return: DataFrame with geolocation data.
    """
    return gpd.read_file(json_path)


def merge_geolocation_with_jobs(
        job_postings_df: pd.DataFrame,
        geolocation_gdf: gpd.GeoDataFrame) -> pd.DataFrame:
    """
    Merge job postings with geolocation data.

    :param job_postings_df: DataFrame of job postings.
    :param geolocation_df: DataFrame of geolocation data.
    :return: Merged DataFrame with job postings and geolocation.
    """
    geolocation_gdf['state'] = geolocation_gdf['name']
    return job_postings_df.merge(geolocation_gdf[['state', 'geometry']],
                                 on='state',
                                 how='left')


def train_job_posting_model(df: pd.DataFrame):
    print(df.isnull().sum())
    X = df[['med_salary', 'views', 'listed_time']]
    y = df['views'] * 0.8

    X_train, X_test, y_train, y_test = train_test_split(X,
                                                        y,
                                                        test_size=0.2,
                                                        random_state=42)

    model = LinearRegression()
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    print(f"Mean Squared Error: {mse}")

    return model


def predict_job_postings_2025(model, df: pd.DataFrame):
    df_2025 = df.copy(deep=True)
    df_2025['year'] = 2025

    X_2025 = df_2025[['med_salary', 'views', 'listed_time']]
    df_2025['predicted_postings'] = model.predict(X_2025)
    df_2025['predicted_postings'] = df_2025['predicted_postings'].round(
        0).astype(int)

    return df_2025
