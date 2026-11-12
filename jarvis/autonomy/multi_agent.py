"""
Capability 103: Multi-Agent Orchestration
Coordinates multi-agent collaboration, role assignments, inter-agent messaging,
subtask delegation, consensus voting, and result aggregation.
"""
from __future__ import annotations

import collections
import enum
import time
import uuid
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any, Optional, Set


class AgentRole(str, enum.Enum):
    COORDINATOR = "coordinator"
    RESEARCHER = "researcher"
    ARCHITECT = "architect"
    CODER = "coder"
    TESTER = "tester"
    SECURITY = "security"
    VERIFIER = "verifier"
    DOCUMENTER = "documenter"


class AgentState(str, enum.Enum):
    IDLE = "idle"
    WORKING = "working"
    WAITING = "waiting"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class AgentMessage:
    """Inter-agent communication message."""
    msg_id: str
    sender: str
    recipient: str  # "@all" or specific agent name e.g. "@coder"
    content: str
    msg_type: str = "STATUS"  # TASK_ASSIGN, STATUS, RESULT, VOTE, HANDOFF, QUERY
    payload: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class AgentWorker:
    """Represents a virtual specialized agent within the orchestrator swarm."""
    agent_id: str
    name: str
    role: AgentRole
    capabilities: List[str] = field(default_factory=list)
    state: AgentState = AgentState.IDLE
    assigned_task_id: Optional[str] = None
    inbox: List[AgentMessage] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["role"] = self.role.value if isinstance(self.role, AgentRole) else str(self.role)
        d["state"] = self.state.value if isinstance(self.state, AgentState) else str(self.state)
        d["inbox"] = [m.to_dict() for m in self.inbox]
        return d


