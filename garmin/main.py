import garth
from fastapi import Depends, FastAPI, HTTPException, status
from pydantic import BaseModel
from fastapi.security.api_key import APIKeyHeader

app = FastAPI()
garmin_key = APIKeyHeader(name="X-Garmin-Key", auto_error=True)


class AuthenticateRequest(BaseModel):
    email: str
    password: str
    mfa_code: str | None = None


class AuthenticateResponse(BaseModel):
    token: str | None = None
    mfa_required: bool = False


def verify_api_key(api_key: str = Depends(garmin_key)):
    garth.client.loads(api_key)


@app.post("/v1/authenticate")
def authenticate(request: AuthenticateRequest) -> AuthenticateResponse:
    result1, result2 = garth.login(request.email, request.password, return_on_mfa=True)

    if result1 == "needs_mfa":
        return AuthenticateResponse(mfa_required=True)
    token = garth.client.dumps()
    return AuthenticateResponse(token=token)


@app.get("/v1/activities", dependencies=[Depends(verify_api_key)])
def get_activities():
    activities = garth.client.connectapi(
        "activitylist-service/activities/search/activities"
    )
    return activities


@app.get("/v1/activities/{activity_id}", dependencies=[Depends(verify_api_key)])
def get_activity(activity_id: str):
    activity = garth.client.connectapi(f"activity-service/activity/{activity_id}")
    if not activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Activity not found",
        )
    return activity


@app.get(
    "/v1/activities/{activity_id}/polyline", dependencies=[Depends(verify_api_key)]
)
def get_activity_polyline(activity_id: str):
    polyline = garth.client.connectapi(
        f"activity-service/activity/{activity_id}/polyline/full-resolution"
    )
    if not polyline:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Activity polyline not found",
        )
    return polyline


@app.get("/v1/user/profile", dependencies=[Depends(verify_api_key)])
def get_user_profile():
    return garth.client.connectapi("/userprofile-service/socialProfile")


@app.get("/v1/user/settings", dependencies=[Depends(verify_api_key)])
def get_user_settings():
    return garth.client.connectapi("/userprofile-service/userprofile/user-settings")


@app.get("/v1/workouts", dependencies=[Depends(verify_api_key)])
def get_workouts():
    return garth.client.connectapi("workout-service/workouts")


@app.get("/v1/workouts/{workout_id}", dependencies=[Depends(verify_api_key)])
def get_workout(workout_id: str):
    workout = garth.client.connectapi(f"workout-service/workout/{workout_id}")
    if not workout:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workout not found",
        )
    return workout


@app.get("/v1/workouts/{workout_id}/{format}", dependencies=[Depends(verify_api_key)])
def export_workout(workout_id: str):
    workout = garth.download(f"workout-service/workout/{format}/{workout_id}")
    if not workout:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workout export not found",
        )

    return workout
