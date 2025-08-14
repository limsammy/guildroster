from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
from typing import Dict, List, Any, Optional
import json
import zipfile
import io
from datetime import datetime

from app.database import get_db
from app.utils.auth import require_superuser
from app.models.user import User
from app.models.guild import Guild
from app.models.team import Team
from app.models.toon import Toon
from app.models.raid import Raid
from app.models.scenario import Scenario
from app.schemas.guild import GuildCreate
from app.schemas.team import TeamCreate
from app.schemas.toon import ToonCreate
from app.schemas.raid import RaidCreate
from app.schemas.scenario import ScenarioCreate
from app.utils.logger import get_logger

logger = get_logger(__name__)
logger.info("Data import router loaded")

router = APIRouter(prefix="/data-import", tags=["Data Import"])


@router.post("/import", dependencies=[Depends(require_superuser)])
async def import_data(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superuser),
):
    """
    Import data from a ZIP file containing exported JSON data or a single JSON file.
    Only superusers can perform imports.
    """
    if not (file.filename.endswith(".zip") or file.filename.endswith(".json")):
        raise HTTPException(
            status_code=400, detail="File must be a ZIP or JSON file"
        )

    try:
        # Read the file content
        content = await file.read()

        # Parse the data based on file type
        if file.filename.endswith(".zip"):
            # Handle ZIP file
            data = {}
            with zipfile.ZipFile(io.BytesIO(content), "r") as zip_file:
                for file_info in zip_file.filelist:
                    if file_info.filename.endswith(".json"):
                        with zip_file.open(file_info.filename) as json_file:
                            json_content = json_file.read().decode("utf-8")
                            json_data = json.loads(json_content)

                            # Handle the new format with id and data fields
                            if "id" in json_data and "data" in json_data:
                                data[json_data["id"]] = json_data["data"]
                            else:
                                # Handle legacy format (direct data)
                                data[
                                    file_info.filename.replace(".json", "")
                                ] = json_data
        else:
            # Handle single JSON file
            try:
                json_data = json.loads(content.decode("utf-8"))

                # Handle the new format with multiple resources
                if isinstance(json_data, dict) and not (
                    "id" in json_data and "data" in json_data
                ):
                    # Multi-resource format
                    data = {}
                    for key, resource_data in json_data.items():
                        if (
                            isinstance(resource_data, dict)
                            and "id" in resource_data
                            and "data" in resource_data
                        ):
                            data[resource_data["id"]] = resource_data["data"]
                        else:
                            data[key] = resource_data
                else:
                    # Single resource format
                    if "id" in json_data and "data" in json_data:
                        data[json_data["id"]] = json_data["data"]
                    else:
                        data["unknown"] = json_data

            except json.JSONDecodeError:
                raise HTTPException(
                    status_code=400, detail="Invalid JSON format in file"
                )

        # Process the imported data
        import_results = await process_import_data(data, db, current_user)

        return {
            "message": "Import completed successfully",
            "results": import_results,
        }

    except Exception as e:
        logger.error(f"Import failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Import failed: {str(e)}")


