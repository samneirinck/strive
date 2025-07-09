import base64
import garth
from fastapi import Depends, FastAPI, HTTPException, status
from pydantic import BaseModel
import pprint
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
    # if api_key != expected_api_key:
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="Invalid API Key",
    #     )


@app.post("/authenticate")
def authenticate(request: AuthenticateRequest) -> AuthenticateResponse:
    result1, result2 = garth.login(request.email, request.password, return_on_mfa=True)

    if result1 == "needs_mfa":
        return AuthenticateResponse(mfa_required=True)
    token = garth.client.dumps()
    return AuthenticateResponse(token=token)


def verify_token(token: str):
    print(f"Verifying token: {token}")
    if not token or token.strip() == "":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid token",
        headers={"WWW-Authenticate": "Bearer"},
    )


@app.get("/activities")
def get_activities(token: str = Depends(verify_api_key)):
    activities = garth.client.connectapi(
        "activitylist-service/activities/search/activities"
    )
    # garth.client.loads(token)
    return activities


@app.get("/activities/{activity_id}")
def get_activity(activity_id: str, token: str = Depends(verify_api_key)):
    activity = garth.client.connectapi(f"activity-service/activity/{activity_id}")
    if not activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Activity not found",
        )
    return activity


@app.get("/user/profile")
def get_user_profile(token: str = Depends(verify_api_key)):
    return garth.UserProfile.get()


@app.get("/user/settings")
def get_user_settings(token: str = Depends(verify_api_key)):
    return garth.UserSettings.get()
