from functools import lru_cache
import pandas as pd

from linkedin_dashboard.settings.settings import get_settings
from project.linkedin_dashboard.Enums.dataset_enum import DatasetName 

global_datasets = {}

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
        return pd.read_csv(csv_path)
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
    
    job_skills_df = job_skills_df.groupby('job_id')['skill_abr'].agg(lambda x: ', '.join(x)).reset_index()
    job_postings_df = job_postings_df.merge(job_skills_df, on="job_id", how="left")
    
    job_postings_df['skill_abr'] = job_postings_df['skill_abr'].fillna('')
    
    handle_missing_values(job_postings_df)
    process_salary(job_postings_df)
    
    add_global_dataset(DatasetName.JOB_POSTINGS, job_postings_df)
    
    return job_postings_df

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
    cols_fill_not_specified = ['skills_desc', 'pay_period', 'currency', 'compensation_type', 
                               'posting_domain', 'application_url', 'formatted_experience_level', 
                               'zip_code',]
    cols_fill_zero = ['applies', 'views']
    
    df[cols_fill_not_specified] = df[cols_fill_not_specified].fillna("Not Specified")
    df[cols_fill_zero] = df[cols_fill_zero].fillna(0)
    
    df['remote_allowed'] = df['remote_allowed'].fillna(0)
    df['is_remote'] = df['remote_allowed'].apply(lambda x: 'Remota' if x == 1 else 'Não Remota')
    

def process_salary(df: pd.DataFrame):
    df[['max_salary', 'min_salary', 'pay_period']] = df.apply(
        lambda row:(
            # Caso o pay_period seja 'HOURLY'
            ((row['max_salary'] * 44) * 4) * 12,
            ((row['min_salary'] * 44) * 4) * 12,
            'YEARLY'
        ) if row['pay_period'] == 'HOURLY' else (
            # Caso o pay_period seja 'MONTHLY'
            row['max_salary'] * 12,
            row['min_salary'] * 12,
            'YEARLY'
        ) if row['pay_period'] == 'MONTHLY' else (
            # Caso contrário, mantenha os valores originais
            row['max_salary'],
            row['min_salary'],
            row['pay_period']
        ),
        axis=1,
        result_type='expand'
    )
    df['calculated_med_salary'] = (df['max_salary'] + df['min_salary']) / 2
    df['med_salary'] = df.apply(
        lambda row: (row['max_salary'] + row['min_salary']) / 2 
        if row['med_salary'] <= 0 else row['med_salary'],
        axis=1
    )
    df['med_salary'] = df['med_salary'].round(-3)


def filter_by_skills(df, selected_skills):
    """
    Filters job postings by selected skills.

    :param df: DataFrame containing job postings data.
    :param selected_skills: List of selected skills to filter by.
    :return: Filtered DataFrame.
    """
    if selected_skills:
        filtered_df = df[df['skill_abr'].apply(lambda x: any(skill in x for skill in selected_skills))]
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
