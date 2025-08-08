from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from app.database import get_db
from app.models.attendance import Attendance
from app.models.raid import Raid
from app.models.toon import Toon
from app.models.team import Team
from app.models.guild import Guild
from app.schemas.attendance import (
    AttendanceCreate,
    AttendanceUpdate,
    AttendanceResponse,
    AttendanceBulkCreate,
    AttendanceBulkUpdate,
    AttendanceBulkUpdateItem,
    AttendanceStats,
    AttendanceReport,
    BenchedPlayer,
    TeamViewData,
    TeamViewToon,
    TeamViewRaid,
    ToonAttendanceRecord,
)
from app.models.attendance import AttendanceStatus
from app.models.token import Token
from app.utils.auth import require_superuser, require_user
from app.models.user import User
from app.utils.image_generator import (
    AttendanceImageGenerator,
    get_current_period,
)
from app.config import settings

# Debug import
from app.utils.logger import get_logger

logger = get_logger(__name__)
logger.info("Attendance router loaded - checking imports...")
try:
    from PIL import Image, ImageDraw, ImageFont

    logger.info("PIL imports successful")
except ImportError as e:
    logger.error(f"PIL import failed: {e}")

router = APIRouter(prefix="/attendance", tags=["Attendance"])


@router.get("/debug")
def debug_attendance_router():
    """Debug endpoint to test if attendance router is working."""
    return {
        "message": "Attendance router is working",
        "routes": ["/export/team/{team_id}/image", "/export/all-teams/image"],
        "export_enabled": settings.ENABLE_ATTENDANCE_EXPORT,
    }


@router.get("/export/status")
def get_export_status():
    """Get the status of attendance export functionality."""
    return {
        "export_enabled": settings.ENABLE_ATTENDANCE_EXPORT,
    }


def get_attendance_or_404(db: Session, attendance_id: int) -> Attendance:
    """Get attendance record by ID or raise 404."""
    attendance = (
        db.query(Attendance).filter(Attendance.id == attendance_id).first()
    )
    if not attendance:
        raise HTTPException(
            status_code=404, detail="Attendance record not found"
        )
    return attendance


def get_raid_or_404(db: Session, raid_id: int) -> Raid:
    """Get raid by ID or raise 404."""
    raid = db.query(Raid).filter(Raid.id == raid_id).first()
    if not raid:
        raise HTTPException(status_code=404, detail="Raid not found")
    return raid


def get_toon_or_404(db: Session, toon_id: int) -> Toon:
    """Get toon by ID or raise 404."""
    toon = db.query(Toon).filter(Toon.id == toon_id).first()
    if not toon:
        raise HTTPException(status_code=404, detail="Toon not found")
    return toon


def get_team_or_404(db: Session, team_id: int) -> Team:
    """Get team by ID or raise 404."""
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    return team


def get_guild_or_404(db: Session, guild_id: int) -> Guild:
    """Get guild by ID or raise 404."""
    guild = db.query(Guild).filter(Guild.id == guild_id).first()
    if not guild:
        raise HTTPException(status_code=404, detail="Guild not found")
    return guild


@router.post(
    "/",
    response_model=AttendanceResponse,
    status_code=201,
    dependencies=[Depends(require_superuser)],
)
def create_attendance(
    attendance_in: AttendanceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superuser),
):
    """
    Create a new attendance record. Superuser only.
    """
    # Verify raid exists
    raid = get_raid_or_404(db, attendance_in.raid_id)

    # Verify toon exists
    toon = get_toon_or_404(db, attendance_in.toon_id)

    # Check for existing attendance record
    existing = (
        db.query(Attendance)
        .filter(
            Attendance.raid_id == attendance_in.raid_id,
            Attendance.toon_id == attendance_in.toon_id,
        )
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Attendance record already exists for this raid and toon",
        )

    attendance = Attendance(
        raid_id=attendance_in.raid_id,
        toon_id=attendance_in.toon_id,
        status=attendance_in.status,
        notes=attendance_in.notes,
        benched_note=attendance_in.benched_note,
    )
    db.add(attendance)
    db.commit()
    db.refresh(attendance)
    return attendance


@router.post(
    "/bulk",
    response_model=List[AttendanceResponse],
    status_code=201,
    dependencies=[Depends(require_superuser)],
)
def create_attendance_bulk(
    bulk_in: AttendanceBulkCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superuser),
):
    """
    Create multiple attendance records. Superuser only.
    """
    created_records = []

    for record in bulk_in.attendance_records:
        # Verify raid and toon exist
        raid = get_raid_or_404(db, record.raid_id)
        toon = get_toon_or_404(db, record.toon_id)

        # Check for existing attendance record
        existing = (
            db.query(Attendance)
            .filter(
                Attendance.raid_id == record.raid_id,
                Attendance.toon_id == record.toon_id,
            )
            .first()
        )

        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Attendance record already exists for raid {record.raid_id} and toon {record.toon_id}",
            )

        attendance = Attendance(
            raid_id=record.raid_id,
            toon_id=record.toon_id,
            status=record.status,
            notes=record.notes,
            benched_note=record.benched_note,
        )
        db.add(attendance)
        created_records.append(attendance)

    db.commit()

    # Refresh all created records
    for record in created_records:
        db.refresh(record)

    return created_records


