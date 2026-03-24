from typing import Literal, Optional

from fastapi.encoders import jsonable_encoder
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse, JSONResponse
from jobspy import scrape_jobs
from pandas import DataFrame
import math
from pathlib import Path


app = FastAPI(
    title="LinkedIn Tech Jobs API",
    description="Fetch tech-focused job listings from LinkedIn via JobSpy.",
    version="1.0.0",
)
BASE_DIR = Path(__file__).resolve().parent

SupportedSite = Literal[
    "linkedin",
    "indeed",
    "zip_recruiter",
    "glassdoor",
    "google",
    "bayt",
    "naukri",
    "bdjobs",
]


def dataframe_to_response(jobs_df: DataFrame) -> list[dict]:
    """
    Convert a pandas DataFrame into JSON-serializable dicts.
    NaN values become None.
    """
    normalized_df = jobs_df.where(jobs_df.notna(), None)
    return normalized_df.to_dict(orient="records")


def sanitize_for_json(value):
    """
    Recursively convert non-JSON-safe values into safe equivalents.
    In particular, JSON disallows NaN/Infinity, so map them to None.
    """
    if isinstance(value, float) and not math.isfinite(value):
        return None
    if isinstance(value, dict):
        return {k: sanitize_for_json(v) for k, v in value.items()}
    if isinstance(value, list):
        return [sanitize_for_json(item) for item in value]
    return value


@app.get("/health")
def health_check() -> dict:
    return {"status": "ok"}


@app.get("/")
def home() -> FileResponse:
    return FileResponse(BASE_DIR / "static" / "index.html")


@app.get("/jobs")
def get_linkedin_jobs(
    site_name: list[SupportedSite] = Query(
        default=["linkedin"],
        description=(
            "One or more job sources. Supported values: "
            "linkedin, indeed, zip_recruiter, glassdoor, google, bayt, naukri, bdjobs."
        ),
    ),
    search_term: str = Query(
        default="software engineer",
        description="Keywords for job search (example: backend engineer, data engineer).",
    ),
    location: str = Query(
        default="United States",
        description="Location to search jobs in.",
    ),
    results_wanted: int = Query(
        default=20,
        ge=1,
        le=100,
        description="Number of job listings to fetch (1-100).",
    ),
    hours_old: Optional[int] = Query(
        default=72,
        ge=1,
        le=720,
        description="Fetch jobs posted in the last N hours.",
    ),
    linkedin_fetch_description: bool = Query(
        default=False,
        description="Whether to fetch full LinkedIn descriptions (slower).",
    ),
) -> JSONResponse:
    try:
        jobs_df = scrape_jobs(
            site_name=site_name,
            search_term=search_term,
            location=location,
            results_wanted=results_wanted,
            hours_old=hours_old,
            linkedin_fetch_description=linkedin_fetch_description,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch jobs from JobSpy for sites {site_name}: {exc}",
        ) from exc

    jobs = sanitize_for_json(dataframe_to_response(jobs_df))
    return JSONResponse(
        content=jsonable_encoder(
            {
            "count": len(jobs),
            "source": site_name,
            "search_term": search_term,
            "location": location,
            "jobs": jobs,
            }
        )
    )