async def process_import_data(
    data: Dict[str, Any], db: Session, current_user: User
) -> Dict[str, Any]:
    """
    Process imported data and insert it into the database.
    """
    results = {
        "guilds": {"imported": 0, "errors": []},
        "teams": {"imported": 0, "errors": []},
        "toons": {"imported": 0, "errors": []},
        "raids": {"imported": 0, "errors": []},
        "scenarios": {"imported": 0, "errors": []},
    }

    # Process guilds first (they're referenced by teams)
    if "guilds" in data:
        for guild_data in data["guilds"]:
            try:
                # Remove id if present (we'll generate a new one)
                if "id" in guild_data:
                    del guild_data["id"]

                # Check if guild already exists by name
                existing_guild = (
                    db.query(Guild)
                    .filter(Guild.name == guild_data["name"])
                    .first()
                )

                if existing_guild:
                    # Update existing guild
                    for key, value in guild_data.items():
                        # Skip read-only properties
                        if hasattr(existing_guild, key) and not key.endswith(
                            "_ids"
                        ):
                            setattr(existing_guild, key, value)
                    existing_guild.updated_at = datetime.now()
                    results["guilds"]["imported"] += 1
                else:
                    # Create new guild
                    guild_create = GuildCreate(**guild_data)
                    guild = Guild(
                        **guild_create.dict(), created_by=current_user.id
                    )
                    db.add(guild)
                    results["guilds"]["imported"] += 1
            except Exception as e:
                results["guilds"]["errors"].append(
                    f"Guild {guild_data.get('name', 'Unknown')}: {str(e)}"
                )

    # Commit guilds so we can reference them
    db.commit()

    # Process teams (they reference guilds)
    if "teams" in data:
        for team_data in data["teams"]:
            try:
                # Remove id if present
                if "id" in team_data:
                    del team_data["id"]

                # Handle guild reference - prefer guild_name over guild_id
                if "guild_name" in team_data:
                    guild = (
                        db.query(Guild)
                        .filter(Guild.name == team_data["guild_name"])
                        .first()
                    )
                    if guild:
                        team_data["guild_id"] = guild.id
                        # Remove guild_name since we now have guild_id
                        del team_data["guild_name"]
                    else:
                        results["teams"]["errors"].append(
                            f"Team {team_data.get('name', 'Unknown')}: Guild '{team_data['guild_name']}' not found"
                        )
                        continue
                elif "guild_id" in team_data:
                    # Check if the guild_id exists
                    guild = (
                        db.query(Guild)
                        .filter(Guild.id == team_data["guild_id"])
                        .first()
                    )
                    if not guild:
                        results["teams"]["errors"].append(
                            f"Team {team_data.get('name', 'Unknown')}: Guild with ID {team_data['guild_id']} not found"
                        )
                        continue
                else:
                    results["teams"]["errors"].append(
                        f"Team {team_data.get('name', 'Unknown')}: No guild reference provided (guild_id or guild_name required)"
                    )
                    continue

                # Check if team already exists by name and guild_id
                existing_team = (
                    db.query(Team)
                    .filter(
                        Team.name == team_data["name"],
                        Team.guild_id == team_data["guild_id"],
                    )
                    .first()
                )

                if existing_team:
                    # Update existing team
                    for key, value in team_data.items():
                        # Skip read-only properties and created_by
                        if (
                            hasattr(existing_team, key)
                            and key != "created_by"
                            and not key.endswith("_ids")
                        ):
                            setattr(existing_team, key, value)
                    existing_team.updated_at = datetime.now()
                    results["teams"]["imported"] += 1
                else:
                    # Create new team
                    team_create = TeamCreate(**team_data)
                    team = Team(
                        **team_create.dict(), created_by=current_user.id
                    )
                    db.add(team)
                    results["teams"]["imported"] += 1
            except Exception as e:
                results["teams"]["errors"].append(
                    f"Team {team_data.get('name', 'Unknown')}: {str(e)}"
                )

    # Commit teams so we can reference them
    db.commit()

    # Process scenarios
    if "scenarios" in data:
        for scenario_data in data["scenarios"]:
            try:
                if "id" in scenario_data:
                    del scenario_data["id"]

                # Check if scenario already exists by name
                existing_scenario = (
                    db.query(Scenario)
                    .filter(Scenario.name == scenario_data["name"])
                    .first()
                )

                if existing_scenario:
                    # Update existing scenario
                    for key, value in scenario_data.items():
                        # Skip read-only properties
                        if hasattr(existing_scenario, key) and not key.endswith(
                            "_ids"
                        ):
                            setattr(existing_scenario, key, value)
                    existing_scenario.updated_at = datetime.now()
                    results["scenarios"]["imported"] += 1
                else:
                    # Create new scenario
                    scenario_create = ScenarioCreate(**scenario_data)
                    scenario = Scenario(**scenario_create.dict())
                    db.add(scenario)
                    results["scenarios"]["imported"] += 1
            except Exception as e:
                results["scenarios"]["errors"].append(
                    f"Scenario {scenario_data.get('name', 'Unknown')}: {str(e)}"
                )

    # Process toons (they reference teams)
    if "toons" in data:
        for toon_data in data["toons"]:
            try:
                if "id" in toon_data:
                    del toon_data["id"]

                # Handle team reference - prefer team_name over team_id
                if "team_name" in toon_data:
                    team = (
                        db.query(Team)
                        .filter(Team.name == toon_data["team_name"])
                        .first()
                    )
                    if team:
                        toon_data["team_id"] = team.id
                        # Remove team_name since we now have team_id
                        del toon_data["team_name"]
                    else:
                        results["toons"]["errors"].append(
                            f"Toon {toon_data.get('name', 'Unknown')}: Team '{toon_data['team_name']}' not found"
                        )
                        continue
                elif "team_id" in toon_data:
                    # Check if the team_id exists
                    team = (
                        db.query(Team)
                        .filter(Team.id == toon_data["team_id"])
                        .first()
                    )
                    if not team:
                        results["toons"]["errors"].append(
                            f"Toon {toon_data.get('name', 'Unknown')}: Team with ID {toon_data['team_id']} not found"
                        )
                        continue
                else:
                    results["toons"]["errors"].append(
                        f"Toon {toon_data.get('name', 'Unknown')}: No team reference provided (team_id or team_name required)"
                    )
                    continue

                # Check if toon already exists by username
                existing_toon = (
                    db.query(Toon)
                    .filter(Toon.username == toon_data["username"])
                    .first()
                )

                if existing_toon:
                    # Update existing toon
                    for key, value in toon_data.items():
                        # Skip read-only properties like team_ids
                        if hasattr(existing_toon, key) and not key.endswith(
                            "_ids"
                        ):
                            setattr(existing_toon, key, value)
                    existing_toon.updated_at = datetime.now()
                    results["toons"]["imported"] += 1
                else:
                    # Create new toon
                    toon_create = ToonCreate(**toon_data)
                    toon = Toon(**toon_create.dict())
                    db.add(toon)
                    results["toons"]["imported"] += 1
            except Exception as e:
                results["toons"]["errors"].append(
                    f"Toon {toon_data.get('name', 'Unknown')}: {str(e)}"
                )

    # Process raids (they reference teams)
    if "raids" in data:
        for raid_data in data["raids"]:
            try:
                if "id" in raid_data:
                    del raid_data["id"]

                # Handle team reference - prefer team_name over team_id
                if "team_name" in raid_data:
                    team = (
                        db.query(Team)
                        .filter(Team.name == raid_data["team_name"])
                        .first()
                    )
                    if team:
                        raid_data["team_id"] = team.id
                        # Remove team_name since we now have team_id
                        del raid_data["team_name"]
                    else:
                        results["raids"]["errors"].append(
                            f"Raid {raid_data.get('scheduled_at', 'Unknown')}: Team '{raid_data['team_name']}' not found"
                        )
                        continue
                elif "team_id" in raid_data:
                    # Check if the team_id exists
                    team = (
                        db.query(Team)
                        .filter(Team.id == raid_data["team_id"])
                        .first()
                    )
                    if not team:
                        results["raids"]["errors"].append(
                            f"Raid {raid_data.get('scheduled_at', 'Unknown')}: Team with ID {raid_data['team_id']} not found"
                        )
                        continue
                else:
                    results["raids"]["errors"].append(
                        f"Raid {raid_data.get('scheduled_at', 'Unknown')}: No team reference provided (team_id or team_name required)"
                    )
                    continue

                # Check if raid already exists by team_id and scheduled_at
                existing_raid = (
                    db.query(Raid)
                    .filter(
                        Raid.team_id == raid_data["team_id"],
                        Raid.scheduled_at == raid_data["scheduled_at"],
                    )
                    .first()
                )

                if existing_raid:
                    # Update existing raid
                    for key, value in raid_data.items():
                        # Skip read-only properties
                        if hasattr(existing_raid, key) and not key.endswith(
                            "_ids"
                        ):
                            setattr(existing_raid, key, value)
                    existing_raid.updated_at = datetime.now()
                    results["raids"]["imported"] += 1
                else:
                    # Create new raid
                    raid_create = RaidCreate(**raid_data)
                    raid = Raid(**raid_create.dict())
                    db.add(raid)
                    results["raids"]["imported"] += 1
            except Exception as e:
                results["raids"]["errors"].append(
                    f"Raid {raid_data.get('scheduled_at', 'Unknown')}: {str(e)}"
                )

    # Final commit
    db.commit()

    return results