@router.get(
    "/",
    response_model=List[AttendanceResponse],
    dependencies=[Depends(require_user)],
)
def list_attendance(
    raid_id: Optional[int] = None,
    toon_id: Optional[int] = None,
    team_id: Optional[int] = None,
    status: Optional[AttendanceStatus] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_user),
):
    """
    List attendance records with filtering options. Any valid user session or token required.
    """
    query = db.query(Attendance)

    if raid_id:
        query = query.filter(Attendance.raid_id == raid_id)

    if toon_id:
        query = query.filter(Attendance.toon_id == toon_id)

    if team_id:
        # Get all raids for the team
        team_raids = (
            db.query(Raid.id).filter(Raid.team_id == team_id).subquery()
        )
        query = query.filter(Attendance.raid_id.in_(team_raids))

    if status is not None:
        query = query.filter(Attendance.status == status)

    if start_date:
        # Join with raids to filter by raid date
        query = query.join(Raid).filter(Raid.scheduled_at >= start_date)

    if end_date:
        # Join with raids to filter by raid date
        query = query.join(Raid).filter(Raid.scheduled_at <= end_date)

    attendance_records = query.all()
    return attendance_records


@router.put(
    "/bulk",
    response_model=List[AttendanceResponse],
    dependencies=[Depends(require_superuser)],
)
def update_attendance_bulk(
    bulk_in: AttendanceBulkUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superuser),
):
    """
    Update multiple attendance records. Superuser only.
    """
    updated_records = []

    for record in bulk_in.attendance_records:
        attendance = get_attendance_or_404(db, record.id)
        update_data = record.model_dump(exclude_unset=True, exclude={"id"})
        if "status" in update_data:
            attendance.status = update_data["status"]  # type: ignore[assignment]
        if "notes" in update_data:
            attendance.notes = update_data["notes"]  # type: ignore[assignment]
        if "benched_note" in update_data:
            attendance.benched_note = update_data["benched_note"]  # type: ignore[assignment]
        updated_records.append(attendance)

    db.commit()

    # Refresh all updated records
    for record in updated_records:
        db.refresh(record)

    return updated_records


@router.get(
    "/{attendance_id}",
    response_model=AttendanceResponse,
    dependencies=[Depends(require_user)],
)
def get_attendance(
    attendance_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_user),
):
    """
    Get attendance record by ID. Any valid token required.
    """
    attendance = get_attendance_or_404(db, attendance_id)
    return attendance


@router.get(
    "/raid/{raid_id}",
    response_model=List[AttendanceResponse],
    dependencies=[Depends(require_user)],
)
def get_attendance_by_raid(
    raid_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_user),
):
    """
    Get all attendance records for a specific raid. Any valid token required.
    """
    raid = get_raid_or_404(db, raid_id)
    attendance_records = (
        db.query(Attendance).filter(Attendance.raid_id == raid_id).all()
    )
    return attendance_records


@router.get(
    "/toon/{toon_id}",
    response_model=List[AttendanceResponse],
    dependencies=[Depends(require_user)],
)
def get_attendance_by_toon(
    toon_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_user),
):
    """
    Get all attendance records for a specific toon. Any valid token required.
    """
    toon = get_toon_or_404(db, toon_id)
    attendance_records = (
        db.query(Attendance).filter(Attendance.toon_id == toon_id).all()
    )
    return attendance_records


@router.get(
    "/team/{team_id}",
    response_model=List[AttendanceResponse],
    dependencies=[Depends(require_user)],
)
def get_attendance_by_team(
    team_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_user),
):
    """
    Get all attendance records for all raids of a specific team. Any valid token required.
    """
    team = get_team_or_404(db, team_id)
    team_raids = db.query(Raid.id).filter(Raid.team_id == team_id).subquery()
    attendance_records = (
        db.query(Attendance).filter(Attendance.raid_id.in_(team_raids)).all()
    )
    return attendance_records


