from fastapi import APIRouter
from sse_starlette.sse import EventSourceResponse
from app.agent.graph import run_agent_stream, SCENARIO_CONFIGS
from app.database.connection import SessionLocal
from app.database.seed import seed_database

router = APIRouter()


@router.get("/api/scenarios")
def list_scenarios():
    """List all available scenarios with their descriptions."""
    scenarios = []
    for sid, config in SCENARIO_CONFIGS.items():
        scenarios.append({
            "id": config["id"],
            "name": config["name"],
            "description": config["description"],
            "type": config["type"],
            "product_id": config["product_id"],
            "node_id": config["node_id"],
            "icon": config.get("icon", ""),
            "color": config.get("color", "indigo")
        })
    return scenarios


@router.get("/api/scenarios/{scenario_id}")
def get_scenario(scenario_id: str):
    """Get detailed scenario configuration."""
    config = SCENARIO_CONFIGS.get(scenario_id)
    if not config:
        return {"error": f"Scenario {scenario_id} not found"}
    return config


@router.get("/api/scenarios/{scenario_id}/run")
async def run_scenario(scenario_id: str):
    """Run a scenario and stream agent reasoning steps via SSE."""
    return EventSourceResponse(run_agent_stream(scenario_id))


@router.post("/api/scenarios/{scenario_id}/reset")
def reset_scenario(scenario_id: str):
    """Reset all data back to the original seeded state."""
    db = SessionLocal()
    try:
        seed_database(db)
        return {"status": "reset", "message": "All data has been reset to initial state."}
    finally:
        db.close()
