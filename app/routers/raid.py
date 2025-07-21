from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models.raid import Raid
from app.models.team import Team
from app.models.scenario import Scenario
from app.models.toon import Toon
from app.models.attendance import Attendance
from app.schemas.raid import RaidCreate, RaidUpdate, RaidResponse
from app.models.token import Token
from app.utils.auth import require_user, require_superuser
from app.models.user import User
from app.utils.warcraftlogs import (
    extract_report_code,
    fetch_report_metadata,
    fetch_report_participants,
    process_warcraftlogs_raid,
)
from pydantic import BaseModel

router = APIRouter(prefix="/raids", tags=["Raids"])


class WarcraftLogsProcessRequest(BaseModel):
    warcraftlogs_url: str
    team_id: int


def get_raid_or_404(db: Session, raid_id: int) -> Raid:
    raid = db.query(Raid).filter(Raid.id == raid_id).first()
    if not raid:
        raise HTTPException(status_code=404, detail="Raid not found")
    return raid


def get_team_or_404(db: Session, team_id: int) -> Team:
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    return team


def get_scenario_or_404(db: Session, scenario_id: int) -> Scenario:
    scenario = db.query(Scenario).filter(Scenario.id == scenario_id).first()
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    return scenario


def get_team_toons(db: Session, team_id: int) -> List[dict]:
    """
    Get all toons for a team with their member information.
    """
    toons = db.query(Toon).join(Toon.teams).filter(Team.id == team_id).all()

    return [
        {
            "id": toon.id,
            "username": toon.username,
            "class": toon.class_,
            "role": toon.role,
            "is_main": toon.is_main,
            "member_id": toon.member_id,
            "member_name": toon.member.display_name if toon.member else None,
        }
        for toon in toons
    ]


@router.post(
    "/process-warcraftlogs",
    dependencies=[Depends(require_superuser)],
)
def process_warcraftlogs_report(
    request: WarcraftLogsProcessRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superuser),
):
    """
    Process a WarcraftLogs report and return participant matching information.
    This endpoint helps the frontend handle unknown participants before creating a raid.
    Superuser only.
    """
    # Verify team exists
    team = get_team_or_404(db, request.team_id)

    # Get team toons (can be empty)
    team_toons = get_team_toons(db, request.team_id)

    # Process WarcraftLogs report
    processing_result = process_warcraftlogs_raid(
        request.warcraftlogs_url, team_toons
    )

    if not processing_result["success"]:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to process WarcraftLogs report: {processing_result['error']}",
        )

    return {
        "success": True,
        "report_metadata": processing_result["report_metadata"],
        "participants": processing_result["participants"],
        "matched_participants": processing_result["matched_participants"],
        "unknown_participants": processing_result["unknown_participants"],
        "attendance_records": processing_result["attendance_records"],
        "team_toons": team_toons,
    }