@router.get(
    "/team-view/{team_id}",
    response_model=TeamViewData,
    dependencies=[Depends(require_user)],
)
def get_team_attendance_view(
    team_id: int,
    raid_count: int = 5,
    guild_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_user),
):
    """
    Get team attendance view with toons as rows and raids as columns.
    Returns toons with their attendance data for the last N raids.
    Any valid token required.
    """
    # Validate raid_count
    if raid_count < 1 or raid_count > 50:
        raise HTTPException(
            status_code=400, detail="raid_count must be between 1 and 50"
        )

    # Get team and verify it exists
    team = get_team_or_404(db, team_id)

    # If guild_id is provided, verify the team belongs to that guild
    if guild_id is not None:
        guild = get_guild_or_404(db, guild_id)
        if team.guild_id != guild_id:
            raise HTTPException(
                status_code=400,
                detail="Team does not belong to the specified guild",
            )

    # Get the last N raids for this team, ordered by date (newest first)
    recent_raids = (
        db.query(Raid)
        .filter(Raid.team_id == team_id)
        .order_by(Raid.scheduled_at.desc())
        .limit(raid_count)
        .all()
    )

    if not recent_raids:
        # Return empty response if no raids found
        return TeamViewData(
            team={"id": team.id, "name": team.name, "guild_id": team.guild_id},
            toons=[],
            raids=[],
        )

    raid_ids = [raid.id for raid in recent_raids]

    # Get all toons that have attendance records for these raids
    toon_ids = (
        db.query(Attendance.toon_id)
        .filter(Attendance.raid_id.in_(raid_ids))
        .distinct()
        .all()
    )
    toon_ids = [toon_id[0] for toon_id in toon_ids]

    # Get toon details
    toons = db.query(Toon).filter(Toon.id.in_(toon_ids)).all()

    # Get all attendance records for these raids and toons
    attendance_records = (
        db.query(Attendance)
        .filter(
            Attendance.raid_id.in_(raid_ids), Attendance.toon_id.in_(toon_ids)
        )
        .all()
    )

    # Build response data
    team_view_toons = []

    for toon in toons:
        # Get attendance records for this toon
        toon_attendance = [
            record for record in attendance_records if record.toon_id == toon.id
        ]

        # Calculate overall attendance percentage (excluding benched)
        total_raids = len(toon_attendance)
        present_count = sum(
            1
            for record in toon_attendance
            if record.status == AttendanceStatus.PRESENT
        )
        benched_count = sum(
            1
            for record in toon_attendance
            if record.status == AttendanceStatus.BENCHED
        )

        # Calculate percentage excluding benched from denominator
        effective_total = total_raids - benched_count
        attendance_percentage = (
            (present_count / effective_total * 100)
            if effective_total > 0
            else 0.0
        )

        # Build attendance records for this toon
        toon_attendance_records = []
        for raid in recent_raids:
            # Find attendance record for this raid and toon
            attendance_record = next(
                (
                    record
                    for record in toon_attendance
                    if record.raid_id == raid.id
                ),
                None,
            )

            if attendance_record:
                # Determine if there's a note
                has_note = bool(
                    (
                        attendance_record.notes
                        and attendance_record.notes.strip()
                    )
                    or (
                        attendance_record.benched_note
                        and attendance_record.benched_note.strip()
                    )
                )

                toon_attendance_records.append(
                    ToonAttendanceRecord(
                        raid_id=raid.id,
                        raid_date=raid.scheduled_at,
                        status=attendance_record.status,
                        notes=attendance_record.notes,
                        benched_note=attendance_record.benched_note,
                        has_note=has_note,
                    )
                )
            else:
                # No attendance record found for this raid
                toon_attendance_records.append(
                    ToonAttendanceRecord(
                        raid_id=raid.id,
                        raid_date=raid.scheduled_at,
                        status=AttendanceStatus.ABSENT,  # Default to absent if no record
                        notes=None,
                        benched_note=None,
                        has_note=False,
                    )
                )

        team_view_toons.append(
            TeamViewToon(
                id=toon.id,
                username=toon.username,
                class_name=toon.class_,
                role=toon.role,
                overall_attendance_percentage=attendance_percentage,
                attendance_records=toon_attendance_records,
            )
        )

    # Build raid data
    team_view_raids = [
        TeamViewRaid(
            id=raid.id,
            scheduled_at=raid.scheduled_at,
            scenario_name=raid.scenario_name,
        )
        for raid in recent_raids
    ]

    return TeamViewData(
        team={"id": team.id, "name": team.name, "guild_id": team.guild_id},
        toons=team_view_toons,
        raids=team_view_raids,
    )


@router.put(
    "/{attendance_id}",
    response_model=AttendanceResponse,
    dependencies=[Depends(require_superuser)],
)
def update_attendance(
    attendance_id: int,
    attendance_in: AttendanceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superuser),
):
    """
    Update an attendance record. Superuser only.
    """
    attendance = get_attendance_or_404(db, attendance_id)

    if attendance_in.status is not None:
        attendance.status = attendance_in.status  # type: ignore[assignment]

    if attendance_in.notes is not None:
        attendance.notes = attendance_in.notes  # type: ignore[assignment]

    if attendance_in.benched_note is not None:
        attendance.benched_note = attendance_in.benched_note  # type: ignore[assignment]

    db.commit()
    db.refresh(attendance)
    return attendance


@router.delete(
    "/{attendance_id}",
    status_code=204,
    dependencies=[Depends(require_superuser)],
)
def delete_attendance(
    attendance_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superuser),
):
    """
    Delete an attendance record. Superuser only.
    """
    attendance = get_attendance_or_404(db, attendance_id)
    db.delete(attendance)
    db.commit()
    return None


