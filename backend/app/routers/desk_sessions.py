from fastapi import APIRouter, Depends, HTTPException, Request, status

from ..dependencies import get_current_admin, get_current_user
from ..desk_sessions import (
    CheckInRequest, DeskSession, StatusUpdateRequest,
    SessionConflict, SessionFinished, SessionNotFound,
    end_session, get_open_session_for_user, set_status, 
    start_session, get_open_sessions_for_desk,
)

router = APIRouter(prefix="/desk-sessions", tags=["desk-sessions"])


# ------------------------------------------------------------------ reads

@router.get("/", response_model=list[DeskSession],
            dependencies=[Depends(get_current_admin)])
def list_sessions(request: Request, offset: int = 0, limit: int = 100):
    limit = max(1, min(limit, 500))
    return list(
        request.app.db.desk_sessions.find()
        .sort("started_at", -1).skip(max(0, offset)).limit(limit)
    )


@router.get("/user/{user_id}", response_model=DeskSession | None)
def get_user_session(
    user_id: str, request: Request,
    current_user: dict = Depends(get_current_user),
):
    if str(current_user["_id"]) != user_id and current_user.get("role") != "admin":
        raise HTTPException(403, "Cannot view another user's session")
    return get_open_session_for_user(request.app.db, user_id)


@router.get("/{session_id}", response_model=DeskSession)
def get_session(
    session_id: str, request: Request,
    current_user: dict = Depends(get_current_user),
):
    s = request.app.db.desk_sessions.find_one({"_id": session_id})
    if s is None:
        raise HTTPException(404, "Session not found")
    if str(current_user["_id"]) != s["user_id"] and current_user.get("role") != "admin":
        raise HTTPException(403, "Cannot view another user's session")
    return s


# ------------------------------------------------------- check-in / out

@router.post("/check-in", response_model=DeskSession, status_code=status.HTTP_201_CREATED)
async def check_in(
    body: CheckInRequest, request: Request,
    current_user: dict = Depends(get_current_user),
):
    try:
        return await start_session(
            db=request.app.db,
            user_id=str(current_user["_id"]),
            desk_id=body.desk_id,
        )
    except SessionConflict as e:
        raise HTTPException(409, str(e))


@router.post("/{session_id}/check-out", response_model=DeskSession)
def check_out(
    session_id: str, request: Request,
    current_user: dict = Depends(get_current_user),
):
    s = request.app.db.desk_sessions.find_one({"_id": session_id})
    if s is None:
        raise HTTPException(404, "Session not found")
    if str(current_user["_id"]) != s["user_id"] and current_user.get("role") != "admin":
        raise HTTPException(403, "Cannot check out another user")
    try:
        return end_session(request.app.db, session_id, reason="checkout")
    except SessionFinished:
        # end_session is idempotent, so a retry returns the existing doc
        return request.app.db.desk_sessions.find_one({"_id": session_id})


@router.post("/user/{user_id}/check-out", response_model=DeskSession,
             dependencies=[Depends(get_current_admin)])
def check_out_user(user_id: str, request: Request):
    s = get_open_session_for_user(request.app.db, user_id)
    if s is None:
        raise HTTPException(404, "No open session for user")
    return end_session(request.app.db, s["_id"], reason="checkout")


@router.post("/desk/{desk_id}/check-out", response_model=list[DeskSession],
             dependencies=[Depends(get_current_admin)])
def check_out_desk(desk_id: str, request: Request):
    open_sessions = get_open_sessions_for_desk(request.app.db, desk_id)
    return [end_session(request.app.db, s["_id"], reason="checkout") for s in open_sessions]


# ------------------------------------------------------------------ status

@router.patch("/{session_id}/status", response_model=DeskSession)
def update_status(
    session_id: str, body: StatusUpdateRequest, request: Request,
    current_user: dict = Depends(get_current_user),
):
    s = request.app.db.desk_sessions.find_one({"_id": session_id})
    if s is None:
        raise HTTPException(404, "Session not found")
    if str(current_user["_id"]) != s["user_id"] and current_user.get("role") != "admin":
        raise HTTPException(403, "Cannot change another user's status")
    try:
        return set_status(request.app.db, session_id, body.status)
    except SessionFinished:
        raise HTTPException(409, "Session already finished")