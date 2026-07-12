"""Pydantic models for the calculator API."""

from pydantic import BaseModel, Field


class CalculateRequest(BaseModel):
    expression: str = Field(..., description="Mathematical expression to evaluate")


class CalculateResponse(BaseModel):
    result: float = Field(..., description="Result of the evaluation")
    expression: str = Field(..., description="Expression that was evaluated")


class FunctionInfo(BaseModel):
    name: str
    arity: int = Field(..., description="Number of arguments")
    description: str


class FunctionsResponse(BaseModel):
    functions: list[FunctionInfo]


class ConstantsResponse(BaseModel):
    constants: dict[str, float]


class HealthResponse(BaseModel):
    status: str = Field(..., description="Health status")
    service: str = Field(..., description="Service name")