@router.get(
    "/stats/raid/{raid_id}",
    response_model=AttendanceStats,
    dependencies=[Depends(require_user)],
)
def get_raid_attendance_stats(
    raid_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_user),
):
    """
    Get attendance statistics for a specific raid. Any valid token required.
    """
    raid = get_raid_or_404(db, raid_id)

    # Get attendance records for this raid
    attendance_records = (
        db.query(Attendance).filter(Attendance.raid_id == raid_id).all()
    )

    total_records = len(attendance_records)
    present_count = sum(
        1
        for record in attendance_records
        if record.status == AttendanceStatus.PRESENT
    )
    absent_count = sum(
        1
        for record in attendance_records
        if record.status == AttendanceStatus.ABSENT
    )
    benched_count = sum(
        1
        for record in attendance_records
        if record.status == AttendanceStatus.BENCHED
    )

    attendance_percentage = (
        (present_count / total_records * 100) if total_records > 0 else 0.0
    )

    return AttendanceStats(
        total_raids=1,  # Single raid
        raids_attended=present_count,
        raids_missed=absent_count,
        raids_benched=benched_count,
        attendance_percentage=attendance_percentage,
        current_streak=0,  # Not applicable for single raid
        longest_streak=0,  # Not applicable for single raid
        last_attendance=raid.scheduled_at if present_count > 0 else None,
    )


@router.get(
    "/stats/toon/{toon_id}",
    response_model=AttendanceStats,
    dependencies=[Depends(require_user)],
)
def get_toon_attendance_stats(
    toon_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_user),
):
    """
    Get attendance statistics for a specific toon. Any valid token required.
    """
    toon = get_toon_or_404(db, toon_id)

    # Get all attendance records for this toon, ordered by raid date
    attendance_records = (
        db.query(Attendance)
        .join(Raid)
        .filter(Attendance.toon_id == toon_id)
        .order_by(Raid.scheduled_at)
        .all()
    )

    total_raids = len(attendance_records)
    raids_attended = sum(
        1
        for record in attendance_records
        if record.status == AttendanceStatus.PRESENT
    )
    raids_missed = sum(
        1
        for record in attendance_records
        if record.status == AttendanceStatus.ABSENT
    )
    raids_benched = sum(
        1
        for record in attendance_records
        if record.status == AttendanceStatus.BENCHED
    )

    # Calculate percentage excluding benched from denominator
    effective_total = total_raids - raids_benched
    attendance_percentage = (
        (raids_attended / effective_total * 100) if effective_total > 0 else 0.0
    )

    # Calculate streaks
    current_streak = 0
    longest_streak = 0
    temp_streak = 0

    for record in reversed(attendance_records):  # Start from most recent
        if record.status == AttendanceStatus.PRESENT:
            temp_streak += 1
            current_streak = temp_streak  # Update current streak continuously
        else:
            longest_streak = max(longest_streak, temp_streak)
            temp_streak = 0
            current_streak = 0  # Reset current streak when we hit an absence

    # Check if the longest streak is the current one
    longest_streak = max(longest_streak, temp_streak)

    last_attendance = None
    if attendance_records:
        last_record = attendance_records[-1]
        if last_record.status == AttendanceStatus.PRESENT:
            last_attendance = last_record.raid.scheduled_at

    return AttendanceStats(
        total_raids=total_raids,
        raids_attended=raids_attended,
        raids_missed=raids_missed,
        raids_benched=raids_benched,
        attendance_percentage=attendance_percentage,
        current_streak=current_streak,
        longest_streak=longest_streak,
        last_attendance=last_attendance,
    )


@router.get(
    "/stats/team/{team_id}",
    response_model=AttendanceStats,
    dependencies=[Depends(require_user)],
)
def get_team_attendance_stats(
    team_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_user),
):
    """
    Get attendance statistics for all raids of a specific team. Any valid token required.
    """
    team = get_team_or_404(db, team_id)

    # Get all attendance records for all raids of this team
    team_raids = db.query(Raid.id).filter(Raid.team_id == team_id).subquery()
    attendance_records = (
        db.query(Attendance)
        .join(Raid)
        .filter(Attendance.raid_id.in_(team_raids))
        .order_by(Raid.scheduled_at)
        .all()
    )

    total_raids = len(attendance_records)
    raids_attended = sum(
        1
        for record in attendance_records
        if record.status == AttendanceStatus.PRESENT
    )
    raids_missed = sum(
        1
        for record in attendance_records
        if record.status == AttendanceStatus.ABSENT
    )
    raids_benched = sum(
        1
        for record in attendance_records
        if record.status == AttendanceStatus.BENCHED
    )

    # Calculate percentage excluding benched from denominator
    effective_total = total_raids - raids_benched
    attendance_percentage = (
        (raids_attended / effective_total * 100) if effective_total > 0 else 0.0
    )

    # For team stats, we'll use simplified streak calculation
    current_streak = 0
    longest_streak = 0
    temp_streak = 0

    for record in reversed(attendance_records):
        if record.status == AttendanceStatus.PRESENT:
            temp_streak += 1
            current_streak = temp_streak  # Update current streak continuously
        else:
            longest_streak = max(longest_streak, temp_streak)
            temp_streak = 0
            current_streak = 0  # Reset current streak when we hit an absence

    longest_streak = max(longest_streak, temp_streak)

    last_attendance = None
    if attendance_records:
        last_record = attendance_records[-1]
        if last_record.status == AttendanceStatus.PRESENT:
            last_attendance = last_record.raid.scheduled_at

    return AttendanceStats(
        total_raids=total_raids,
        raids_attended=raids_attended,
        raids_missed=raids_missed,
        raids_benched=raids_benched,
        attendance_percentage=attendance_percentage,
        current_streak=current_streak,
        longest_streak=longest_streak,
        last_attendance=last_attendance,
    )


