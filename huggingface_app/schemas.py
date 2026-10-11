from typing import Annotated, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


Rating = Annotated[float, Field(ge=0, le=100, allow_inf_nan=False)]


class TeamInput(BaseModel):
    """Raw squad and tactical attributes required by the profiler."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    team_name: Optional[str] = Field(default=None, max_length=120)
    avg_overall_rating: Rating
    avg_potential: Rating
    goalkeeper_rating: Rating
    avg_pace: Rating
    avg_physical: Rating
    avg_defence: Rating
    avg_attack: Rating
    buildUpPlaySpeed: Rating
    buildUpPlayPassing: Rating
    chanceCreationPassing: Rating
    chanceCreationCrossing: Rating
    chanceCreationShooting: Rating
    defencePressure: Rating
    defenceAggression: Rating
    defenceTeamWidth: Rating

    @field_validator("team_name")
    @classmethod
    def empty_team_name_is_optional(cls, value: Optional[str]) -> Optional[str]:
        return value or None


class PredictionResponse(BaseModel):
    team_name: str
    cluster: int
    team_profile: str
    distance_to_centroid: float
    description: str


class ProfileResponse(BaseModel):
    cluster: int
    name: str
    description: str


class BatchPredictionResponse(BaseModel):
    count: int
    results: list[PredictionResponse]
