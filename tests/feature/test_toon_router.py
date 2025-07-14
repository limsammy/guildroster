# type: ignore[comparison-overlap,assignment,arg-type]
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime

from app.models.user import User
from app.models.guild import Guild
from app.models.team import Team
from app.models.member import Member
from app.models.toon import Toon
from app.models.token import Token
from app.utils.password import hash_password


class TestToonAPI:
    def _create_superuser(self, db_session: Session):
        user = User(
            username="superuser",
            hashed_password=hash_password("superpassword123"),
            is_active=True,
            is_superuser=True,
        )
        db_session.add(user)
        db_session.commit()
        user_id = user.id
        token = Token.create_user_token(user_id, "Superuser Token")
        db_session.add(token)
        db_session.commit()
        return user_id, token.key

    def _create_regular_user(self, db_session: Session):
        user = User(
            username="regularuser",
            hashed_password=hash_password("userpassword123"),
            is_active=True,
            is_superuser=False,
        )
        db_session.add(user)
        db_session.commit()
        user_id = user.id
        token = Token.create_user_token(user_id, "User Token")
        db_session.add(token)
        db_session.commit()
        return user_id, token.key

    def _create_guild(
        self, db_session: Session, user_id: int, name: str = "Test Guild"
    ):
        guild = Guild(name=name, created_by=user_id)
        db_session.add(guild)
        db_session.commit()
        return guild.id

    def _create_member(
        self,
        db_session: Session,
        guild_id: int,
        display_name: str = "Test Member",
    ):
        member = Member(guild_id=guild_id, display_name=display_name)
        db_session.add(member)
        db_session.commit()
        return member.id

    def test_create_toon_superuser(
        self, client: TestClient, db_session: Session
    ):
        user_id, token_key = self._create_superuser(db_session)
        guild_id = self._create_guild(db_session, user_id)
        member_id = self._create_member(db_session, guild_id)
        headers = {"Authorization": f"Bearer {token_key}"}
        data = {
            "username": "TestToon",
            "class": "Mage",
            "role": "DPS",
            "is_main": True,
            "member_id": member_id,
        }
        response = client.post("/toons/", json=data, headers=headers)
        assert response.status_code == 201
        resp = response.json()
        assert resp["username"] == "TestToon"
        assert resp["class"] == "Mage"
        assert resp["role"] == "DPS"
        assert resp["is_main"] is True
        assert resp["member_id"] == member_id

    def test_create_toon_regular_user_forbidden(
        self, client: TestClient, db_session: Session
    ):
        user_id, token_key = self._create_regular_user(db_session)
        guild_id = self._create_guild(db_session, user_id)
        member_id = self._create_member(db_session, guild_id)
        headers = {"Authorization": f"Bearer {token_key}"}
        data = {
            "username": "TestToon",
            "class": "Mage",
            "role": "DPS",
            "is_main": True,
            "member_id": member_id,
        }
        response = client.post("/toons/", json=data, headers=headers)
        assert response.status_code == 403

    def test_create_toon_duplicate_username(
        self, client: TestClient, db_session: Session
    ):
        user_id, token_key = self._create_superuser(db_session)
        guild_id = self._create_guild(db_session, user_id)
        member_id = self._create_member(db_session, guild_id)
        headers = {"Authorization": f"Bearer {token_key}"}
        data = {
            "username": "TestToon",
            "class": "Mage",
            "role": "DPS",
            "is_main": False,
            "member_id": member_id,
        }
        response1 = client.post("/toons/", json=data, headers=headers)
        assert response1.status_code == 201
        response2 = client.post("/toons/", json=data, headers=headers)
        assert response2.status_code == 400
        assert "already exists" in response2.json()["detail"]

    def test_create_toon_main_constraint(
        self, client: TestClient, db_session: Session
    ):
        user_id, token_key = self._create_superuser(db_session)
        guild_id = self._create_guild(db_session, user_id)
        member_id = self._create_member(db_session, guild_id)
        headers = {"Authorization": f"Bearer {token_key}"}
        data1 = {
            "username": "MainToon1",
            "class": "Mage",
            "role": "DPS",
            "is_main": True,
            "member_id": member_id,
        }
        data2 = {
            "username": "MainToon2",
            "class": "Priest",
            "role": "Healer",
            "is_main": True,
            "member_id": member_id,
        }
        response1 = client.post("/toons/", json=data1, headers=headers)
        assert response1.status_code == 201
        response2 = client.post("/toons/", json=data2, headers=headers)
        assert response2.status_code == 400
        assert "only one main toon" in response2.json()["detail"]

    def test_list_toons(self, client: TestClient, db_session: Session):
        user_id, token_key = self._create_superuser(db_session)
        guild_id = self._create_guild(db_session, user_id)
        member_id = self._create_member(db_session, guild_id)
        headers = {"Authorization": f"Bearer {token_key}"}
        toon1 = Toon(
            member_id=member_id, username="Toon1", class_="Mage", role="DPS"
        )
        toon2 = Toon(
            member_id=member_id,
            username="Toon2",
            class_="Priest",
            role="Healer",
        )
        db_session.add_all([toon1, toon2])
        db_session.commit()
        response = client.get("/toons/", headers=headers)
        assert response.status_code == 200
        toons = response.json()
        assert any(t["username"] == "Toon1" for t in toons)
        assert any(t["username"] == "Toon2" for t in toons)

    def test_list_toons_filter_by_member(
        self, client: TestClient, db_session: Session
    ):
        user_id, token_key = self._create_superuser(db_session)
        guild_id = self._create_guild(db_session, user_id)
        member1_id = self._create_member(
            db_session, guild_id, display_name="M1"
        )
        member2_id = self._create_member(
            db_session, guild_id, display_name="M2"
        )
        headers = {"Authorization": f"Bearer {token_key}"}
        toon1 = Toon(
            member_id=member1_id, username="Toon1", class_="Mage", role="DPS"
        )
        toon2 = Toon(
            member_id=member2_id,
            username="Toon2",
            class_="Priest",
            role="Healer",
        )
        db_session.add_all([toon1, toon2])
        db_session.commit()
        response = client.get(
            f"/toons/?member_id={member1_id}", headers=headers
        )
        assert response.status_code == 200
        toons = response.json()
        assert all(t["member_id"] == member1_id for t in toons)

    def test_get_toon_by_id(self, client: TestClient, db_session: Session):
        user_id, token_key = self._create_superuser(db_session)
        guild_id = self._create_guild(db_session, user_id)
        member_id = self._create_member(db_session, guild_id)
        toon = Toon(
            member_id=member_id, username="ToonGet", class_="Mage", role="DPS"
        )
        db_session.add(toon)
        db_session.commit()
        headers = {"Authorization": f"Bearer {token_key}"}
        response = client.get(f"/toons/{toon.id}", headers=headers)
        assert response.status_code == 200
        resp = response.json()
        assert resp["id"] == toon.id
        assert resp["username"] == "ToonGet"

    def test_get_toon_not_found(self, client: TestClient, db_session: Session):
        user_id, token_key = self._create_superuser(db_session)
        headers = {"Authorization": f"Bearer {token_key}"}
        response = client.get("/toons/99999", headers=headers)
        assert response.status_code == 404

    def test_get_toons_by_member(self, client: TestClient, db_session: Session):
        user_id, token_key = self._create_superuser(db_session)
        guild_id = self._create_guild(db_session, user_id)
        member_id = self._create_member(db_session, guild_id)
        toon1 = Toon(
            member_id=member_id, username="ToonA", class_="Mage", role="DPS"
        )
        toon2 = Toon(
            member_id=member_id,
            username="ToonB",
            class_="Priest",
            role="Healer",
        )
        db_session.add_all([toon1, toon2])
        db_session.commit()
        headers = {"Authorization": f"Bearer {token_key}"}
        response = client.get(f"/toons/member/{member_id}", headers=headers)
        assert response.status_code == 200
        toons = response.json()
        assert any(t["username"] == "ToonA" for t in toons)
        assert any(t["username"] == "ToonB" for t in toons)

    def test_update_toon_superuser(
        self, client: TestClient, db_session: Session
    ):
        user_id, token_key = self._create_superuser(db_session)
        guild_id = self._create_guild(db_session, user_id)
        member_id = self._create_member(db_session, guild_id)
        toon = Toon(
            member_id=member_id,
            username="ToonUpdate",
            class_="Mage",
            role="DPS",
        )
        db_session.add(toon)
        db_session.commit()
        headers = {"Authorization": f"Bearer {token_key}"}
        data = {"role": "Healer", "is_main": True}
        response = client.put(f"/toons/{toon.id}", json=data, headers=headers)
        assert response.status_code == 200
        resp = response.json()
        assert resp["role"] == "Healer"
        assert resp["is_main"] is True

    def test_update_toon_regular_user_forbidden(
        self, client: TestClient, db_session: Session
    ):
        user_id, token_key = self._create_superuser(db_session)
        reg_user_id, reg_token = self._create_regular_user(db_session)
        guild_id = self._create_guild(db_session, user_id)
        member_id = self._create_member(db_session, guild_id)
        toon = Toon(
            member_id=member_id,
            username="ToonUpdate",
            class_="Mage",
            role="DPS",
        )
        db_session.add(toon)
        db_session.commit()
        headers = {"Authorization": f"Bearer {reg_token}"}
        data = {"role": "Healer"}
        response = client.put(f"/toons/{toon.id}", json=data, headers=headers)
        assert response.status_code == 403

    def test_update_toon_duplicate_username(
        self, client: TestClient, db_session: Session
    ):
        user_id, token_key = self._create_superuser(db_session)
        guild_id = self._create_guild(db_session, user_id)
        member_id = self._create_member(db_session, guild_id)
        toon1 = Toon(
            member_id=member_id, username="Toon1", class_="Mage", role="DPS"
        )
        toon2 = Toon(
            member_id=member_id,
            username="Toon2",
            class_="Priest",
            role="Healer",
        )
        db_session.add_all([toon1, toon2])
        db_session.commit()
        headers = {"Authorization": f"Bearer {token_key}"}
        data = {"username": "Toon2"}
        response = client.put(f"/toons/{toon1.id}", json=data, headers=headers)
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]

    def test_update_toon_main_constraint(
        self, client: TestClient, db_session: Session
    ):
        user_id, token_key = self._create_superuser(db_session)
        guild_id = self._create_guild(db_session, user_id)
        member_id = self._create_member(db_session, guild_id)
        toon1 = Toon(
            member_id=member_id,
            username="Main1",
            class_="Mage",
            role="DPS",
            is_main=True,
        )
        toon2 = Toon(
            member_id=member_id,
            username="Alt1",
            class_="Priest",
            role="Healer",
            is_main=False,
        )
        db_session.add_all([toon1, toon2])
        db_session.commit()
        headers = {"Authorization": f"Bearer {token_key}"}
        data = {"is_main": True}
        response = client.put(f"/toons/{toon2.id}", json=data, headers=headers)
        assert response.status_code == 400
        assert "only one main toon" in response.json()["detail"]

    def test_delete_toon_superuser(
        self, client: TestClient, db_session: Session
    ):
        user_id, token_key = self._create_superuser(db_session)
        guild_id = self._create_guild(db_session, user_id)
        member_id = self._create_member(db_session, guild_id)
        toon = Toon(
            member_id=member_id,
            username="ToonDelete",
            class_="Mage",
            role="DPS",
        )
        db_session.add(toon)
        db_session.commit()
        headers = {"Authorization": f"Bearer {token_key}"}
        response = client.delete(f"/toons/{toon.id}", headers=headers)
        assert response.status_code == 204
        # Confirm deleted
        response = client.get(f"/toons/{toon.id}", headers=headers)
        assert response.status_code == 404

    def test_delete_toon_regular_user_forbidden(
        self, client: TestClient, db_session: Session
    ):
        user_id, token_key = self._create_superuser(db_session)
        reg_user_id, reg_token = self._create_regular_user(db_session)
        guild_id = self._create_guild(db_session, user_id)
        member_id = self._create_member(db_session, guild_id)
        toon = Toon(
            member_id=member_id,
            username="ToonDelete",
            class_="Mage",
            role="DPS",
        )
        db_session.add(toon)
        db_session.commit()
        headers = {"Authorization": f"Bearer {reg_token}"}
        response = client.delete(f"/toons/{toon.id}", headers=headers)
        assert response.status_code == 403
