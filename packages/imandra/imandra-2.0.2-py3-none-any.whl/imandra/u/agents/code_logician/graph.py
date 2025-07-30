import textwrap
from typing import Literal, Self

from langchain_core.runnables.config import RunnableConfig
from langgraph.graph.state import CompiledStateGraph
from langgraph.types import Command as LGCommand
from pydantic import BaseModel, Field, field_validator

from .base import FormalizationState
from .command import Command as UserCommand, UserStep


class EndResult(BaseModel):
    result: Literal["success", "failure", "abort"] = Field(
        description="Final result of agent calling"
    )
    info: str | None = Field(
        None, description="Additional information about the result"
    )


class GraphState(BaseModel):
    """
    Graph state of Code Logician
    """

    steps: list[UserStep] = Field([], description="Commands and their trajectories")
    step_i: int | None = Field(None, description="Index of the current step")
    info: dict = Field({}, description="Internal information shared between nodes")
    end_result: EndResult = Field(default=EndResult(result="success"))

    @property
    def last_fstate(self) -> FormalizationState | None:
        """Return the last formalization state"""
        last_fstate = None
        for step in self.steps:
            if step.last_fstate is not None:
                last_fstate = step.last_fstate
        return last_fstate

    @field_validator("steps", mode="after")
    @classmethod
    def last_fstate_cannot_be_later_than_the_first_pending_step(
        cls, steps: list[UserStep]
    ) -> list[UserStep]:
        # Find the first pending step
        step_i = next(
            (i for i, step in enumerate(steps) if step.meta.status == "pending"),
            None,
        )
        if step_i is None:
            return steps

        # Check is there any fstate after the first pending step
        for step in steps[step_i + 1 :]:
            if step.last_fstate is not None:
                raise ValueError(
                    "Last fstate cannot be later than the first pending step"
                )
        return steps

    def add_commands(self, commands: UserCommand | list[UserCommand]) -> Self:
        """Return a new GraphState with the added commands"""
        match commands:
            case UserCommand() as command:
                new_steps = [
                    *self.steps,
                    UserStep(command=command),
                ]
                return self.model_copy(update={"steps": new_steps})
            case list() as commands:
                new_steps = [
                    *self.steps,
                    *[UserStep(command=command) for command in commands],
                ]
                return self.model_copy(update={"steps": new_steps})
            case _:
                raise ValueError(f"Invalid command: {commands}")

    async def run(
        self,
        graph: CompiledStateGraph,
        config: dict | RunnableConfig | None = None,
        resume: LGCommand | None = None,
    ) -> tuple[Self, dict | None]:
        config = RunnableConfig(**(config or {}))
        inputs = resume or self
        async for chunk in graph.astream(
            inputs, config, stream_mode=["values", "updates"]
        ):
            chunk_type, chunk_value = chunk
            if chunk_type == "values":
                values = chunk_value
            elif chunk_type == "updates":
                updates = chunk_value
        gs = GraphState.model_validate(values)
        if "__interrupt__" in updates:
            return (gs, updates)
        else:
            return (gs, None)

    def __repr__(self):
        s = ""
        s += "Graph State:\n\n"
        s += f"{len(self.steps)} Steps\n\n"
        for i, step in enumerate(self.steps, 1):
            s += f"Step {i}:\n\n"
            s += textwrap.indent(step.__repr__(), "  ")
            s += "\n\n"
            s += "=" * 40 + "\n\n"

        return s