@router.get("/export-status")
def get_export_status():
    """
    Get the status of import/export functionality.
    """
    return {
        "import_enabled": True,
        "export_enabled": True,
        "supported_formats": ["zip", "json"],
        "supported_data_types": [
            "guilds",
            "teams",
            "toons",
            "raids",
            "scenarios",
        ],
    }


@router.get("/export", dependencies=[Depends(require_superuser)])
async def export_data(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superuser),
):
    """
    Export all data as JSON with names instead of IDs for seamless import.
    Only superusers can perform exports.
    """
    try:
        export_data = {}

        # Export guilds
        guilds = db.query(Guild).all()
        export_data["guilds"] = {
            "id": "guilds",
            "exported_at": datetime.now().isoformat() + "Z",
            "data": [
                {
                    "name": guild.name,
                    "id": guild.id,
                    "created_by": guild.created_by,
                    "created_at": (
                        guild.created_at.isoformat()
                        if guild.created_at
                        else None
                    ),
                    "updated_at": (
                        guild.updated_at.isoformat()
                        if guild.updated_at
                        else None
                    ),
                }
                for guild in guilds
            ],
        }

        # Export teams with guild names
        teams = db.query(Team).all()
        export_data["teams"] = {
            "id": "teams",
            "exported_at": datetime.now().isoformat() + "Z",
            "data": [
                {
                    "name": team.name,
                    "description": team.description,
                    "guild_name": team.guild.name if team.guild else None,
                    "id": team.id,
                    "created_by": team.created_by,
                    "is_active": team.is_active,
                    "created_at": (
                        team.created_at.isoformat() if team.created_at else None
                    ),
                    "updated_at": (
                        team.updated_at.isoformat() if team.updated_at else None
                    ),
                }
                for team in teams
            ],
        }

        # Export toons with team names
        toons = db.query(Toon).all()
        export_data["toons"] = {
            "id": "toons",
            "exported_at": datetime.now().isoformat() + "Z",
            "data": [
                {
                    "id": toon.id,
                    "username": toon.username,
                    "class": toon.class_,
                    "role": toon.role,
                    "team_name": toon.teams[0].name if toon.teams else None,
                    "created_at": (
                        toon.created_at.isoformat() if toon.created_at else None
                    ),
                    "updated_at": (
                        toon.updated_at.isoformat() if toon.updated_at else None
                    ),
                }
                for toon in toons
            ],
        }

        # Export raids with team names
        raids = db.query(Raid).all()
        export_data["raids"] = {
            "id": "raids",
            "exported_at": datetime.now().isoformat() + "Z",
            "data": [
                {
                    "id": raid.id,
                    "team_name": raid.team.name if raid.team else None,
                    "scheduled_at": (
                        raid.scheduled_at.isoformat()
                        if raid.scheduled_at
                        else None
                    ),
                    "created_at": (
                        raid.created_at.isoformat() if raid.created_at else None
                    ),
                    "updated_at": (
                        raid.updated_at.isoformat() if raid.updated_at else None
                    ),
                }
                for raid in raids
            ],
        }

        # Export scenarios
        scenarios = db.query(Scenario).all()
        export_data["scenarios"] = {
            "id": "scenarios",
            "exported_at": datetime.now().isoformat() + "Z",
            "data": [
                {
                    "name": scenario.name,
                    "is_active": scenario.is_active,
                    "mop": scenario.mop,
                    "id": scenario.id,
                    "created_at": (
                        scenario.created_at.isoformat()
                        if scenario.created_at
                        else None
                    ),
                    "updated_at": (
                        scenario.updated_at.isoformat()
                        if scenario.updated_at
                        else None
                    ),
                }
                for scenario in scenarios
            ],
        }

        return export_data

    except Exception as e:
        logger.error(f"Export failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")
