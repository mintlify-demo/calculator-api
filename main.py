"""Calculator API: add, subtract, multiply and divide over HTTP.

It also tells a small versioning story:
  * v1  - one endpoint per operation, two numbers in (a, b), one number out.
  * v2  - a single /v2/calculate endpoint that takes an operation name and
          two or more operands.

Run it:  uvicorn main:app --reload
"""
from enum import Enum

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# --------------------------------------------------------------------------- #
# The math (plain functions, no web code)
# --------------------------------------------------------------------------- #


def add(a: float, b: float) -> float:
    return a + b


def subtract(a: float, b: float) -> float:
    return a - b


def multiply(a: float, b: float) -> float:
    return a * b


def divide(a: float, b: float) -> float:
    if b == 0:
        # We turn this into an HTTP 400 in the endpoint (see `safe_divide`).
        raise ZeroDivisionError("Cannot divide by zero")
    return a / b


def safe_divide(a: float, b: float) -> float:
    """Divide, but raise an HTTP 400 instead of crashing when b is zero."""
    try:
        return divide(a, b)
    except ZeroDivisionError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


# --------------------------------------------------------------------------- #
# Request / response models
# --------------------------------------------------------------------------- #


class Operands(BaseModel):
    """Two numbers to combine (v1)."""

    a: float = Field(..., description="The first number.", examples=[12])
    b: float = Field(..., description="The second number.", examples=[4])


class Result(BaseModel):
    result: float = Field(..., description="The answer.", examples=[16])


class Operation(str, Enum):
    add = "add"
    subtract = "subtract"
    multiply = "multiply"
    divide = "divide"


class CalculateRequest(BaseModel):
    """An operation and the numbers to apply it to (v2)."""

    operation: Operation = Field(..., description="Which operation to perform.", examples=["add"])
    operands: list[float] = Field(
        ...,
        min_length=2,
        max_length=20,
        description=(
            "Two or more numbers. The operation is applied left to right, "
            "so `subtract` on `[10, 3, 2]` is `(10 - 3) - 2 = 5`."
        ),
        examples=[[10, 3, 2]],
    )


class CalculateResponse(Result):
    operation: Operation = Field(..., description="The operation that was performed.", examples=["subtract"])
    operands: list[float] = Field(..., description="The numbers that were used.", examples=[[10, 3, 2]])


class ErrorResponse(BaseModel):
    detail: str = Field(..., description="What went wrong.", examples=["Cannot divide by zero"])


DIVIDE_BY_ZERO = {400: {"model": ErrorResponse, "description": "Division by zero."}}

# --------------------------------------------------------------------------- #
# The app
# --------------------------------------------------------------------------- #

app = FastAPI(
    title="Calculator API",
    version="2.0.0",
    summary="Add, subtract, multiply and divide over HTTP.",
    description=(
        "A small demo API for basic arithmetic.\n\n"
        "**v1** has one endpoint per operation and takes exactly two numbers. "
        "**v2** adds `POST /v2/calculate`, which takes any operation and up to 20 numbers. "
        "Both versions return a `400` error when you divide by zero."
    ),
    servers=[{"url": "http://localhost:8000", "description": "Local development"}],
    openapi_tags=[
        {"name": "v1", "description": "Original endpoints: one operation each, two numbers."},
        {"name": "v2", "description": "Newer endpoint: any operation, two or more numbers."},
    ],
)

# Allow browsers to call the API from anywhere. The docs' "Try it" playground
# sends requests straight from your browser to the API, so it needs CORS.
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


@app.post("/v1/add", tags=["v1"], operation_id="v1Add", summary="Add two numbers", response_model=Result)
def v1_add(body: Operands) -> Result:
    """Return `a + b`."""
    return Result(result=add(body.a, body.b))


@app.post("/v1/subtract", tags=["v1"], operation_id="v1Subtract", summary="Subtract two numbers", response_model=Result)
def v1_subtract(body: Operands) -> Result:
    """Return `a - b`."""
    return Result(result=subtract(body.a, body.b))


@app.post("/v1/multiply", tags=["v1"], operation_id="v1Multiply", summary="Multiply two numbers", response_model=Result)
def v1_multiply(body: Operands) -> Result:
    """Return `a * b`."""
    return Result(result=multiply(body.a, body.b))


@app.post(
    "/v1/divide",
    tags=["v1"],
    operation_id="v1Divide",
    summary="Divide two numbers",
    response_model=Result,
    responses=DIVIDE_BY_ZERO,
)
def v1_divide(body: Operands) -> Result:
    """Return `a / b`. Returns a `400` error if `b` is `0`."""
    return Result(result=safe_divide(body.a, body.b))


@app.post(
    "/v2/calculate",
    tags=["v2"],
    operation_id="v2Calculate",
    summary="Calculate with any operation",
    response_model=CalculateResponse,
    responses=DIVIDE_BY_ZERO,
)
def v2_calculate(body: CalculateRequest) -> CalculateResponse:
    """Apply one operation across two or more numbers, left to right.

    Division stops with a `400` error as soon as any divisor is `0`.
    """
    functions = {
        Operation.add: add,
        Operation.subtract: subtract,
        Operation.multiply: multiply,
        Operation.divide: safe_divide,
    }
    fn = functions[body.operation]

    total = body.operands[0]
    for number in body.operands[1:]:
        total = fn(total, number)
    return CalculateResponse(result=total, operation=body.operation, operands=body.operands)
