from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models.raid import Raid
from app.models.team import Team
from app.models.scenario import Scenario
from app.schemas.raid import RaidCreate, RaidUpdate, RaidResponse
from app.models.token import Token
from app.utils.auth import require_any_token, require_superuser
from app.models.user import User
from app.utils.warcraftlogs import (
    extract_report_code,
    fetch_report_metadata,
    fetch_report_participants,
)

router = APIRouter(prefix="/raids", tags=["Raids"])


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

    # Process warcraftlogs_url if provided
    participants = []
    if raid_in.warcraftlogs_url:
        report_code = extract_report_code(raid_in.warcraftlogs_url)
        if report_code:
            # Fetch report metadata
            report_data = fetch_report_metadata(report_code)
            if report_data:
                print(
                    f"Fetched WarcraftLogs report: {report_data.get('title', 'Unknown')}"
                )

                # Fetch participant data
                participants = fetch_report_participants(report_code)
                if participants:
                    print(f"Found {len(participants)} participants in the raid")
                    for participant in participants:
                        print(
                            f"  - {participant.get('name', 'Unknown')} ({participant.get('class', 'Unknown')} {participant.get('spec', 'Unknown')})"
                        )
                else:
                    print("No participants found in the report")
            else:
                print(
                    f"Failed to fetch WarcraftLogs report data for code: {report_code}"
                )
        else:
            print(f"Invalid WarcraftLogs URL: {raid_in.warcraftlogs_url}")

    raid = Raid(
        scheduled_at=raid_in.scheduled_at,
        scenario_id=raid_in.scenario_id,
        team_id=raid_in.team_id,
        warcraftlogs_url=raid_in.warcraftlogs_url,
    )
    db.add(raid)
    db.commit()
    db.refresh(raid)
    return raid


@router.get(
    "/",
    response_model=List[RaidResponse],
    dependencies=[Depends(require_any_token)],
)
def list_raids(
    team_id: Optional[int] = None,
    scenario_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_token: Token = Depends(require_any_token),
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
    dependencies=[Depends(require_any_token)],
)
def get_raid(
    raid_id: int,
    db: Session = Depends(get_db),
    current_token: Token = Depends(require_any_token),
):
    """
    Get a raid by ID. Any valid token required.
    """
    raid = get_raid_or_404(db, raid_id)
    return raid


@router.get(
    "/team/{team_id}",
    response_model=List[RaidResponse],
    dependencies=[Depends(require_any_token)],
)
def get_raids_by_team(
    team_id: int,
    db: Session = Depends(get_db),
    current_token: Token = Depends(require_any_token),
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
    dependencies=[Depends(require_any_token)],
)
def get_raids_by_scenario(
    scenario_id: int,
    db: Session = Depends(get_db),
    current_token: Token = Depends(require_any_token),
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