@router.get(
    "/report/date-range",
    response_model=AttendanceReport,
    dependencies=[Depends(require_user)],
)
def get_attendance_report(
    start_date: datetime,
    end_date: datetime,
    team_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_user),
):
    """
    Get comprehensive attendance report for a date range. Any valid token required.
    """
    if start_date >= end_date:
        raise HTTPException(
            status_code=400, detail="Start date must be before end date"
        )

    # Build base query for raids in date range
    raid_query = db.query(Raid).filter(
        Raid.scheduled_at >= start_date, Raid.scheduled_at <= end_date
    )

    if team_id:
        team = get_team_or_404(db, team_id)
        raid_query = raid_query.filter(Raid.team_id == team_id)

    raids_in_period = raid_query.all()
    raid_ids = [raid.id for raid in raids_in_period]

    if not raid_ids:
        return AttendanceReport(
            start_date=start_date,
            end_date=end_date,
            total_raids=0,
            total_attendance_records=0,
            present_count=0,
            absent_count=0,
            benched_count=0,
            overall_attendance_rate=0.0,
            attendance_by_raid=[],
            attendance_by_toon=[],
        )

    # Get all attendance records for these raids
    attendance_query = db.query(Attendance).filter(
        Attendance.raid_id.in_(raid_ids)
    )

    attendance_records = attendance_query.all()

    total_attendance_records = len(attendance_records)
    present_count = sum(
        1
        for record in attendance_records
        if record.status == AttendanceStatus.PRESENT
    )
    absent_count = sum(
        1
        for record in attendance_records
        if record.status == AttendanceStatus.ABSENT
    )
    benched_count = sum(
        1
        for record in attendance_records
        if record.status == AttendanceStatus.BENCHED
    )
    overall_attendance_rate = (
        (present_count / total_attendance_records * 100)
        if total_attendance_records > 0
        else 0.0
    )

    # Generate attendance by raid breakdown
    attendance_by_raid = []
    for raid in raids_in_period:
        raid_attendance = [
            r for r in attendance_records if r.raid_id == raid.id
        ]
        raid_present = sum(
            1 for r in raid_attendance if r.status == AttendanceStatus.PRESENT
        )
        raid_absent = sum(
            1 for r in raid_attendance if r.status == AttendanceStatus.ABSENT
        )
        raid_benched = sum(
            1 for r in raid_attendance if r.status == AttendanceStatus.BENCHED
        )

        attendance_by_raid.append(
            {
                "raid_id": raid.id,
                "raid_name": f"Raid {raid.id}",
                "scheduled_at": raid.scheduled_at,
                "present": raid_present,
                "absent": raid_absent,
                "benched": raid_benched,
                "total": len(raid_attendance),
            }
        )

    # Generate attendance by toon breakdown
    toon_ids = list(set(r.toon_id for r in attendance_records))
    attendance_by_toon = []

    for toon_id in toon_ids:
        toon_attendance = [
            r for r in attendance_records if r.toon_id == toon_id
        ]
        toon_present = sum(
            1 for r in toon_attendance if r.status == AttendanceStatus.PRESENT
        )
        toon_absent = sum(
            1 for r in toon_attendance if r.status == AttendanceStatus.ABSENT
        )
        toon_benched = sum(
            1 for r in toon_attendance if r.status == AttendanceStatus.BENCHED
        )

        attendance_by_toon.append(
            {
                "toon_id": toon_id,
                "present": toon_present,
                "absent": toon_absent,
                "benched": toon_benched,
                "total": len(toon_attendance),
            }
        )

    return AttendanceReport(
        start_date=start_date,
        end_date=end_date,
        total_raids=len(raids_in_period),
        total_attendance_records=total_attendance_records,
        present_count=present_count,
        absent_count=absent_count,
        benched_count=benched_count,
        overall_attendance_rate=overall_attendance_rate,
        attendance_by_raid=attendance_by_raid,
        attendance_by_toon=attendance_by_toon,
    )


