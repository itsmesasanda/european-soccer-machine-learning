from io import BytesIO
from pathlib import Path

import pandas as pd
from fastapi import FastAPI, File, HTTPException, Request, UploadFile
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .predictor import REQUIRED_COLUMNS, predict_team_profiles, profile_names
from .schemas import (
    BatchPredictionResponse,
    PredictionResponse,
    ProfileResponse,
    TeamInput,
)


APP_DIR = Path(__file__).resolve().parent
EXAMPLE_CSV = APP_DIR / "examples" / "example_team_data.csv"

PROFILE_DESCRIPTIONS = {
    0: (
        "Above-average defensive and physical characteristics with relatively "
        "stronger build-up passing and lower defensive pressure."
    ),
    1: (
        "Characterised by higher defensive pressure, aggression, defensive "
        "width and crossing-related tactical attributes."
    ),
    2: (
        "Above-average squad quality and pace with a more attack-oriented "
        "balance and distinctive lower build-up speed/passing characteristics."
    ),
    3: (
        "Characterised by below-average overall squad quality, pace, physical "
        "ability and defensive strength."
    ),
    4: (
        "Very strong overall squad quality, pace, physical ability, defensive "
        "quality and chance-creation shooting."
    ),
}

app = FastAPI(
    title="Football Team Performance Profiler",
    description=(
        "Assign football teams to one of five historical archetypes using a "
        "saved K-Means model. This is profile assignment, not future match prediction."
    ),
    version="1.0.0",
)
app.mount("/static", StaticFiles(directory=APP_DIR / "static"), name="static")
templates = Jinja2Templates(directory=APP_DIR / "templates")


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    errors = []
    for error in exc.errors():
        field = ".".join(str(part) for part in error["loc"] if part != "body")
        errors.append(
            {
                "field": field or "request",
                "message": error["msg"],
            }
        )

    return JSONResponse(
        status_code=422,
        content={"detail": "Input validation failed.", "errors": errors},
    )


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def homepage(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"required_columns": REQUIRED_COLUMNS},
    )


@app.get("/health", tags=["System"])
async def health() -> dict:
    return {
        "status": "ok",
        "model": "K-Means Team Profiler",
        "profiles": 5,
    }


@app.get("/profiles", response_model=list[ProfileResponse], tags=["Profiles"])
async def profiles() -> list[ProfileResponse]:
    return [
        ProfileResponse(
            cluster=cluster,
            name=profile_names[str(cluster)],
            description=PROFILE_DESCRIPTIONS[cluster],
        )
        for cluster in range(5)
    ]


def _result_records(data: pd.DataFrame) -> list[dict]:
    results = predict_team_profiles(data)
    records = []

    for row in results.itertuples(index=False):
        cluster = int(row.cluster)
        records.append(
            {
                "team_name": str(row.team_name),
                "cluster": cluster,
                "team_profile": str(row.team_profile),
                "distance_to_centroid": float(row.distance_to_centroid),
                "description": PROFILE_DESCRIPTIONS[cluster],
            }
        )

    return records


@app.post("/predict", response_model=PredictionResponse, tags=["Predictions"])
async def predict(payload: TeamInput) -> dict:
    row = payload.model_dump()
    if row["team_name"] is None:
        row.pop("team_name")

    try:
        return _result_records(pd.DataFrame([row]))[0]
    except (TypeError, ValueError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.post(
    "/predict-csv",
    response_model=BatchPredictionResponse,
    tags=["Predictions"],
)
async def predict_csv(file: UploadFile = File(...)) -> dict:
    filename = file.filename or ""
    if not filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Please upload a .csv file.")

    contents = await file.read()
    await file.close()

    if not contents.strip():
        raise HTTPException(status_code=400, detail="The uploaded CSV file is empty.")

    try:
        data = pd.read_csv(BytesIO(contents))
    except (pd.errors.EmptyDataError, pd.errors.ParserError, UnicodeDecodeError) as exc:
        raise HTTPException(
            status_code=400,
            detail="The uploaded file could not be read as a valid CSV.",
        ) from exc

    if data.empty:
        raise HTTPException(
            status_code=400,
            detail="The uploaded CSV contains no team data rows.",
        )

    try:
        records = _result_records(data)
    except (TypeError, ValueError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    return {"count": len(records), "results": records}


@app.get("/example-csv", response_class=FileResponse, tags=["Downloads"])
async def example_csv() -> FileResponse:
    return FileResponse(
        path=EXAMPLE_CSV,
        media_type="text/csv",
        filename="example_team_data.csv",
    )
