from enum import StrEnum, auto

from pydantic import BaseModel, JsonValue


class FinalEnvironmentRequest(BaseModel):
    status: str


class StoreAgentStatePostRequest(BaseModel):
    agent_id: str
    step: str
    state: JsonValue
    trajectory_timestep: int


class StoreEnvironmentFrameRequest(BaseModel):
    agent_state_point_in_time: str
    current_agent_step: str
    state: JsonValue
    trajectory_timestep: int


class ExecutionStatus(StrEnum):
    QUEUED = auto()
    IN_PROGRESS = "in progress"
    FAIL = auto()
    SUCCESS = auto()
    CANCELLED = auto()

    def is_terminal_state(self) -> bool:
        return self in self.terminal_states()

    @classmethod
    def terminal_states(cls) -> set["ExecutionStatus"]:
        return {cls.SUCCESS, cls.FAIL, cls.CANCELLED}
