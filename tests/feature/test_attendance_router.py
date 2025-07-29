# type: ignore[comparison-overlap,assignment,arg-type]
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.models.user import User
from app.models.guild import Guild
from app.models.team import Team
from app.models.scenario import Scenario, SCENARIO_DIFFICULTIES, SCENARIO_SIZES
from app.models.raid import Raid
from app.models.toon import Toon
from app.models.attendance import Attendance, AttendanceStatus
from app.models.token import Token
from app.utils.password import hash_password


class TestAttendanceAPI:
    def _create_superuser(self, db_session: Session):
        """Helper method to create a superuser with token."""
        user = User(
            username="superuser",
            hashed_password=hash_password("superpassword123"),
            is_active=True,
            is_superuser=True,
        )
        db_session.add(user)
        db_session.commit()
        user_id = user.id
        token = Token.create_user_token(user_id, "Superuser Token")  # type: ignore[arg-type]
        db_session.add(token)
        db_session.commit()
        return user_id, token.key

    def _create_regular_user(self, db_session: Session):
        """Helper method to create a regular user with token."""
        user = User(
            username="regularuser",
            hashed_password=hash_password("userpassword123"),
            is_active=True,
            is_superuser=False,
        )
        db_session.add(user)
        db_session.commit()
        user_id = user.id
        token = Token.create_user_token(user_id, "User Token")  # type: ignore[arg-type]
        db_session.add(token)
        db_session.commit()
        return user_id, token.key

    def _create_test_data(self, db_session: Session, user_id: int):
        """Helper method to create all necessary test data."""
        # Create guild
        guild = Guild(name="Test Guild", created_by=user_id)
        db_session.add(guild)
        db_session.commit()

        # Create team
        team = Team(
            name="Test Team",
            guild_id=guild.id,
            created_by=user_id,
        )
        db_session.add(team)
        db_session.commit()

        # Create scenario
        scenario = Scenario(
            name="Test Scenario",
            difficulty=SCENARIO_DIFFICULTIES[0],
            size=SCENARIO_SIZES[0],
            is_active=True,
        )
        db_session.add(scenario)
        db_session.commit()

        # Create toon
        toon = Toon(username="TestToon", class_="Mage", role="Ranged DPS")
        db_session.add(toon)
        db_session.commit()

        # Create raid
        raid = Raid(
            scheduled_at=datetime.now() + timedelta(days=1),
            scenario_id=scenario.id,
            team_id=team.id,
        )
        db_session.add(raid)
        db_session.commit()

        return {
            "guild_id": guild.id,
            "team_id": team.id,
            "scenario_id": scenario.id,
            "toon_id": toon.id,
            "raid_id": raid.id,
        }

    def test_create_attendance_superuser(
        self, client: TestClient, db_session: Session
    ):
        """Test creating attendance record as superuser."""
        user_id, token_key = self._create_superuser(db_session)
        test_data = self._create_test_data(db_session, user_id)

        headers = {"Authorization": f"Bearer {token_key}"}
        data = {
            "raid_id": test_data["raid_id"],
            "toon_id": test_data["toon_id"],
            "status": "present",
            "notes": "On time and performed well",
        }
        response = client.post("/attendance/", json=data, headers=headers)
        assert response.status_code == 201
        resp = response.json()
        assert resp["raid_id"] == test_data["raid_id"]
        assert resp["toon_id"] == test_data["toon_id"]
        assert resp["status"] == "present"
        assert resp["notes"] == "On time and performed well"
        assert "id" in resp
        assert "created_at" in resp
        assert "updated_at" in resp

    def test_create_attendance_regular_user_forbidden(
        self, client: TestClient, db_session: Session
    ):
        """Test that regular users cannot create attendance records."""
        user_id, token_key = self._create_regular_user(db_session)
        test_data = self._create_test_data(db_session, user_id)

        headers = {"Authorization": f"Bearer {token_key}"}
        data = {
            "raid_id": test_data["raid_id"],
            "toon_id": test_data["toon_id"],
            "status": "present",
        }
        response = client.post("/attendance/", json=data, headers=headers)
        assert response.status_code == 403

    def test_create_attendance_duplicate(
        self, client: TestClient, db_session: Session
    ):
        """Test that duplicate attendance records are rejected."""
        user_id, token_key = self._create_superuser(db_session)
        test_data = self._create_test_data(db_session, user_id)

        headers = {"Authorization": f"Bearer {token_key}"}
        data = {
            "raid_id": test_data["raid_id"],
            "toon_id": test_data["toon_id"],
            "is_present": True,
        }

        # Create first attendance record
        response = client.post("/attendance/", json=data, headers=headers)
        assert response.status_code == 201

        # Try to create duplicate
        response = client.post("/attendance/", json=data, headers=headers)
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]

    def test_create_attendance_raid_not_found(
        self, client: TestClient, db_session: Session
    ):
        """Test creating attendance with non-existent raid."""
        user_id, token_key = self._create_superuser(db_session)
        test_data = self._create_test_data(db_session, user_id)

        headers = {"Authorization": f"Bearer {token_key}"}
        data = {
            "raid_id": 999,  # Non-existent raid
            "toon_id": test_data["toon_id"],
            "is_present": True,
        }
        response = client.post("/attendance/", json=data, headers=headers)
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_create_attendance_toon_not_found(
        self, client: TestClient, db_session: Session
    ):
        """Test creating attendance with non-existent toon."""
        user_id, token_key = self._create_superuser(db_session)
        test_data = self._create_test_data(db_session, user_id)

        headers = {"Authorization": f"Bearer {token_key}"}
        data = {
            "raid_id": test_data["raid_id"],
            "toon_id": 999,  # Non-existent toon
            "is_present": True,
        }
        response = client.post("/attendance/", json=data, headers=headers)
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_create_attendance_bulk_superuser(
        self, client: TestClient, db_session: Session
    ):
        """Test creating multiple attendance records as superuser."""
        user_id, token_key = self._create_superuser(db_session)
        test_data = self._create_test_data(db_session, user_id)

        # Create second toon for bulk test
        toon2 = Toon(
            username="TestToon2",
            class_="Priest",
            role="Healer",
        )
        db_session.add(toon2)
        db_session.commit()
        toon2_id = toon2.id  # Capture the ID immediately after commit

        headers = {"Authorization": f"Bearer {token_key}"}
        data = {
            "attendance_records": [
                {
                    "raid_id": test_data["raid_id"],
                    "toon_id": test_data["toon_id"],
                    "status": "present",
                    "notes": "On time",
                },
                {
                    "raid_id": test_data["raid_id"],
                    "toon_id": toon2_id,
                    "status": "absent",
                    "notes": "No show",
                },
            ]
        }
        response = client.post("/attendance/bulk", json=data, headers=headers)
        assert response.status_code == 201
        resp = response.json()
        assert len(resp) == 2
        assert resp[0]["raid_id"] == test_data["raid_id"]
        assert resp[0]["toon_id"] == test_data["toon_id"]
        assert resp[0]["status"] == "present"
        assert resp[1]["toon_id"] == toon2_id
        assert resp[1]["status"] == "absent"

    def test_list_attendance(self, client: TestClient, db_session: Session):
        """Test listing attendance records."""
        user_id, token_key = self._create_superuser(db_session)
        test_data = self._create_test_data(db_session, user_id)

        # Create attendance record
        attendance = Attendance(
            raid_id=test_data["raid_id"],
            toon_id=test_data["toon_id"],
            status=AttendanceStatus.PRESENT,
        )
        db_session.add(attendance)
        db_session.commit()

        headers = {"Authorization": f"Bearer {token_key}"}
        response = client.get("/attendance/", headers=headers)
        assert response.status_code == 200
        resp = response.json()
        assert len(resp) == 1
        assert resp[0]["raid_id"] == test_data["raid_id"]
        assert resp[0]["toon_id"] == test_data["toon_id"]

    def test_list_attendance_filter_by_raid(
        self, client: TestClient, db_session: Session
    ):
        """Test filtering attendance by raid."""
        user_id, token_key = self._create_superuser(db_session)
        test_data = self._create_test_data(db_session, user_id)

        # Create second raid
        raid2 = Raid(
            scheduled_at=datetime.now() + timedelta(days=2),
            scenario_id=test_data["scenario_id"],
            team_id=test_data["team_id"],
        )
        db_session.add(raid2)
        db_session.commit()

        # Create attendance records for both raids
        attendance1 = Attendance(
            raid_id=test_data["raid_id"],
            toon_id=test_data["toon_id"],
            is_present=True,
        )
        attendance2 = Attendance(
            raid_id=raid2.id, toon_id=test_data["toon_id"], is_present=False
        )
        db_session.add_all([attendance1, attendance2])
        db_session.commit()

        headers = {"Authorization": f"Bearer {token_key}"}
        response = client.get(
            f"/attendance/?raid_id={test_data['raid_id']}", headers=headers
        )
        assert response.status_code == 200
        resp = response.json()
        assert len(resp) == 1
        assert resp[0]["raid_id"] == test_data["raid_id"]

    def test_list_attendance_filter_by_toon(
        self, client: TestClient, db_session: Session
    ):
        """Test filtering attendance by toon."""
        user_id, token_key = self._create_superuser(db_session)
        test_data = self._create_test_data(db_session, user_id)

        # Create second toon
        member2 = Member(
            guild_id=test_data["guild_id"],
            display_name="Test Member 2",
            team_id=test_data["team_id"],
        )
        db_session.add(member2)
        db_session.commit()

        toon2 = Toon(
            member_id=member2.id,
            username="TestToon2",
            class_="Priest",
            role="Healer",
        )
        db_session.add(toon2)
        db_session.commit()
        toon2_id = toon2.id  # Capture the ID immediately after commit

        # Create attendance records for both toons
        attendance1 = Attendance(
            raid_id=test_data["raid_id"],
            toon_id=test_data["toon_id"],
            is_present=True,
        )
        attendance2 = Attendance(
            raid_id=test_data["raid_id"], toon_id=toon2_id, is_present=False
        )
        db_session.add_all([attendance1, attendance2])
        db_session.commit()

        headers = {"Authorization": f"Bearer {token_key}"}
        response = client.get(
            f"/attendance/?toon_id={test_data['toon_id']}", headers=headers
        )
        assert response.status_code == 200
        resp = response.json()
        assert len(resp) == 1
        assert resp[0]["toon_id"] == test_data["toon_id"]

    def test_list_attendance_filter_by_member(
        self, client: TestClient, db_session: Session
    ):
        """Test filtering attendance by member."""
        user_id, token_key = self._create_superuser(db_session)
        test_data = self._create_test_data(db_session, user_id)

        # Create second toon for same member
        toon2 = Toon(
            member_id=test_data["member_id"],
            username="TestToon2",
            class_="Priest",
            role="Healer",
        )
        db_session.add(toon2)
        db_session.commit()
        toon2_id = toon2.id  # Capture the ID immediately after commit

        # Create attendance records for both toons
        attendance1 = Attendance(
            raid_id=test_data["raid_id"],
            toon_id=test_data["toon_id"],
            is_present=True,
        )
        attendance2 = Attendance(
            raid_id=test_data["raid_id"], toon_id=toon2_id, is_present=False
        )
        db_session.add_all([attendance1, attendance2])
        db_session.commit()

        headers = {"Authorization": f"Bearer {token_key}"}
        response = client.get(
            f"/attendance/?member_id={test_data['member_id']}", headers=headers
        )
        assert response.status_code == 200
        resp = response.json()
        assert len(resp) == 2

    def test_list_attendance_filter_by_team(
        self, client: TestClient, db_session: Session
    ):
        """Test filtering attendance by team."""
        user_id, token_key = self._create_superuser(db_session)
        test_data = self._create_test_data(db_session, user_id)

        # Create second raid for same team
        raid2 = Raid(
            scheduled_at=datetime.now() + timedelta(days=2),
            scenario_id=test_data["scenario_id"],
            team_id=test_data["team_id"],
        )
        db_session.add(raid2)
        db_session.commit()

        # Create attendance records for both raids
        attendance1 = Attendance(
            raid_id=test_data["raid_id"],
            toon_id=test_data["toon_id"],
            is_present=True,
        )
        attendance2 = Attendance(
            raid_id=raid2.id, toon_id=test_data["toon_id"], is_present=False
        )
        db_session.add_all([attendance1, attendance2])
        db_session.commit()

        headers = {"Authorization": f"Bearer {token_key}"}
        response = client.get(
            f"/attendance/?team_id={test_data['team_id']}", headers=headers
        )
        assert response.status_code == 200
        resp = response.json()
        assert len(resp) == 2

    def test_list_attendance_filter_by_present(
        self, client: TestClient, db_session: Session
    ):
        """Test filtering attendance by present status."""
        user_id, token_key = self._create_superuser(db_session)
        test_data = self._create_test_data(db_session, user_id)

        # Create second toon
        member2 = Member(
            guild_id=test_data["guild_id"],
            display_name="Test Member 2",
            team_id=test_data["team_id"],
        )
        db_session.add(member2)
        db_session.commit()

        toon2 = Toon(
            member_id=member2.id,
            username="TestToon2",
            class_="Priest",
            role="Healer",
        )
        db_session.add(toon2)
        db_session.commit()
        toon2_id = toon2.id  # Capture the ID immediately after commit

        # Create attendance records with different present status
        attendance1 = Attendance(
            raid_id=test_data["raid_id"],
            toon_id=test_data["toon_id"],
            is_present=True,
        )
        attendance2 = Attendance(
            raid_id=test_data["raid_id"], toon_id=toon2_id, is_present=False
        )
        db_session.add_all([attendance1, attendance2])
        db_session.commit()

        headers = {"Authorization": f"Bearer {token_key}"}
        response = client.get("/attendance/?is_present=true", headers=headers)
        assert response.status_code == 200
        resp = response.json()
        assert len(resp) == 1
        assert resp[0]["is_present"] is True

    def test_get_attendance_by_id(
        self, client: TestClient, db_session: Session
    ):
        """Test getting attendance record by ID."""
        user_id, token_key = self._create_superuser(db_session)
        test_data = self._create_test_data(db_session, user_id)

        attendance = Attendance(
            raid_id=test_data["raid_id"],
            toon_id=test_data["toon_id"],
            is_present=True,
            notes="Test notes",
        )
        db_session.add(attendance)
        db_session.commit()

        headers = {"Authorization": f"Bearer {token_key}"}
        response = client.get(f"/attendance/{attendance.id}", headers=headers)
        assert response.status_code == 200
        resp = response.json()
        assert resp["id"] == attendance.id
        assert resp["raid_id"] == test_data["raid_id"]
        assert resp["toon_id"] == test_data["toon_id"]
        assert resp["notes"] == "Test notes"

    def test_get_attendance_not_found(
        self, client: TestClient, db_session: Session
    ):
        """Test getting non-existent attendance record."""
        user_id, token_key = self._create_superuser(db_session)

        headers = {"Authorization": f"Bearer {token_key}"}
        response = client.get("/attendance/999", headers=headers)
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_get_attendance_by_raid(
        self, client: TestClient, db_session: Session
    ):
        """Test getting attendance records by raid."""
        user_id, token_key = self._create_superuser(db_session)
        test_data = self._create_test_data(db_session, user_id)

        # Create second toon
        member2 = Member(
            guild_id=test_data["guild_id"],
            display_name="Test Member 2",
            team_id=test_data["team_id"],
        )
        db_session.add(member2)
        db_session.commit()

        toon2 = Toon(
            member_id=member2.id,
            username="TestToon2",
            class_="Priest",
            role="Healer",
        )
        db_session.add(toon2)
        db_session.commit()
        toon2_id = toon2.id  # Capture the ID immediately after commit

        # Create attendance records for both toons in same raid
        attendance1 = Attendance(
            raid_id=test_data["raid_id"],
            toon_id=test_data["toon_id"],
            is_present=True,
        )
        attendance2 = Attendance(
            raid_id=test_data["raid_id"], toon_id=toon2_id, is_present=False
        )
        db_session.add_all([attendance1, attendance2])
        db_session.commit()

        headers = {"Authorization": f"Bearer {token_key}"}
        response = client.get(
            f"/attendance/raid/{test_data['raid_id']}", headers=headers
        )
        assert response.status_code == 200
        resp = response.json()
        assert len(resp) == 2
        assert all(record["raid_id"] == test_data["raid_id"] for record in resp)

    def test_get_attendance_by_toon(
        self, client: TestClient, db_session: Session
    ):
        """Test getting attendance records by toon."""
        user_id, token_key = self._create_superuser(db_session)
        test_data = self._create_test_data(db_session, user_id)

        # Create second raid
        raid2 = Raid(
            scheduled_at=datetime.now() + timedelta(days=2),
            scenario_id=test_data["scenario_id"],
            team_id=test_data["team_id"],
        )
        db_session.add(raid2)
        db_session.commit()

        # Create attendance records for same toon in different raids
        attendance1 = Attendance(
            raid_id=test_data["raid_id"],
            toon_id=test_data["toon_id"],
            is_present=True,
        )
        attendance2 = Attendance(
            raid_id=raid2.id, toon_id=test_data["toon_id"], is_present=False
        )
        db_session.add_all([attendance1, attendance2])
        db_session.commit()

        headers = {"Authorization": f"Bearer {token_key}"}
        response = client.get(
            f"/attendance/toon/{test_data['toon_id']}", headers=headers
        )
        assert response.status_code == 200
        resp = response.json()
        assert len(resp) == 2
        assert all(record["toon_id"] == test_data["toon_id"] for record in resp)

    def test_get_attendance_by_member(
        self, client: TestClient, db_session: Session
    ):
        """Test getting attendance records by member."""
        user_id, token_key = self._create_superuser(db_session)
        test_data = self._create_test_data(db_session, user_id)

        # Create second toon for same member
        toon2 = Toon(
            member_id=test_data["member_id"],
            username="TestToon2",
            class_="Priest",
            role="Healer",
        )
        db_session.add(toon2)
        db_session.commit()
        toon2_id = toon2.id  # Capture the ID immediately after commit

        # Create attendance records for both toons
        attendance1 = Attendance(
            raid_id=test_data["raid_id"],
            toon_id=test_data["toon_id"],
            is_present=True,
        )
        attendance2 = Attendance(
            raid_id=test_data["raid_id"], toon_id=toon2_id, is_present=False
        )
        db_session.add_all([attendance1, attendance2])
        db_session.commit()

        headers = {"Authorization": f"Bearer {token_key}"}
        response = client.get(
            f"/attendance/member/{test_data['member_id']}", headers=headers
        )
        assert response.status_code == 200
        resp = response.json()
        assert len(resp) == 2

    def test_get_attendance_by_team(
        self, client: TestClient, db_session: Session
    ):
        """Test getting attendance records by team."""
        user_id, token_key = self._create_superuser(db_session)
        test_data = self._create_test_data(db_session, user_id)

        # Create second raid for same team
        raid2 = Raid(
            scheduled_at=datetime.now() + timedelta(days=2),
            scenario_id=test_data["scenario_id"],
            team_id=test_data["team_id"],
        )
        db_session.add(raid2)
        db_session.commit()

        # Create attendance records for both raids
        attendance1 = Attendance(
            raid_id=test_data["raid_id"],
            toon_id=test_data["toon_id"],
            is_present=True,
        )
        attendance2 = Attendance(
            raid_id=raid2.id, toon_id=test_data["toon_id"], is_present=False
        )
        db_session.add_all([attendance1, attendance2])
        db_session.commit()

        headers = {"Authorization": f"Bearer {token_key}"}
        response = client.get(
            f"/attendance/team/{test_data['team_id']}", headers=headers
        )
        assert response.status_code == 200
        resp = response.json()
        assert len(resp) == 2

    def test_update_attendance_superuser(
        self, client: TestClient, db_session: Session
    ):
        """Test updating attendance record as superuser."""
        user_id, token_key = self._create_superuser(db_session)
        test_data = self._create_test_data(db_session, user_id)

        attendance = Attendance(
            raid_id=test_data["raid_id"],
            toon_id=test_data["toon_id"],
            is_present=True,
            notes="Original notes",
        )
        db_session.add(attendance)
        db_session.commit()

        headers = {"Authorization": f"Bearer {token_key}"}
        data = {"is_present": False, "notes": "Updated notes"}
        response = client.put(
            f"/attendance/{attendance.id}", json=data, headers=headers
        )
        assert response.status_code == 200
        resp = response.json()
        assert resp["is_present"] is False
        assert resp["notes"] == "Updated notes"

    def test_update_attendance_regular_user_forbidden(
        self, client: TestClient, db_session: Session
    ):
        """Test that regular users cannot update attendance records."""
        user_id, token_key = self._create_regular_user(db_session)
        test_data = self._create_test_data(db_session, user_id)

        attendance = Attendance(
            raid_id=test_data["raid_id"],
            toon_id=test_data["toon_id"],
            is_present=True,
        )
        db_session.add(attendance)
        db_session.commit()

        headers = {"Authorization": f"Bearer {token_key}"}
        data = {"is_present": False}
        response = client.put(
            f"/attendance/{attendance.id}", json=data, headers=headers
        )
        assert response.status_code == 403

    def test_update_attendance_not_found(
        self, client: TestClient, db_session: Session
    ):
        """Test updating non-existent attendance record."""
        user_id, token_key = self._create_superuser(db_session)

        headers = {"Authorization": f"Bearer {token_key}"}
        data = {"is_present": False}
        response = client.put("/attendance/999", json=data, headers=headers)
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_update_attendance_bulk_superuser(
        self, client: TestClient, db_session: Session
    ):
        """Test bulk updating attendance records as superuser."""
        user_id, token_key = self._create_superuser(db_session)
        test_data = self._create_test_data(db_session, user_id)

        # Create second toon
        member2 = Member(
            guild_id=test_data["guild_id"],
            display_name="Test Member 2",
            team_id=test_data["team_id"],
        )
        db_session.add(member2)
        db_session.commit()

        toon2 = Toon(
            member_id=member2.id,
            username="TestToon2",
            class_="Priest",
            role="Healer",
        )
        db_session.add(toon2)
        db_session.commit()
        toon2_id = toon2.id  # Capture the ID immediately after commit

        # Create attendance records
        attendance1 = Attendance(
            raid_id=test_data["raid_id"],
            toon_id=test_data["toon_id"],
            is_present=True,
        )
        attendance2 = Attendance(
            raid_id=test_data["raid_id"], toon_id=toon2_id, is_present=True
        )
        db_session.add_all([attendance1, attendance2])
        db_session.commit()

        headers = {"Authorization": f"Bearer {token_key}"}
        data = {
            "attendance_records": [
                {
                    "id": attendance1.id,
                    "is_present": False,
                    "notes": "Updated notes 1",
                },
                {
                    "id": attendance2.id,
                    "is_present": False,
                    "notes": "Updated notes 2",
                },
            ]
        }
        response = client.put("/attendance/bulk", json=data, headers=headers)
        if response.status_code != 200:
            print(f"Response status: {response.status_code}")
            print(f"Response body: {response.text}")
        assert response.status_code == 200
        resp = response.json()
        assert len(resp) == 2
        assert resp[0]["is_present"] is False
        assert resp[0]["notes"] == "Updated notes 1"
        assert resp[1]["is_present"] is False
        assert resp[1]["notes"] == "Updated notes 2"

    def test_delete_attendance_superuser(
        self, client: TestClient, db_session: Session
    ):
        """Test deleting attendance record as superuser."""
        user_id, token_key = self._create_superuser(db_session)
        test_data = self._create_test_data(db_session, user_id)

        attendance = Attendance(
            raid_id=test_data["raid_id"],
            toon_id=test_data["toon_id"],
            is_present=True,
        )
        db_session.add(attendance)
        db_session.commit()
        attendance_id = attendance.id

        headers = {"Authorization": f"Bearer {token_key}"}
        response = client.delete(
            f"/attendance/{attendance_id}", headers=headers
        )
        assert response.status_code == 204

        # Verify it's deleted
        response = client.get(f"/attendance/{attendance_id}", headers=headers)
        assert response.status_code == 404

    def test_delete_attendance_regular_user_forbidden(
        self, client: TestClient, db_session: Session
    ):
        """Test that regular users cannot delete attendance records."""
        user_id, token_key = self._create_regular_user(db_session)
        test_data = self._create_test_data(db_session, user_id)

        attendance = Attendance(
            raid_id=test_data["raid_id"],
            toon_id=test_data["toon_id"],
            is_present=True,
        )
        db_session.add(attendance)
        db_session.commit()

        headers = {"Authorization": f"Bearer {token_key}"}
        response = client.delete(
            f"/attendance/{attendance.id}", headers=headers
        )
        assert response.status_code == 403

    def test_delete_attendance_not_found(
        self, client: TestClient, db_session: Session
    ):
        """Test deleting non-existent attendance record."""
        user_id, token_key = self._create_superuser(db_session)

        headers = {"Authorization": f"Bearer {token_key}"}
        response = client.delete("/attendance/999", headers=headers)
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_get_raid_attendance_stats(
        self, client: TestClient, db_session: Session
    ):
        """Test getting attendance statistics for a raid."""
        user_id, token_key = self._create_superuser(db_session)
        test_data = self._create_test_data(db_session, user_id)

        # Create second toon
        member2 = Member(
            guild_id=test_data["guild_id"],
            display_name="Test Member 2",
            team_id=test_data["team_id"],
        )
        db_session.add(member2)
        db_session.commit()

        toon2 = Toon(
            member_id=member2.id,
            username="TestToon2",
            class_="Priest",
            role="Healer",
        )
        db_session.add(toon2)
        db_session.commit()
        toon2_id = toon2.id  # Capture the ID immediately after commit

        # Create attendance records
        attendance1 = Attendance(
            raid_id=test_data["raid_id"],
            toon_id=test_data["toon_id"],
            is_present=True,
        )
        attendance2 = Attendance(
            raid_id=test_data["raid_id"], toon_id=toon2_id, is_present=False
        )
        db_session.add_all([attendance1, attendance2])
        db_session.commit()

        headers = {"Authorization": f"Bearer {token_key}"}
        response = client.get(
            f"/attendance/stats/raid/{test_data['raid_id']}", headers=headers
        )
        assert response.status_code == 200
        resp = response.json()
        assert resp["total_raids"] == 1
        assert resp["raids_attended"] == 1
        assert resp["raids_missed"] == 1
        assert resp["attendance_percentage"] == 50.0

    def test_get_toon_attendance_stats(
        self, client: TestClient, db_session: Session
    ):
        """Test getting attendance statistics for a toon."""
        user_id, token_key = self._create_superuser(db_session)
        test_data = self._create_test_data(db_session, user_id)

        # Create second raid
        raid2 = Raid(
            scheduled_at=datetime.now() + timedelta(days=2),
            scenario_id=test_data["scenario_id"],
            team_id=test_data["team_id"],
        )
        db_session.add(raid2)
        db_session.commit()

        # Create attendance records
        attendance1 = Attendance(
            raid_id=test_data["raid_id"],
            toon_id=test_data["toon_id"],
            is_present=True,
        )
        attendance2 = Attendance(
            raid_id=raid2.id, toon_id=test_data["toon_id"], is_present=True
        )
        db_session.add_all([attendance1, attendance2])
        db_session.commit()

        headers = {"Authorization": f"Bearer {token_key}"}
        response = client.get(
            f"/attendance/stats/toon/{test_data['toon_id']}", headers=headers
        )
        assert response.status_code == 200
        resp = response.json()
        assert resp["total_raids"] == 2
        assert resp["raids_attended"] == 2
        assert resp["raids_missed"] == 0
        assert resp["attendance_percentage"] == 100.0
        assert resp["current_streak"] == 2
        assert resp["longest_streak"] == 2

    def test_attendance_endpoints_require_authentication(
        self, client: TestClient, db_session: Session
    ):
        """Test that attendance endpoints require authentication."""
        # Test without authentication
        response = client.get("/attendance/")
        assert response.status_code == 401

        response = client.post("/attendance/", json={})
        assert response.status_code == 401

        response = client.put("/attendance/1", json={})
        assert response.status_code == 401

        response = client.delete("/attendance/1")
        assert response.status_code == 401
