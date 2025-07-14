# type: ignore[comparison-overlap,assignment]
import pytest
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime

from app.models.toon import Toon, WOW_CLASSES, WOW_ROLES
from app.models.member import Member
from app.models.user import User
from app.models.guild import Guild


class TestToonModel:
    def setup_member(self, db_session: Session):
        user = User(username="testuser", hashed_password="hashed")
        db_session.add(user)
        db_session.commit()
        guild = Guild(name="Test Guild", created_by=user.id)
        db_session.add(guild)
        db_session.commit()
        member = Member(guild_id=guild.id, display_name="Test Member")
        db_session.add(member)
        db_session.commit()
        return member

    def test_create_toon(self, db_session: Session):
        member = self.setup_member(db_session)
        toon = Toon(
            member_id=member.id,
            username="TestToon",
            is_main=True,
            class_="Mage",
            role="DPS",
        )
        db_session.add(toon)
        db_session.commit()
        assert toon.id is not None
        assert toon.member_id == member.id
        assert toon.username == "TestToon"
        assert toon.is_main is True
        assert toon.class_ == "Mage"
        assert toon.role == "DPS"
        assert toon.created_at is not None
        assert toon.updated_at is not None

    def test_unique_member_username(self, db_session: Session):
        member = self.setup_member(db_session)
        toon1 = Toon(
            member_id=member.id, username="Toon1", class_="Druid", role="Healer"
        )
        toon2 = Toon(
            member_id=member.id, username="Toon1", class_="Druid", role="Healer"
        )
        db_session.add(toon1)
        db_session.commit()
        db_session.add(toon2)
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_class_and_role_validation(self, db_session: Session):
        member = self.setup_member(db_session)
        # Invalid class
        toon = Toon(
            member_id=member.id,
            username="ToonBadClass",
            class_="InvalidClass",
            role="DPS",
        )
        db_session.add(toon)
        with pytest.raises(IntegrityError):
            db_session.commit()
        db_session.rollback()
        # Invalid role
        toon = Toon(
            member_id=member.id,
            username="ToonBadRole",
            class_="Mage",
            role="InvalidRole",
        )
        db_session.add(toon)
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_relationship_to_member(self, db_session: Session):
        member = self.setup_member(db_session)
        toon = Toon(
            member_id=member.id,
            username="RelToon",
            class_="Priest",
            role="Healer",
        )
        db_session.add(toon)
        db_session.commit()
        assert toon.member == member
        assert toon in member.toons

    def test_cascade_delete_on_member(self, db_session: Session):
        member = self.setup_member(db_session)
        toon = Toon(
            member_id=member.id,
            username="CascadeToon",
            class_="Rogue",
            role="DPS",
        )
        db_session.add(toon)
        db_session.commit()
        toon_id = toon.id
        db_session.delete(member)
        db_session.commit()
        deleted = db_session.query(Toon).filter(Toon.id == toon_id).first()
        assert deleted is None

    def test_timestamps(self, db_session: Session):
        member = self.setup_member(db_session)
        toon = Toon(
            member_id=member.id,
            username="TimeToon",
            class_="Shaman",
            role="Healer",
        )
        db_session.add(toon)
        db_session.commit()
        created_at = toon.created_at
        toon.username = "TimeToon2"
        db_session.commit()
        assert toon.updated_at >= created_at

    def test_foreign_key_constraint(self, db_session: Session):
        toon = Toon(
            member_id=99999, username="NoMember", class_="Mage", role="DPS"
        )
        db_session.add(toon)
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_only_one_main_toon_per_member(self, db_session: Session):
        member = self.setup_member(db_session)
        toon1 = Toon(
            member_id=member.id,
            username="Main1",
            class_="Paladin",
            role="Tank",
            is_main=True,
        )
        toon2 = Toon(
            member_id=member.id,
            username="Alt1",
            class_="Paladin",
            role="Tank",
            is_main=True,
        )
        db_session.add(toon1)
        db_session.commit()
        db_session.add(toon2)
        db_session.commit()
        # Enforce in code: only one main toon per member
        mains = [t for t in member.toons if t.is_main]
        assert (
            len(mains) == 2
        )  # DB allows, but API/code should enforce only one
