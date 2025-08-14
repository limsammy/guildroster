import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.main import app
from app.models.attendance import Attendance, AttendanceStatus
from app.models.raid import Raid
from app.models.toon import Toon
from app.models.team import Team
from app.models.guild import Guild
from app.models.user import User
from app.models.token import Token
from app.database import get_db


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def db_session():
    """Get database session for testing."""
    for session in get_db():
        yield session
        break


@pytest.fixture
def test_user(db_session: Session):
    """Create a test user."""
    user = User(
        username="testuser",
        hashed_password="hashed_password",
        is_active=True,
        is_superuser=False
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_token(db_session: Session, test_user: User):
    """Create a test token."""
    token = Token(
        key="test_token_key",
        user_id=test_user.id,
        token_type="user",
        name="Test Token"
    )
    db_session.add(token)
    db_session.commit()
    db_session.refresh(token)
    return token


@pytest.fixture
def test_guild(db_session: Session, test_user: User):
    """Create a test guild."""
    guild = Guild(
        name="Test Guild",
        created_by=test_user.id
    )
    db_session.add(guild)
    db_session.commit()
    db_session.refresh(guild)
    return guild


@pytest.fixture
def test_team(db_session: Session, test_guild: Guild, test_user: User):
    """Create a test team."""
    team = Team(
        name="Test Team",
        guild_id=test_guild.id,
        created_by=test_user.id
    )
    db_session.add(team)
    db_session.commit()
    db_session.refresh(team)
    return team


@pytest.fixture
def test_toon(db_session: Session):
    """Create a test toon."""
    toon = Toon(
        username="TestToon",
        class_="Warrior",
        role="Tank"
    )
    db_session.add(toon)
    db_session.commit()
    db_session.refresh(toon)
    return toon


@pytest.fixture
def test_raids(db_session: Session, test_team: Team):
    """Create test raids."""
    raids = []
    for i in range(3):
        raid = Raid(
            scheduled_at=datetime.now() - timedelta(days=i),
            team_id=test_team.id,
            scenario_name=f"Test Scenario {i+1}",
            scenario_difficulty="Mythic",
            scenario_size="20"
        )
        db_session.add(raid)
        raids.append(raid)
    
    db_session.commit()
    for raid in raids:
        db_session.refresh(raid)
    return raids


def test_get_team_attendance_view_success(
    client: TestClient,
    db_session: Session,
    test_token: Token,
    test_team: Team,
    test_toon: Toon,
    test_raids: list[Raid]
):
    """Test successful team attendance view retrieval."""
    # Create attendance records
    for i, raid in enumerate(test_raids):
        status = AttendanceStatus.PRESENT if i < 2 else AttendanceStatus.ABSENT
        attendance = Attendance(
            raid_id=raid.id,
            toon_id=test_toon.id,
            status=status,
            notes=f"Test note {i}" if i == 0 else None
        )
        db_session.add(attendance)
    
    db_session.commit()

    # Make request
    response = client.get(
        f"/attendance/team-view/{test_team.id}",
        headers={"Authorization": f"Bearer {test_token.key}"}
    )

    # Assert response
    assert response.status_code == 200
    data = response.json()
    
    # Check team info
    assert data["team"]["id"] == test_team.id
    assert data["team"]["name"] == test_team.name
    assert data["team"]["guild_id"] == test_team.guild_id
    
    # Check raids
    assert len(data["raids"]) == 3
    assert data["raids"][0]["id"] == test_raids[2].id  # Oldest raid first (earliest to latest)
    
    # Check toons
    assert len(data["toons"]) == 1
    toon_data = data["toons"][0]
    assert toon_data["id"] == test_toon.id
    assert toon_data["username"] == test_toon.username
    assert toon_data["class_name"] == test_toon.class_
    assert toon_data["role"] == test_toon.role
    
    # Check attendance percentage (2 present out of 3 total, so 66.67%)
    assert toon_data["overall_attendance_percentage"] == pytest.approx(66.67, abs=0.01)
    
    # Check attendance records (order is now oldest to newest)
    assert len(toon_data["attendance_records"]) == 3
    assert toon_data["attendance_records"][0]["status"] == "absent"  # Oldest raid (test_raids[2])
    assert toon_data["attendance_records"][0]["has_note"] == False
    assert toon_data["attendance_records"][1]["status"] == "present"  # Middle raid (test_raids[1])
    assert toon_data["attendance_records"][1]["has_note"] == False
    assert toon_data["attendance_records"][2]["status"] == "present"  # Newest raid (test_raids[0])
    assert toon_data["attendance_records"][2]["has_note"] == True


def test_get_team_attendance_view_with_benched(
    client: TestClient,
    db_session: Session,
    test_token: Token,
    test_team: Team,
    test_toon: Toon,
    test_raids: list[Raid]
):
    """Test team attendance view with benched status (should be excluded from percentage)."""
    # Create attendance records: present, benched, absent
    attendance_records = [
        Attendance(
            raid_id=test_raids[0].id,
            toon_id=test_toon.id,
            status=AttendanceStatus.PRESENT
        ),
        Attendance(
            raid_id=test_raids[1].id,
            toon_id=test_toon.id,
            status=AttendanceStatus.BENCHED,
            benched_note="Was benched"
        ),
        Attendance(
            raid_id=test_raids[2].id,
            toon_id=test_toon.id,
            status=AttendanceStatus.ABSENT
        )
    ]
    
    for attendance in attendance_records:
        db_session.add(attendance)
    db_session.commit()

    # Make request
    response = client.get(
        f"/attendance/team-view/{test_team.id}",
        headers={"Authorization": f"Bearer {test_token.key}"}
    )

    # Assert response
    assert response.status_code == 200
    data = response.json()
    
    # Check attendance percentage (1 present out of 2 effective raids, so 50%)
    toon_data = data["toons"][0]
    assert toon_data["overall_attendance_percentage"] == pytest.approx(50.0, abs=0.01)
    
    # Check benched record has note (order is now oldest to newest)
    benched_record = toon_data["attendance_records"][1]  # Middle raid (test_raids[1])
    assert benched_record["status"] == "benched"
    assert benched_record["has_note"] == True
    assert benched_record["benched_note"] == "Was benched"


def test_get_team_attendance_view_no_raids(
    client: TestClient,
    db_session: Session,
    test_token: Token,
    test_team: Team
):
    """Test team attendance view when team has no raids."""
    response = client.get(
        f"/attendance/team-view/{test_team.id}",
        headers={"Authorization": f"Bearer {test_token.key}"}
    )

    assert response.status_code == 200
    data = response.json()
    
    assert data["team"]["id"] == test_team.id
    assert data["toons"] == []
    assert data["raids"] == []


def test_get_team_attendance_view_invalid_team(
    client: TestClient,
    test_token: Token
):
    """Test team attendance view with invalid team ID."""
    response = client.get(
        "/attendance/team-view/99999",
        headers={"Authorization": f"Bearer {test_token.key}"}
    )

    assert response.status_code == 404
    assert "Team not found" in response.json()["detail"]


def test_get_team_attendance_view_invalid_raid_count(
    client: TestClient,
    test_token: Token,
    test_team: Team
):
    """Test team attendance view with invalid raid count."""
    response = client.get(
        f"/attendance/team-view/{test_team.id}?raid_count=0",
        headers={"Authorization": f"Bearer {test_token.key}"}
    )

    assert response.status_code == 400
    assert "raid_count must be between 1 and 50" in response.json()["detail"]


def test_get_team_attendance_view_with_guild_filter(
    client: TestClient,
    db_session: Session,
    test_token: Token,
    test_team: Team,
    test_guild: Guild
):
    """Test team attendance view with guild filter."""
    response = client.get(
        f"/attendance/team-view/{test_team.id}?guild_id={test_guild.id}",
        headers={"Authorization": f"Bearer {test_token.key}"}
    )

    assert response.status_code == 200


def test_get_team_attendance_view_wrong_guild(
    client: TestClient,
    db_session: Session,
    test_token: Token,
    test_team: Team,
    test_user: User
):
    """Test team attendance view with wrong guild ID."""
    # Create another guild
    other_guild = Guild(
        name="Other Guild",
        created_by=test_user.id
    )
    db_session.add(other_guild)
    db_session.commit()
    db_session.refresh(other_guild)

    response = client.get(
        f"/attendance/team-view/{test_team.id}?guild_id={other_guild.id}",
        headers={"Authorization": f"Bearer {test_token.key}"}
    )

    assert response.status_code == 400
    assert "Team does not belong to the specified guild" in response.json()["detail"] 