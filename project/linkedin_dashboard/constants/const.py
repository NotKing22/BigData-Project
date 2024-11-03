from project.linkedin_dashboard.Enums.dataset_enum import DatasetName


ALL_STATES = [
        "AL",  # Alabama
        "AK",  # Alaska
        "AZ",  # Arizona
        "AR",  # Arkansas
        "CA",  # California
        "CO",  # Colorado
        "CT",  # Connecticut
        "DE",  # Delaware
        "DC",  # District of Columbia
        "FL",  # Florida
        "GA",  # Georgia
        "HI",  # Hawaii
        "ID",  # Idaho
        "IL",  # Illinois
        "IN",  # Indiana
        "IA",  # Iowa
        "KS",  # Kansas
        "KY",  # Kentucky
        "LA",  # Louisiana
        "ME",  # Maine
        "MD",  # Maryland
        "MA",  # Massachusetts
        "MI",  # Michigan
        "MN",  # Minnesota
        "MS",  # Mississippi
        "MO",  # Missouri
        "MT",  # Montana
        "NE",  # Nebraska
        "NV",  # Nevada
        "NH",  # New Hampshire
        "NJ",  # New Jersey
        "NM",  # New Mexico
        "NY",  # New York
        "NC",  # North Carolina
        "ND",  # North Dakota
        "OH",  # Ohio
        "OK",  # Oklahoma
        "OR",  # Oregon
        "PA",  # Pennsylvania
        "RI",  # Rhode Island
        "SC",  # South Carolina
        "SD",  # South Dakota
        "TN",  # Tennessee
        "TX",  # Texas
        "UT",  # Utah
        "VT",  # Vermont
        "VA",  # Virginia
        "WA",  # Washington
        "WV",  # West Virginia
        "WI",  # Wisconsin
        "WY",  # Wyoming
        "PR"  # Puerto Rico
    ]


GLOBAL_DATASETS = {}

SKILLS_LIST = ["DSGN", "PRDM", "QA", "IT"]
SKILLS_WITH_DATASET_MAPPING = {
        "DSGN": DatasetName.PREDICT_JOB_POSTINGS_DSGN,
        "PRDM": DatasetName.PREDICT_JOB_POSTINGS_PRDM,
        "QA": DatasetName.PREDICT_JOB_POSTINGS_QA,
        "IT": DatasetName.PREDICT_JOB_POSTINGS_IT
    }
CACHED_PROCESSED_DF = None