@router.post(
    "/",
    response_model=RaidResponse,
    status_code=201,
    dependencies=[Depends(require_superuser)],
)
def create_raid(
    raid_in: RaidCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superuser),
):
    """
    Create a new raid. Superuser only.
    Accepts a WarcraftLogs URL and processes it to extract participant data.
    """
    # Verify team exists
    team = get_team_or_404(db, raid_in.team_id)

    # Verify scenario exists
    scenario = get_scenario_or_404(db, raid_in.scenario_id)

    # Create the raid first
    raid = Raid(
        scheduled_at=raid_in.scheduled_at,
        scenario_id=raid_in.scenario_id,
        team_id=raid_in.team_id,
        warcraftlogs_url=raid_in.warcraftlogs_url,
    )
    db.add(raid)
    db.commit()
    db.refresh(raid)

    # Process WarcraftLogs URL if provided
    processing_result = None
    if raid_in.warcraftlogs_url:
        try:
            # Get team toons
            team_toons = get_team_toons(db, raid_in.team_id)

            if not team_toons:
                print(f"No toons found for team {raid_in.team_id}")
            else:
                print(
                    f"Found {len(team_toons)} toons in team {raid_in.team_id}"
                )

                # Process WarcraftLogs report
                processing_result = process_warcraftlogs_raid(
                    raid_in.warcraftlogs_url, team_toons
                )

                if processing_result["success"]:
                    # Store WarcraftLogs data in the raid record
                    report_code = extract_report_code(raid_in.warcraftlogs_url)
                    raid.warcraftlogs_report_code = report_code
                    raid.warcraftlogs_metadata = processing_result[
                        "report_metadata"
                    ]
                    raid.warcraftlogs_participants = processing_result[
                        "participants"
                    ]

                    # Create attendance records
                    attendance_records = processing_result["attendance_records"]
                    created_attendance = []

                    for record in attendance_records:
                        # Check if attendance record already exists
                        existing = (
                            db.query(Attendance)
                            .filter(
                                Attendance.raid_id == raid.id,
                                Attendance.toon_id == record["toon_id"],
                            )
                            .first()
                        )

                        if not existing:
                            attendance = Attendance(
                                raid_id=raid.id,
                                toon_id=record["toon_id"],
                                is_present=record["is_present"],
                                notes=record["notes"],
                            )
                            db.add(attendance)
                            created_attendance.append(attendance)

                    if created_attendance:
                        db.commit()
                        print(
                            f"Created {len(created_attendance)} attendance records"
                        )

                    # Log processing results
                    print(f"WarcraftLogs processing completed:")
                    print(
                        f"  - Report: {processing_result['report_metadata'].get('title', 'Unknown')}"
                    )
                    print(
                        f"  - Participants found: {len(processing_result['participants'])}"
                    )
                    print(
                        f"  - Attendance records created: {len(created_attendance)}"
                    )
                    print(
                        f"  - Unknown participants: {len(processing_result['unknown_participants'])}"
                    )

                else:
                    print(
                        f"WarcraftLogs processing failed: {processing_result['error']}"
                    )

        except Exception as e:
            print(f"Error processing WarcraftLogs report: {e}")
            # Don't fail the raid creation, just log the error

    return raid


@router.get(
    "/",
    response_model=List[RaidResponse],
)
def list_raids(
    team_id: Optional[int] = None,
    scenario_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_user),
):
    """
    List raids. Can filter by team_id or scenario_id. Any valid token required.
    """
    query = db.query(Raid)
    if team_id:
        query = query.filter(Raid.team_id == team_id)
    if scenario_id:
        query = query.filter(Raid.scenario_id == scenario_id)
    raids = query.all()
    return raids


@router.get(
    "/{raid_id}",
    response_model=RaidResponse,
)
def get_raid(
    raid_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_user),
):
    """
    Get a raid by ID. Any valid token required.
    """
    raid = get_raid_or_404(db, raid_id)
    return raid


@router.get(
    "/team/{team_id}",
    response_model=List[RaidResponse],
)
def get_raids_by_team(
    team_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_user),
):
    """
    Get all raids for a specific team. Any valid token required.
    """
    team = get_team_or_404(db, team_id)
    raids = db.query(Raid).filter(Raid.team_id == team_id).all()
    return raids


@router.get(
    "/scenario/{scenario_id}",
    response_model=List[RaidResponse],
)
def get_raids_by_scenario(
    scenario_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_user),
):
    """
    Get all raids for a specific scenario. Any valid token required.
    """
    scenario = get_scenario_or_404(db, scenario_id)
    raids = db.query(Raid).filter(Raid.scenario_id == scenario_id).all()
    return raids


@router.put(
    "/{raid_id}",
    response_model=RaidResponse,
    dependencies=[Depends(require_superuser)],
)
def update_raid(
    raid_id: int,
    raid_in: RaidUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superuser),
):
    """
    Update a raid. Superuser only.
    """
    raid = get_raid_or_404(db, raid_id)

    if raid_in.scheduled_at is not None:
        raid.scheduled_at = raid_in.scheduled_at  # type: ignore[assignment]

    if raid_in.scenario_id is not None:
        # Verify new scenario exists
        scenario = get_scenario_or_404(db, raid_in.scenario_id)
        raid.scenario_id = raid_in.scenario_id  # type: ignore[assignment]

    if raid_in.team_id is not None:
        # Verify new team exists
        team = get_team_or_404(db, raid_in.team_id)
        raid.team_id = raid_in.team_id  # type: ignore[assignment]

    if raid_in.warcraftlogs_url is not None:
        raid.warcraftlogs_url = raid_in.warcraftlogs_url

    db.commit()
    db.refresh(raid)
    return raid


@router.delete(
    "/{raid_id}",
    status_code=204,
    dependencies=[Depends(require_superuser)],
)
def delete_raid(
    raid_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superuser),
):
    """
    Delete a raid. Superuser only.
    """
    raid = get_raid_or_404(db, raid_id)
    db.delete(raid)
    db.commit()
    return None