@router.get(
    "/benched/team/{team_id}/week/{week_date}",
    response_model=List[BenchedPlayer],
    dependencies=[Depends(require_user)],
)
def get_benched_players_for_week(
    team_id: int,
    week_date: datetime,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_user),
):
    """
    Get benched players for a team in a specific week (Tuesday reset to next Tuesday).
    Any valid token required.

    Week is defined as Tuesday 9am PST to the following Tuesday 9am PST.
    """
    # Verify team exists
    team = get_team_or_404(db, team_id)

    # Calculate week boundaries (Tuesday 9am PST)
    # Convert week_date to Tuesday 9am PST of that week
    from datetime import timezone, timedelta
    import pytz

    pst = pytz.timezone("US/Pacific")

    # Get the Tuesday of the week_date
    days_since_tuesday = (week_date.weekday() - 1) % 7  # 1 = Tuesday
    tuesday_start = week_date - timedelta(days=days_since_tuesday)
    tuesday_start = tuesday_start.replace(
        hour=9, minute=0, second=0, microsecond=0
    )
    tuesday_start = pst.localize(tuesday_start)

    # End of week is next Tuesday 9am PST
    week_end = tuesday_start + timedelta(days=7)

    # Get all raids for the team in this week
    team_raids = (
        db.query(Raid)
        .filter(
            Raid.team_id == team_id,
            Raid.scheduled_at >= tuesday_start,
            Raid.scheduled_at < week_end,
        )
        .all()
    )

    if not team_raids:
        return []

    raid_ids = [raid.id for raid in team_raids]

    # Get benched attendance records for these raids
    benched_attendance = (
        db.query(Attendance)
        .filter(
            Attendance.raid_id.in_(raid_ids),
            Attendance.status == AttendanceStatus.BENCHED,
        )
        .all()
    )

    # Get toon and raid details for benched players
    benched_players = []
    for attendance in benched_attendance:
        # Get toon details
        toon = db.query(Toon).filter(Toon.id == attendance.toon_id).first()
        if not toon:
            continue

        # Get raid details
        raid = db.query(Raid).filter(Raid.id == attendance.raid_id).first()
        if not raid:
            continue

        benched_players.append(
            BenchedPlayer(
                toon_id=toon.id,
                toon_name=toon.name,
                class_name=toon.class_name,
                spec_name=toon.spec_name,
                raid_id=raid.id,
                raid_name=f"Raid {raid.id}",
                raid_date=raid.scheduled_at,
                benched_note=attendance.benched_note,
            )
        )

    return benched_players


