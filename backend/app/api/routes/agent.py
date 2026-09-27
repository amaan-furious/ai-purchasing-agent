from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.database.models import AgentDecision
from sse_starlette.sse import EventSourceResponse
from app.agent.graph import run_agent_stream

router = APIRouter()


@router.post("/api/agent/run")
async def run_agent_route(config: dict = None):
    """Run the agent with a custom config. Returns SSE stream."""
    scenario_id = config.get("scenario_id", "1") if config else "1"
    return EventSourceResponse(run_agent_stream(scenario_id))


@router.get("/api/agent/decisions")
def list_decisions(db: Session = Depends(get_db)):
    """List all past agent decisions."""
    decisions = db.query(AgentDecision).order_by(AgentDecision.created_at.desc()).all()
    result = []
    for d in decisions:
        result.append({
            "id": d.id,
            "scenario_type": d.scenario_type,
            "decision_type": d.decision_type,
            "original_recommendation": d.original_recommendation,
            "final_decision": d.final_decision,
            "validation_results": d.validation_results,
            "execution_result": d.execution_result,
            "status": d.status,
            "created_at": d.created_at.isoformat() if d.created_at else None
        })
    return result


@router.get("/api/agent/decisions/{decision_id}")
def get_decision(decision_id: int, db: Session = Depends(get_db)):
    """Get a specific agent decision with full details."""
    d = db.query(AgentDecision).filter(AgentDecision.id == decision_id).first()
    if not d:
        return {"error": "Decision not found"}
    return {
        "id": d.id,
        "scenario_type": d.scenario_type,
        "decision_type": d.decision_type,
        "original_recommendation": d.original_recommendation,
        "agent_analysis": d.agent_analysis,
        "final_decision": d.final_decision,
        "validation_results": d.validation_results,
        "execution_result": d.execution_result,
        "feedback_loop_log": d.feedback_loop_log,
        "status": d.status,
        "created_at": d.created_at.isoformat() if d.created_at else None
    }
