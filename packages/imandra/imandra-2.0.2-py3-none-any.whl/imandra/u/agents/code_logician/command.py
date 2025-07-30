import textwrap
from datetime import UTC, datetime
from typing import Any, Literal, Self

from pydantic import BaseModel, Field, RootModel, model_validator

from .base import FormalizationState

# ----------------------
# Command
# ----------------------


class InitStateCommand(BaseModel, extra="forbid"):
    """
    Initialize the formalization state. Formalization status will be initialized to
    `UNKNOWN`.

    Updates `src_code`, `src_lang` in the formalization state.
    """

    type: Literal["init_state"] = "init_state"
    src_code: str = Field(description="Source program to formalize")
    src_lang: str = Field(description="Source language")


class GetStateElementCommand(BaseModel, extra="forbid"):
    """
    Get a state element from the formalization state.

    The following elements are supported:
    - `status`
    - `src_code`
    - `src_lang`
    - `refactored_code`
    - `conversion_source_info`
    - `conversion_failures_info`
    - `iml_code`
    - `iml_symbols`
    - `opaques`
    - `vgs`
    - `region_decomps`
    Will not change the formalization state.
    """

    type: Literal["get_state_element"] = "get_state_element"
    element_names: list[str] = Field(
        description="Name(s) of the state element(s) to get"
    )


class EditStateElementCommand(BaseModel, extra="forbid"):
    """
    Edit a state element in the formalization state.
    """

    type: Literal["edit_state_element"] = "edit_state_element"
    update: dict[str, Any] = Field(
        description=(
            "Updating dictionary to the formalization state, "
            "key-value pairs of field names and values"
        )
    )


class SearchFDBCommand(BaseModel, extra="forbid"):
    """
    Search the FDB for a table and query.
    """

    type: Literal["search_fdb"] = "search_fdb"
    name: Literal[
        "missing_functions",
        "iml_code_by_iml_code",
        "formalization_examples_by_src_lang",
        "formalization_examples_by_src_code",
        "iml_api_reference_by_pattern",
        "iml_api_reference_by_src_code",
        "error_suggestion_by_error_msg",
    ] = Field(description="Name of the table to search")
    query: str | tuple[str, str] | None = Field(
        description=(
            textwrap.dedent(
                """
                Query to search the table. 
                - Not required for `missing_functions`
                - For `formalization_examples_by_src_code`, the query is a tuple of 
                (source language, source code)
                - For `iml_api_reference_by_src_code`, the query is a tuple of 
                (source language, source code)
                - Otherwise, the query is a string
                """
            )
        )
    )
    top_k: int = Field(5, description="Number of results to return")


class CheckFormalizationCommand(BaseModel, extra="forbid"):
    """
    Check if the source code contains any functions that are hard to formalize in IML.
    If so, relevant context will be retrieved from the FDB to help the later
    formalization.

    Updates `conversion_source_info.missing_funcs` in the formalization state.
    """

    type: Literal["check_formalization"] = "check_formalization"


class GenProgramRefactorCommand(BaseModel, extra="forbid"):
    """
    Refactor the source code to make it easier to formalize in IML.

    Updates `refactored_code` in the formalization state.
    """

    type: Literal["gen_program_refactor"] = "gen_program_refactor"


class GenFormalizationDataCommand(BaseModel, extra="forbid"):
    """
    Based on the source code, retrieve relevant information from the FDB as context
    for formalization. Must be called before `gen_model`.

    Updates `conversion_source_info` in the formalization state.
    """

    type: Literal["gen_formalization_data"] = "gen_formalization_data"


class GenFormalizationFailureDataCommand(BaseModel, extra="forbid"):
    """
    Based on the formalization failure, retrieve relevant information from the FDB as
    context for re-try formalization.

    Retrieved information will be appended to `conversion_failures_info` in the
    formalization state.
    """

    type: Literal["gen_formalization_failure_data"] = "gen_formalization_failure_data"


class AdmitModelCommand(BaseModel, extra="forbid"):
    """
    Admit the current IML model and see if there's any error.

    Updates `eval_res` in the formalization state.
    """

    type: Literal["admit_model"] = "admit_model"


class GenModelCommand(BaseModel, extra="forbid"):
    """
    Generate IML code based on source program and retrieved context.

    Updates `iml_code`, `iml_symbols`, `opaques`, `eval_res`, `status` in the
    formalization state.
    """

    type: Literal["gen_model"] = "gen_model"


class SetModelCommand(BaseModel, extra="forbid"):
    """
    Set the IML model and admit it to see if there's any error.

    Updates `iml_code`, `iml_symbols`, `opaques`, `eval_res`, `status` in the
    formalization state.
    """

    type: Literal["set_model"] = "set_model"
    model: str = Field(description="new IML model to use")