class MultiAgentOrchestrator:
    """
    Capability 103: Multi-Agent Swarm Orchestrator.
    Manages team roster, message dispatching, collaborative workflows,
    and consensus resolution across specialized agents.
    """

    def __init__(self):
        self.agents: Dict[str, AgentWorker] = {}
        self.message_board: List[AgentMessage] = []
        self._seq = 0

    def register_agent(self, agent: AgentWorker) -> None:
        """Enrolls an agent into the swarm roster."""
        self.agents[agent.name] = agent

    def get_agent(self, name: str) -> Optional[AgentWorker]:
        """Retrieves an agent by name (with or without leading @)."""
        clean_name = name.lstrip("@")
        return self.agents.get(clean_name)

    def get_roster(self) -> List[Dict[str, Any]]:
        """Returns snapshot of current swarm roster."""
        return [a.to_dict() for a in self.agents.values()]

    def find_best_agent(self, capability: str, role_hint: Optional[AgentRole] = None) -> Optional[AgentWorker]:
        """Finds an available agent capable of executing the requested work."""
        candidates = []
        for a in self.agents.values():
            if capability in a.capabilities or not a.capabilities:
                if role_hint is None or a.role == role_hint:
                    score = 0
                    if a.state == AgentState.IDLE:
                        score += 10
                    if capability in a.capabilities:
                        score += 5
                    candidates.append((score, a))

        if candidates:
            candidates.sort(key=lambda x: x[0], reverse=True)
            return candidates[0][1]
        return None

    def post_message(self, sender: str, recipient: str, content: str,
                     msg_type: str = "STATUS", payload: Optional[Dict[str, Any]] = None) -> AgentMessage:
        """Posts a message to the shared board and routes it to recipients' inboxes."""
        self._seq += 1
        msg = AgentMessage(
            msg_id=f"msg_{self._seq}",
            sender=sender.lstrip("@"),
            recipient=recipient,
            content=content,
            msg_type=msg_type,
            payload=payload or {}
        )
        self.message_board.append(msg)

        # Route message
        recip_clean = recipient.lstrip("@")
        if recip_clean == "all":
            for a in self.agents.values():
                if a.name != msg.sender:
                    a.inbox.append(msg)
        elif recip_clean in self.agents:
            self.agents[recip_clean].inbox.append(msg)

        return msg

    def read_inbox(self, agent_name: str, clear: bool = True) -> List[AgentMessage]:
        """Reads and optionally clears incoming messages for an agent."""
        agent = self.get_agent(agent_name)
        if not agent:
            return []
        msgs = list(agent.inbox)
        if clear:
            agent.inbox.clear()
        return msgs

    def assign_task(self, agent_name: str, task_id: str, task_description: str) -> bool:
        """Assigns a discrete task to an agent."""
        agent = self.get_agent(agent_name)
        if not agent:
            return False
        agent.assigned_task_id = task_id
        agent.state = AgentState.WORKING
        self.post_message(
            sender="coordinator",
            recipient=f"@{agent.name}",
            content=f"Assigned task {task_id}: {task_description}",
            msg_type="TASK_ASSIGN",
            payload={"task_id": task_id, "description": task_description}
        )
        return True

    def handoff(self, from_agent: str, to_agent: str, task_id: str, artifact: Any) -> AgentMessage:
        """Executes a structured task handoff between two agents."""
        f_agent = self.get_agent(from_agent)
        if f_agent and f_agent.assigned_task_id == task_id:
            f_agent.state = AgentState.IDLE
            f_agent.assigned_task_id = None

        t_agent = self.get_agent(to_agent)
        if t_agent:
            t_agent.state = AgentState.WORKING
            t_agent.assigned_task_id = task_id

        return self.post_message(
            sender=from_agent,
            recipient=f"@{to_agent.lstrip('@')}",
            content=f"Handoff task {task_id} with completed artifacts.",
            msg_type="HANDOFF",
            payload={"task_id": task_id, "artifact": artifact}
        )

    def conduct_voting(self, topic: str, options: List[str], voters: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Conducts a consensus poll among agents.
        Returns voting tally, winner, and agreement percentage.
        """
        voter_names = voters if voters is not None else list(self.agents.keys())
        if not voter_names or not options:
            return {"topic": topic, "winner": None, "tally": {}, "consensus_ratio": 0.0}

        tally: Dict[str, int] = {opt: 0 for opt in options}
        votes: Dict[str, str] = {}

        for vname in voter_names:
            agent = self.get_agent(vname)
            # Deterministic voting heuristic based on agent role preferences
            chosen_opt = options[0]
            if agent:
                if agent.role == AgentRole.SECURITY and any("safe" in o.lower() or "audit" in o.lower() for o in options):
                    chosen_opt = next(o for o in options if "safe" in o.lower() or "audit" in o.lower())
                elif agent.role == AgentRole.TESTER and any("test" in o.lower() or "verify" in o.lower() for o in options):
                    chosen_opt = next(o for o in options if "test" in o.lower() or "verify" in o.lower())
                else:
                    # Choose option deterministically based on agent name hash
                    chosen_opt = options[hash(vname) % len(options)]

            votes[vname] = chosen_opt
            tally[chosen_opt] = tally.get(chosen_opt, 0) + 1
            self.post_message(
                sender=vname,
                recipient="@coordinator",
                content=f"Vote for topic '{topic}': {chosen_opt}",
                msg_type="VOTE",
                payload={"topic": topic, "choice": chosen_opt}
            )

        winner = max(tally.keys(), key=lambda k: tally[k])
        ratio = tally[winner] / len(voter_names) if voter_names else 0.0

        return {
            "topic": topic,
            "winner": winner,
            "tally": tally,
            "votes": votes,
            "total_voters": len(voter_names),
            "consensus_ratio": round(ratio, 2)
        }

    def aggregate_results(self, subtask_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Combines outputs from multiple subtasks into a unified synthesis.
        """
        aggregated = {
            "timestamp": time.time(),
            "total_subtasks": len(subtask_results),
            "successful_subtasks": 0,
            "failed_subtasks": 0,
            "combined_artifacts": {},
            "errors": []
        }

        for st_id, res in subtask_results.items():
            if isinstance(res, dict) and res.get("status") == "failed":
                aggregated["failed_subtasks"] += 1
                aggregated["errors"].append({"subtask_id": st_id, "error": res.get("error", "Unknown")})
            else:
                aggregated["successful_subtasks"] += 1
                aggregated["combined_artifacts"][st_id] = res

        aggregated["success_rate"] = (
            aggregated["successful_subtasks"] / len(subtask_results)
            if subtask_results else 0.0
        )
        return aggregated
