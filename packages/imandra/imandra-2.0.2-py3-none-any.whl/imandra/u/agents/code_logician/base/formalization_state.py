import textwrap
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class FormalizationStatus(str, Enum):
    UNKNOWN = "unknown"
    INADMISSIBLE = "inadmissible"
    ADMITTED_WITH_OPAQUENESS = "admitted_with_opaqueness"
    EXECUTABLE_WITH_APPROXIMATION = "executable_with_approximation"
    TRANSPARENT = "transparent"

    def __repr__(self) -> str:
        return self.value.capitalize()


class FormalizationState(BaseModel):
    status: FormalizationStatus = Field(
        description="The status of the formalization",
        default=FormalizationStatus.UNKNOWN,
    )
    src_code: str = Field(description="Source program")
    src_lang: str = Field(description="Source language")
    refactored_code: list[tuple[str, str]] = Field(
        [], description="Refactored code. A list of (step_name, refactored_code) pairs"
    )

    conversion_source_info: Any | None = Field(
        None,
        description=(
            "Context retrieved based on the source code. "
            "Includes conversion examples for the source language, "
            "relevant examples, IML API references, and missing functions."
        ),
    )
    conversion_failures_info: list[Any] = Field(
        [],
        description=(
            "Context retrieved based on conversion failures. "
            "Used for re-try conversion. Includes evaluation errors, "
            "similar error-suggestions pairs, and additional context."
        ),
    )

    iml_code: str | None = Field(None, description="IML code")
    iml_symbols: list[Any] = Field([], description="IML symbols in the IML code")
    opaques: list[Any] = Field([], description="Opaque functions in the IML code")
    eval_res: Any | None = Field(None, description="Evaluation result")

    vgs: list[Any] = Field([], description="Verification goals")
    region_decomps: list[Any] = Field([], description="Region decompositions")

    def pp(self) -> str:
        def truncate(s: str | None, n: int, indent: bool = True) -> str:
            if s is None:
                return textwrap.indent("None", "    " if indent else "")
            if len(s) <= n:
                return textwrap.indent(s, "    " if indent else "")
            else:
                return textwrap.indent(s[:n] + "..." + "\n", "    " if indent else "")

        s = ""
        s += f"Status: {self.status.name}\n"
        s += f"Src code: \n{truncate(self.src_code, 100)}\n"
        s += f"Refactored: {len(self.refactored_code) > 0}\n"
        s += f"IML code: \n{truncate(self.iml_code, 100)}\n"
        s += "IML symbols: \n"
        for i, sym in enumerate(self.iml_symbols, 1):
            s += f"    - {i}: {sym.__repr__()}\n"
        s += "Opaques: \n"
        for i, opa in enumerate(self.opaques, 1):
            s += f"    - {i}: {opa.__repr__()}\n"
        s += f"Eval res: {self.eval_res}\n"
        s += f"VGS: {self.vgs}\n"

        # Region decomps
        if not self.region_decomps:
            s += "Region decomps: []\n"
        else:
            s += f"Region decomps: ({len(self.region_decomps)})\n"
            for i, decomp in enumerate(self.region_decomps, 1):
                s += f"    - {i}.\n"
                s += textwrap.indent(decomp.__repr__(), "        ")
            s += "\n"

        # Context bytes
        source_info_data_len = (
            len(self.conversion_source_info.model_dump_json())
            if self.conversion_source_info is not None
            else 0
        )
        s += f"Source info data: {source_info_data_len} bytes\n"
        failures_info_data_len = sum(
            len(f.model_dump_json()) for f in self.conversion_failures_info
        )
        s += f"Failures info data: {failures_info_data_len} bytes\n"

        s = "Formalization State:\n" + textwrap.indent(s, "    ")
        return s

    class Config:
        arbitrary_types_allowed = True
