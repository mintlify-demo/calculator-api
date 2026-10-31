import pytest
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


@pytest.mark.parametrize(
    "op, a, b, expected",
    [("add", 12, 4, 16), ("subtract", 12, 4, 8), ("multiply", 12, 4, 48), ("divide", 12, 4, 3)],
)
def test_v1_operations(op, a, b, expected):
    r = client.post(f"/v1/{op}", json={"a": a, "b": b})
    assert r.status_code == 200
    assert r.json() == {"result": expected}


def test_v1_handles_decimals_and_negatives():
    assert client.post("/v1/add", json={"a": 0.5, "b": -2}).json() == {"result": -1.5}


def test_v1_divide_by_zero_is_400():
    r = client.post("/v1/divide", json={"a": 1, "b": 0})
    assert r.status_code == 400
    assert r.json() == {"detail": "Cannot divide by zero"}


def test_v1_rejects_missing_field():
    assert client.post("/v1/add", json={"a": 1}).status_code == 422


def test_v2_folds_left_to_right():
    r = client.post("/v2/calculate", json={"operation": "subtract", "operands": [10, 3, 2]})
    assert r.status_code == 200
    assert r.json() == {"result": 5, "operation": "subtract", "operands": [10, 3, 2]}


def test_v2_multiply_many():
    r = client.post("/v2/calculate", json={"operation": "multiply", "operands": [2, 3, 4]})
    assert r.json()["result"] == 24


def test_v2_divide_by_zero_is_400():
    r = client.post("/v2/calculate", json={"operation": "divide", "operands": [8, 2, 0]})
    assert r.status_code == 400
    assert r.json()["detail"] == "Cannot divide by zero"


def test_v2_needs_two_operands():
    r = client.post("/v2/calculate", json={"operation": "add", "operands": [1]})
    assert r.status_code == 422


def test_v2_power_folds_left_to_right():
    r = client.post("/v2/calculate", json={"operation": "power", "operands": [2, 3, 2]})
    assert r.status_code == 200
    assert r.json()["result"] == 64


def test_v2_modulo():
    r = client.post("/v2/calculate", json={"operation": "modulo", "operands": [17, 5]})
    assert r.json()["result"] == 2


def test_v2_modulo_by_zero_is_400():
    r = client.post("/v2/calculate", json={"operation": "modulo", "operands": [17, 0]})
    assert r.status_code == 400


def test_v2_rejects_unknown_operation():
    r = client.post("/v2/calculate", json={"operation": "logarithm", "operands": [1, 2]})
    assert r.status_code == 422


def test_v2_sqrt():
    r = client.post("/v2/sqrt", json={"number": 144})
    assert r.status_code == 200
    assert r.json() == {"result": 12, "number": 144}


def test_v2_sqrt_precision():
    r = client.post("/v2/sqrt", json={"number": 2, "precision": 3})
    assert r.json()["result"] == 1.414


def test_v2_sqrt_rejects_negative():
    assert client.post("/v2/sqrt", json={"number": -4}).status_code == 422


def test_v1_endpoints_are_marked_deprecated():
    paths = app.openapi()["paths"]
    for op in ["add", "subtract", "multiply", "divide"]:
        assert paths[f"/v1/{op}"]["post"]["deprecated"] is True
    assert "deprecated" not in paths["/v2/calculate"]["post"]
