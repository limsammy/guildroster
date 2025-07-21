from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from app.database import get_db
from app.models.attendance import Attendance
from app.models.raid import Raid
from app.models.toon import Toon
from app.models.team import Team
from app.schemas.attendance import (
    AttendanceCreate,
    AttendanceUpdate,
    AttendanceResponse,
    AttendanceBulkCreate,
    AttendanceBulkUpdate,
    AttendanceBulkUpdateItem,
    AttendanceStats,
    AttendanceReport,
)
from app.models.token import Token
from app.utils.auth import require_any_token, require_superuser
from app.models.user import User

router = APIRouter(prefix="/attendance", tags=["Attendance"])


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
        is_present=attendance_in.is_present,
        notes=attendance_in.notes,
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
            is_present=record.is_present,
            notes=record.notes,
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
    dependencies=[Depends(require_any_token)],
)
def list_attendance(
    raid_id: Optional[int] = None,
    toon_id: Optional[int] = None,
    team_id: Optional[int] = None,
    is_present: Optional[bool] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_token: Token = Depends(require_any_token),
):
    """
    List attendance records with filtering options. Any valid token required.
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

    if is_present is not None:
        query = query.filter(Attendance.is_present == is_present)

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
        if "is_present" in update_data:
            attendance.is_present = update_data["is_present"]  # type: ignore[assignment]
        if "notes" in update_data:
            attendance.notes = update_data["notes"]  # type: ignore[assignment]
        updated_records.append(attendance)

    db.commit()

    # Refresh all updated records
    for record in updated_records:
        db.refresh(record)

    return updated_records


@router.get(
    "/{attendance_id}",
    response_model=AttendanceResponse,
    dependencies=[Depends(require_any_token)],
)
def get_attendance(
    attendance_id: int,
    db: Session = Depends(get_db),
    current_token: Token = Depends(require_any_token),
):
    """
    Get attendance record by ID. Any valid token required.
    """
    attendance = get_attendance_or_404(db, attendance_id)
    return attendance


@router.get(
    "/raid/{raid_id}",
    response_model=List[AttendanceResponse],
    dependencies=[Depends(require_any_token)],
)
def get_attendance_by_raid(
    raid_id: int,
    db: Session = Depends(get_db),
    current_token: Token = Depends(require_any_token),
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
    dependencies=[Depends(require_any_token)],
)
def get_attendance_by_toon(
    toon_id: int,
    db: Session = Depends(get_db),
    current_token: Token = Depends(require_any_token),
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
    dependencies=[Depends(require_any_token)],
)
def get_attendance_by_team(
    team_id: int,
    db: Session = Depends(get_db),
    current_token: Token = Depends(require_any_token),
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

    if attendance_in.is_present is not None:
        attendance.is_present = attendance_in.is_present  # type: ignore[assignment]

    if attendance_in.notes is not None:
        attendance.notes = attendance_in.notes  # type: ignore[assignment]

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
    dependencies=[Depends(require_any_token)],
)
def get_raid_attendance_stats(
    raid_id: int,
    db: Session = Depends(get_db),
    current_token: Token = Depends(require_any_token),
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
    present_count = sum(1 for record in attendance_records if record.is_present)
    absent_count = total_records - present_count

    attendance_percentage = (
        (present_count / total_records * 100) if total_records > 0 else 0.0
    )

    return AttendanceStats(
        total_raids=1,  # Single raid
        raids_attended=present_count,
        raids_missed=absent_count,
        attendance_percentage=attendance_percentage,
        current_streak=0,  # Not applicable for single raid
        longest_streak=0,  # Not applicable for single raid
        last_attendance=raid.scheduled_at if present_count > 0 else None,
    )


@router.get(
    "/stats/toon/{toon_id}",
    response_model=AttendanceStats,
    dependencies=[Depends(require_any_token)],
)
def get_toon_attendance_stats(
    toon_id: int,
    db: Session = Depends(get_db),
    current_token: Token = Depends(require_any_token),
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
        1 for record in attendance_records if record.is_present
    )
    raids_missed = total_raids - raids_attended

    attendance_percentage = (
        (raids_attended / total_raids * 100) if total_raids > 0 else 0.0
    )

    # Calculate streaks
    current_streak = 0
    longest_streak = 0
    temp_streak = 0

    for record in reversed(attendance_records):  # Start from most recent
        if record.is_present:
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
        if last_record.is_present:
            last_attendance = last_record.raid.scheduled_at

    return AttendanceStats(
        total_raids=total_raids,
        raids_attended=raids_attended,
        raids_missed=raids_missed,
        attendance_percentage=attendance_percentage,
        current_streak=current_streak,
        longest_streak=longest_streak,
        last_attendance=last_attendance,
    )


@router.get(
    "/stats/team/{team_id}",
    response_model=AttendanceStats,
    dependencies=[Depends(require_any_token)],
)
def get_team_attendance_stats(
    team_id: int,
    db: Session = Depends(get_db),
    current_token: Token = Depends(require_any_token),
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
        1 for record in attendance_records if record.is_present
    )
    raids_missed = total_raids - raids_attended

    attendance_percentage = (
        (raids_attended / total_raids * 100) if total_raids > 0 else 0.0
    )

    # For team stats, we'll use simplified streak calculation
    current_streak = 0
    longest_streak = 0
    temp_streak = 0

    for record in reversed(attendance_records):
        if record.is_present:
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
        if last_record.is_present:
            last_attendance = last_record.raid.scheduled_at

    return AttendanceStats(
        total_raids=total_raids,
        raids_attended=raids_attended,
        raids_missed=raids_missed,
        attendance_percentage=attendance_percentage,
        current_streak=current_streak,
        longest_streak=longest_streak,
        last_attendance=last_attendance,
    )


@router.get(
    "/report/date-range",
    response_model=AttendanceReport,
    dependencies=[Depends(require_any_token)],
)
def get_attendance_report(
    start_date: datetime,
    end_date: datetime,
    team_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_token: Token = Depends(require_any_token),
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
    present_count = sum(1 for record in attendance_records if record.is_present)
    absent_count = total_attendance_records - present_count
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
        raid_present = sum(1 for r in raid_attendance if r.is_present)
        raid_absent = len(raid_attendance) - raid_present

        attendance_by_raid.append(
            {
                "raid_id": raid.id,
                "raid_name": f"Raid {raid.id}",
                "scheduled_at": raid.scheduled_at,
                "present": raid_present,
                "absent": raid_absent,
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
        toon_present = sum(1 for r in toon_attendance if r.is_present)
        toon_absent = len(toon_attendance) - toon_present

        attendance_by_toon.append(
            {
                "toon_id": toon_id,
                "present": toon_present,
                "absent": toon_absent,
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
        overall_attendance_rate=overall_attendance_rate,
        attendance_by_raid=attendance_by_raid,
        attendance_by_toon=attendance_by_toon,
    )