class GenVgsCommand(BaseModel, extra="forbid"):
    """
    Generate verification goals on the source code and its corresponding IML model. Then
    use ImandraX to verify the VGs.

    Cannot be called when the formalization status is `UNKNOWN` or `INADMISSIBLE`.

    Updates `vgs` in the formalization state.
    """

    type: Literal["gen_vgs"] = "gen_vgs"
    description: str | None = Field(
        None,
        description=(
            "Description of the VGs to generate. If not provided, CodeLogician will "
            "seek verification goal requests from the comments in the source code."
        ),
    )


class GenRegionDecompsCommand(BaseModel, extra="forbid"):
    """
    Generate region decompositions.

    If `function_name` is provided, the region decompositions will be generated for the
    specific function. Otherwise, CodeLogician will seek region decomposition requests
    from the comments in the source code.

    Cannot be called when the formalization status is `UNKNOWN` or `INADMISSIBLE`.

    Updates `region_decomps` in the formalization state.

    After successful execution, you can either:
    - See the region decomposition results using `get_state_element` with
        `region_decomps`
    - Generate test cases for this specific region decomposition using `gen_test_cases`
    """

    type: Literal["gen_region_decomps"] = "gen_region_decomps"
    function_name: str | None = Field(
        None,
        description="Name of the function to decompose",
    )


class GenTestCasesCommand(BaseModel, extra="forbid"):
    """
    Use a specific region decomposition to generate test cases for a specific function
    in the source code.

    Updates `region_decomps[decomp_idx].test_cases` in the formalization state.
    """

    type: Literal["gen_test_cases"] = "gen_test_cases"
    decomp_idx: int = Field(
        description="Index of the region decomposition to generate test cases for"
    )


class SyncSourceCommand(BaseModel, extra="forbid"):
    """
    Use the most recent IML model and last pair of source code and IML code to
    update the source code.

    Updates `src_code` in the formalization state.
    """

    type: Literal["sync_source"] = "sync_source"


class SyncModelCommand(BaseModel, extra="forbid"):
    """
    Use the most recent IML model and last pair of source code and IML code to
    update the IML code.

    Updates `iml_code` in the formalization state.
    """

    type: Literal["sync_model"] = "sync_model"


class AgentFormalizerCommand(BaseModel, extra="forbid"):
    """
    Use the agentic workflow to formalize the source code. This is roughly equivalent to
    the following steps:
    1. check if the source code is within the scope of Imandra's capability
    (CheckFormalizationCommand)
    2. refactor the source code to make it easier to formalize in IML
    (GenProgramRefactorCommand)
    3. retrieve relevant information from the FDB based on the source code
    (GenFormalizationDataCommand)
    4. generate IML code based on the source code and retrieved context
    (GenModelCommand)
    5. admit the IML code and see if there's any error (AdmitModelCommand)
    6. If the IML code is not admissible, retrieve relevant information from the FDB
    based on the error message (GenFormalizationFailureDataCommand)
    7. repeat 4-6 until the IML code is admissible or the number of tries is exhausted

    Some steps can be skipped by setting the corresponding flags.

    Relevant fields in the formalization state:
    - `refactored_code`, `conversion_source_info`, `conversion_failures_info`?,
    `iml_code`, `eval_res`, `iml_symbols`, `opaques`, `status`
    """

    type: Literal["agent_formalizer"] = "agent_formalizer"
    no_check_formalization_hil: bool = Field(
        False,
        description="Whether to skip HIL in check_formalization",
    )
    no_refactor: bool = Field(
        False,
        description="Whether to skip refactoring",
    )
    no_gen_model_hil: bool = Field(
        False,
        description="Whether to skip HIL in gen_model",
    )
    max_tries_wo_hil: int = Field(
        2,
        description=(
            "Maximum number of tries for the formalizer agent without human-in-the-loop"
        ),
    )
    max_tries: int = Field(
        3,
        description="Maximum number of tries for the formalizer agent",
    )


class SuggestFormalizationActionCommand(BaseModel, extra="forbid"):
    """
    Upon a formalization failure, provide information by populating the `human_hint`
    field of the latest `conversion_failures_info` in the formalization state, which
    will be taken into account by the next formalization attempt (either GenModelCommand
    or AgentFormalizerCommand).
    """

    type: Literal["suggest_formalization_action"] = "suggest_formalization_action"
    feedback: str = Field(
        description="Feedback on the formalization failure",
    )


class SuggestAssumptionsCommand(BaseModel, extra="forbid"):
    """
    Suggest assumptions for a specific opaque function.

    Updates `opaques[i].assumptions` in the formalization state.
    """

    type: Literal["suggest_assumptions"] = "suggest_assumptions"
    feedback: str = Field()


class SuggestApproximationCommand(BaseModel, extra="forbid"):
    """
    Suggest an approximation for a specific opaque function.

    Updates `opaques[i].approximation` in the formalization state.
    """

    type: Literal["suggest_approximation"] = "suggest_approximation"
    feedback: str = Field()