@router.get(
    "/export/team/{team_id}/image",
    dependencies=[Depends(require_user)],
)
def export_team_attendance_image(
    team_id: int,
    period: str = "current",  # "current", "all", or "custom"
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    raid_count: int = 20,  # Max raids to include
    db: Session = Depends(get_db),
    current_user: User = Depends(require_user),
):
    """
    Export team attendance as a PNG image.
    Any valid token required.

    Period options:
    - "current": From previous Tuesday to now (default)
    - "all": All available raids
    - "custom": Use start_date and end_date parameters
    """
    # Check if attendance export is enabled
    if not settings.ENABLE_ATTENDANCE_EXPORT:
        raise HTTPException(
            status_code=403,
            detail="Attendance export functionality is disabled",
        )

    logger.info(
        f"Export team image called: team_id={team_id}, period={period}, raid_count={raid_count}"
    )

    # Validate raid_count
    if raid_count < 1 or raid_count > 50:
        raise HTTPException(
            status_code=400, detail="raid_count must be between 1 and 50"
        )

    # Get team and verify it exists
    team = get_team_or_404(db, team_id)
    logger.info(f"Team found: {team.name}")

    # Get guild
    guild = db.query(Guild).filter(Guild.id == team.guild_id).first()
    if not guild:
        raise HTTPException(status_code=404, detail="Guild not found")
    logger.info(f"Guild found: {guild.name}")

    # Determine date range
    if period == "current":
        start_date, end_date = get_current_period()
        logger.info(f"Current period: {start_date} to {end_date}")
    elif period == "all":
        start_date = None
        end_date = None
        logger.info("Using all raids")
    elif period == "custom":
        if not start_date or not end_date:
            raise HTTPException(
                status_code=400,
                detail="start_date and end_date are required for custom period",
            )
        logger.info(f"Custom period: {start_date} to {end_date}")
    else:
        raise HTTPException(
            status_code=400,
            detail="period must be 'current', 'all', or 'custom'",
        )

    # Get raids for the team
    raid_query = db.query(Raid).filter(Raid.team_id == team_id)

    # Debug: Show all raids for this team
    all_raids = db.query(Raid).filter(Raid.team_id == team_id).all()
    logger.info(f"All raids for team {team_id}: {len(all_raids)} total")
    for raid in all_raids[:5]:  # Show first 5 raids
        logger.info(
            f"  Raid {raid.id}: {raid.scheduled_at} - {raid.scenario_name}"
        )

    if start_date and end_date:
        raid_query = raid_query.filter(
            Raid.scheduled_at >= start_date, Raid.scheduled_at <= end_date
        )

    raids = (
        raid_query.order_by(Raid.scheduled_at.desc()).limit(raid_count).all()
    )
    logger.info(
        f"Found {len(raids)} raids for team {team_id} in period {start_date} to {end_date}"
    )

    if not raids:
        raise HTTPException(
            status_code=404,
            detail="No raids found for the specified team and period",
        )

    # Get team view data
    raid_ids = [raid.id for raid in raids]

    # Get all toons that have attendance records for these raids
    toon_ids = (
        db.query(Attendance.toon_id)
        .filter(Attendance.raid_id.in_(raid_ids))
        .distinct()
        .all()
    )
    toon_ids = [toon_id[0] for toon_id in toon_ids]
    logger.info(f"Found {len(toon_ids)} toons with attendance records")

    # Get toon details
    toons = db.query(Toon).filter(Toon.id.in_(toon_ids)).all()

    # Get all attendance records for these raids and toons
    attendance_records = (
        db.query(Attendance)
        .filter(
            Attendance.raid_id.in_(raid_ids), Attendance.toon_id.in_(toon_ids)
        )
        .all()
    )

    # Build team view data
    team_view_toons = []

    for toon in toons:
        # Get attendance records for this toon
        toon_attendance = [
            record for record in attendance_records if record.toon_id == toon.id
        ]

        # Calculate overall attendance percentage (excluding benched)
        total_raids = len(toon_attendance)
        present_count = sum(
            1
            for record in toon_attendance
            if record.status == AttendanceStatus.PRESENT
        )
        benched_count = sum(
            1
            for record in toon_attendance
            if record.status == AttendanceStatus.BENCHED
        )

        # Calculate percentage excluding benched from denominator
        effective_total = total_raids - benched_count
        attendance_percentage = (
            (present_count / effective_total * 100)
            if effective_total > 0
            else 0.0
        )

        # Build attendance records for this toon
        toon_attendance_records = []
        for raid in raids:
            record = next(
                (r for r in toon_attendance if r.raid_id == raid.id), None
            )
            if record:
                # Clean up notes for display
                notes = record.notes
                benched_note = record.benched_note

                # Remove "Benched Note:" prefix and "Notes: Not present in warcraftlogs report"
                if benched_note and benched_note.startswith("Benched Note:"):
                    benched_note = benched_note[13:].strip()
                if notes and notes == "Not present in warcraftlogs report":
                    notes = None

                has_note = bool(notes or benched_note)

                toon_attendance_records.append(
                    ToonAttendanceRecord(
                        raid_id=raid.id,
                        raid_date=raid.scheduled_at,
                        status=record.status.value,
                        notes=notes,
                        benched_note=benched_note,
                        has_note=has_note,
                    )
                )

        team_view_toons.append(
            TeamViewToon(
                id=toon.id,
                username=toon.username,
                class_name=toon.class_,
                role=toon.role,
                overall_attendance_percentage=attendance_percentage,
                attendance_records=toon_attendance_records,
            )
        )

    # Build raid data
    team_view_raids = []
    for raid in raids:
        team_view_raids.append(
            TeamViewRaid(
                id=raid.id,
                scheduled_at=raid.scheduled_at,
                scenario_name=raid.scenario_name,
            )
        )

    team_view_data = TeamViewData(
        team={"id": team.id, "name": team.name, "guild_id": team.guild_id},
        toons=team_view_toons,
        raids=team_view_raids,
    )

    logger.info(
        f"Generated team view data with {len(team_view_toons)} toons and {len(team_view_raids)} raids"
    )

    # Generate image
    generator = AttendanceImageGenerator()
    image_bytes = generator.generate_team_report(
        team_view_data, guild, start_date, end_date
    )

    logger.info(f"Generated image with {len(image_bytes)} bytes")

    # Create filename
    team_name = team.name.replace(" ", "_").replace("/", "_")
    guild_name = guild.name.replace(" ", "_").replace("/", "_")
    date_str = datetime.now().strftime("%Y%m%d")
    filename = f"{guild_name}_{team_name}_attendance_{date_str}.png"

    logger.info(f"Returning image with filename: {filename}")

    return Response(
        content=image_bytes,
        media_type="image/png",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@router.get(
    "/export/all-teams/image",
    dependencies=[Depends(require_user)],
)
def export_all_teams_attendance_images(
    guild_id: Optional[int] = None,
    period: str = "current",  # "current", "all", or "custom"
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    raid_count: int = 20,  # Max raids to include per team
    db: Session = Depends(get_db),
    current_user: User = Depends(require_user),
):
    """
    Export attendance images for all teams as a ZIP file.
    Any valid token required.

    Period options:
    - "current": From previous Tuesday to now (default)
    - "all": All available raids
    - "custom": Use start_date and end_date parameters
    """
    # Check if attendance export is enabled
    if not settings.ENABLE_ATTENDANCE_EXPORT:
        raise HTTPException(
            status_code=403,
            detail="Attendance export functionality is disabled",
        )
    # Validate raid_count
    if raid_count < 1 or raid_count > 50:
        raise HTTPException(
            status_code=400, detail="raid_count must be between 1 and 50"
        )

    # Get teams
    team_query = db.query(Team).filter(Team.is_active == True)
    if guild_id:
        team_query = team_query.filter(Team.guild_id == guild_id)

    teams = team_query.all()

    if not teams:
        raise HTTPException(status_code=404, detail="No active teams found")

    # Determine date range
    if period == "current":
        start_date, end_date = get_current_period()
    elif period == "all":
        start_date = None
        end_date = None
    elif period == "custom":
        if not start_date or not end_date:
            raise HTTPException(
                status_code=400,
                detail="start_date and end_date are required for custom period",
            )
    else:
        raise HTTPException(
            status_code=400,
            detail="period must be 'current', 'all', or 'custom'",
        )

    # Generate reports for each team
    generator = AttendanceImageGenerator()
    reports_data = []

    for team in teams:
        try:
            # Get guild
            guild = db.query(Guild).filter(Guild.id == team.guild_id).first()
            if not guild:
                continue

            # Get raids for the team
            raid_query = db.query(Raid).filter(Raid.team_id == team.id)

            if start_date and end_date:
                raid_query = raid_query.filter(
                    Raid.scheduled_at >= start_date,
                    Raid.scheduled_at <= end_date,
                )

            raids = (
                raid_query.order_by(Raid.scheduled_at.desc())
                .limit(raid_count)
                .all()
            )

            if not raids:
                continue

            # Get team view data (similar logic to single team export)
            raid_ids = [raid.id for raid in raids]

            toon_ids = (
                db.query(Attendance.toon_id)
                .filter(Attendance.raid_id.in_(raid_ids))
                .distinct()
                .all()
            )
            toon_ids = [toon_id[0] for toon_id in toon_ids]

            toons = db.query(Toon).filter(Toon.id.in_(toon_ids)).all()

            attendance_records = (
                db.query(Attendance)
                .filter(
                    Attendance.raid_id.in_(raid_ids),
                    Attendance.toon_id.in_(toon_ids),
                )
                .all()
            )

            team_view_toons = []
            for toon in toons:
                toon_attendance = [
                    record
                    for record in attendance_records
                    if record.toon_id == toon.id
                ]

                total_raids = len(toon_attendance)
                present_count = sum(
                    1
                    for record in toon_attendance
                    if record.status == AttendanceStatus.PRESENT
                )
                benched_count = sum(
                    1
                    for record in toon_attendance
                    if record.status == AttendanceStatus.BENCHED
                )

                effective_total = total_raids - benched_count
                attendance_percentage = (
                    (present_count / effective_total * 100)
                    if effective_total > 0
                    else 0.0
                )

                toon_attendance_records = []
                for raid in raids:
                    record = next(
                        (r for r in toon_attendance if r.raid_id == raid.id),
                        None,
                    )
                    if record:
                        notes = record.notes
                        benched_note = record.benched_note

                        if benched_note and benched_note.startswith(
                            "Benched Note:"
                        ):
                            benched_note = benched_note[13:].strip()
                        if (
                            notes
                            and notes == "Not present in warcraftlogs report"
                        ):
                            notes = None

                        has_note = bool(notes or benched_note)

                        toon_attendance_records.append(
                            ToonAttendanceRecord(
                                raid_id=raid.id,
                                raid_date=raid.scheduled_at,
                                status=record.status.value,
                                notes=notes,
                                benched_note=benched_note,
                                has_note=has_note,
                            )
                        )

                team_view_toons.append(
                    TeamViewToon(
                        id=toon.id,
                        username=toon.username,
                        class_name=toon.class_,
                        role=toon.role,
                        overall_attendance_percentage=attendance_percentage,
                        attendance_records=toon_attendance_records,
                    )
                )

            team_view_raids = []
            for raid in raids:
                team_view_raids.append(
                    TeamViewRaid(
                        id=raid.id,
                        scheduled_at=raid.scheduled_at,
                        scenario_name=raid.scenario_name,
                    )
                )

            team_view_data = TeamViewData(
                team={
                    "id": team.id,
                    "name": team.name,
                    "guild_id": team.guild_id,
                },
                toons=team_view_toons,
                raids=team_view_raids,
            )

            reports_data.append((team_view_data, guild, start_date, end_date))

        except Exception as e:
            # Skip teams that fail to generate
            continue

    if not reports_data:
        raise HTTPException(
            status_code=404, detail="No valid team reports could be generated"
        )

    # Generate ZIP file
    zip_bytes = generator.generate_multiple_reports(reports_data)

    # Create filename
    guild_name = (
        "All_Guilds"
        if not guild_id
        else reports_data[0][1].name.replace(" ", "_").replace("/", "_")
    )
    date_str = datetime.now().strftime("%Y%m%d")
    filename = f"{guild_name}_all_teams_attendance_{date_str}.zip"

    return Response(
        content=zip_bytes,
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
