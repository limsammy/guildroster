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
logger.info("Import/Export router loaded")

router = APIRouter(prefix="/import-export", tags=["Import/Export"])


@router.post("/import", dependencies=[Depends(require_superuser)])
async def import_data(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superuser),
):
    """
    Import data from a ZIP file containing exported JSON data.
    Only superusers can perform imports.
    """
    if not file.filename.endswith(".zip"):
        raise HTTPException(status_code=400, detail="File must be a ZIP file")

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
        import_results = await process_import_data(data, db)

        return {
            "message": "Import completed successfully",
            "results": import_results,
        }

    except Exception as e:
        logger.error(f"Import failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Import failed: {str(e)}")


async def process_import_data(
    data: Dict[str, Any], db: Session
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

                guild_create = GuildCreate(**guild_data)
                guild = Guild(**guild_create.dict())
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

                # Find the guild by name if guild_id is not available
                if "guild_id" not in team_data and "guild_name" in team_data:
                    guild = (
                        db.query(Guild)
                        .filter(Guild.name == team_data["guild_name"])
                        .first()
                    )
                    if guild:
                        team_data["guild_id"] = guild.id
                    else:
                        results["teams"]["errors"].append(
                            f"Team {team_data.get('name', 'Unknown')}: Guild not found"
                        )
                        continue

                team_create = TeamCreate(**team_data)
                team = Team(**team_create.dict())
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

                # Find the team by name if team_id is not available
                if "team_id" not in toon_data and "team_name" in toon_data:
                    team = (
                        db.query(Team)
                        .filter(Team.name == toon_data["team_name"])
                        .first()
                    )
                    if team:
                        toon_data["team_id"] = team.id
                    else:
                        results["toons"]["errors"].append(
                            f"Toon {toon_data.get('name', 'Unknown')}: Team not found"
                        )
                        continue

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

                # Find the team by name if team_id is not available
                if "team_id" not in raid_data and "team_name" in raid_data:
                    team = (
                        db.query(Team)
                        .filter(Team.name == raid_data["team_name"])
                        .first()
                    )
                    if team:
                        raid_data["team_id"] = team.id
                    else:
                        results["raids"]["errors"].append(
                            f"Raid {raid_data.get('scheduled_at', 'Unknown')}: Team not found"
                        )
                        continue

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
        "supported_formats": ["zip"],
        "supported_data_types": [
            "guilds",
            "teams",
            "toons",
            "raids",
            "scenarios",
        ],
    }