class Command(RootModel):
    root: (
        InitStateCommand
        | GetStateElementCommand
        | EditStateElementCommand
        | SearchFDBCommand
        | CheckFormalizationCommand
        | GenProgramRefactorCommand
        | GenFormalizationDataCommand
        | GenFormalizationFailureDataCommand
        | AdmitModelCommand
        | GenModelCommand
        | SetModelCommand
        | GenVgsCommand
        | GenRegionDecompsCommand
        | GenTestCasesCommand
        | SyncSourceCommand
        | SyncModelCommand
        | AgentFormalizerCommand
        | SuggestFormalizationActionCommand
        | SuggestAssumptionsCommand
        | SuggestApproximationCommand
    ) = Field(discriminator="type")

    def __repr__(self):
        args = self.root.model_dump()
        args.pop("type")
        return textwrap.dedent(f"""\
                Command: 
                    Type: {self.root.type}
                    Args: {args}
            """)


# ----------------------
# Formalization Steps and Trajectory
# ----------------------


class FormalizationStep(BaseModel):
    """Represents a single step in the formalization process.

    Each step captures the action taken, the resulting state, and when it occurred.
    """

    action: str = Field(description="Name of the action")
    fstate: FormalizationState = Field(description="Formalization state")
    time: str = Field(
        default_factory=lambda: datetime.now(UTC).strftime("%y%m%d-%H%M%S"),
        description="The UTC timestamp of the formalization",
    )

    def __repr__(self):
        time = datetime.strptime(self.time, "%y%m%d-%H%M%S")
        s = ""
        s += f"Action: {self.action}\n"
        s += f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
        s += "F-state: \n"
        s += textwrap.indent(self.fstate.__repr__(), "  ")
        return s


class PrecheckFailure(BaseModel):
    """Represents a failure during pre-execution checks.

    Used to capture validation failures before executing a command.
    """

    field: str = Field(..., description="Field name")
    reason: str = Field(..., description="Reason for the error")
    message: str | None = Field(None, description="Message to the user")


class UserStepMeta(BaseModel):
    """Metadata about a user-initiated step in the formalization process.

    Tracks the status of the step and any pre-execution validation failures.
    """

    status: Literal[
        "precheck_failed",  # Fstate not satisfied for the command
        "pending",
        "done",
        "error",
        "hil_waiting",
        "hil_done",
    ] = Field("pending", description="Status of the command")
    precheck_failures: list[PrecheckFailure] = Field([])
    extra: dict = Field({}, description="Extra information about the status")

    @model_validator(mode="after")
    def validate_precheck_failures(self) -> Self:
        """Validate precheck failures"""
        if self.status == "precheck_failed" and len(self.precheck_failures) == 0:
            raise ValueError("Precheck failures cannot be empty")
        elif self.status != "precheck_failed" and len(self.precheck_failures) > 0:
            raise ValueError("Precheck failures cannot be non-empty")
        return self


class UserStep(BaseModel):
    """Represents a complete user-initiated step in the formalization process.

    Contains the command to execute, the trajectory of formalization states,
    and metadata about the step's execution.
    """

    command: Command = Field(description="User command")
    fstep_trajectory: list[FormalizationStep] = Field(
        [], description="Trajectory of formalization steps"
    )
    non_fstate_info: dict = Field({}, description="Non-formalization state information")
    meta: UserStepMeta = Field(
        UserStepMeta(status="pending"),
        description="Meta information about the user step",
    )
    hil_qas: list[list[Any]] = Field(
        [],
        description="Interrupt messages used for `interrupt`",
    )

    def extend_traj(self, action: str, fstate: FormalizationState) -> Self:
        """Extend the trajectory with a new formalization step"""
        return self.model_copy(
            update={
                "fstep_trajectory": [
                    *self.fstep_trajectory,
                    FormalizationStep(action=action, fstate=fstate),
                ],
            }
        )

    @property
    def last_fstate(self) -> FormalizationState | None:
        """Return the last formalization state, or None if there is no trajectory"""
        if len(self.fstep_trajectory) == 0:
            return None
        return self.fstep_trajectory[-1].fstate

    def __repr__(self):
        traj = self.fstep_trajectory
        s = ""
        s += f"{self.command.__repr__()}\n"
        if self.non_fstate_info:
            s += f"Non-F-state info: {', '.join(self.non_fstate_info.keys())}\n"

        traj_len = len(traj)
        if traj_len > 0:
            s += f"{traj_len} F-steps: \n\n"
        else:
            s += "No F-steps\n"

        steps_str = ""
        for i, step in enumerate(traj, 1):
            steps_str += f"F-step {i}:\n"
            steps_str += textwrap.indent(step.__repr__(), "  ")
            steps_str += "\n"
        if steps_str:
            s += textwrap.indent(steps_str, "  ")

        s += "\n"

        s += self.meta.__repr__()
        return s
