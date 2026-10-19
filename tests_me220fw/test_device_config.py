"""Static regression tests for the ME220FW local Tuya datapoint mapping.

These checks deliberately make no claim about live battery reporting or hardware.
"""

# Pytest assertions are intentional in this standalone regression module.
# ruff: noqa: S101
from pathlib import Path

import yaml

CONFIG = (
    Path(__file__).resolve().parents[1]
    / "custom_components/tuya_local/devices/me220fw_smart_water_valve.yaml"
)


def _device():
    with CONFIG.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def test_me220fw_product_identity():
    device = _device()
    assert device["name"] == "ME220FW smart water valve"
    assert any(p["id"] == "6w5zwkrivvjgqizb" and p["model"] == "ME220FW" for p in device["products"])


def test_me220fw_local_datapoints_are_unique_and_have_expected_roles():
    device = _device()
    expected = {
        102: ("valve", "boolean"),
        2: ("number", "integer"),
        3: ("sensor", "integer"),
        5: ("sensor", "integer"),
        6: ("sensor", "integer"),
        116: ("sensor", "integer"),
    }
    actual = {}
    for entity in device["entities"]:
        assert len(entity["dps"]) == 1
        dp = entity["dps"][0]
        assert dp["id"] not in actual, "Duplicate Tuya DP would create conflicting entities"
        actual[dp["id"]] = (entity["entity"], dp["type"])
    assert actual == expected


def test_me220fw_water_usage_scaling_and_position_limits():
    by_id = {entity["dps"][0]["id"]: entity["dps"][0] for entity in _device()["entities"]}
    for dp_id in (5, 6):
        assert by_id[dp_id]["unit"] == "L"
        assert by_id[dp_id]["mapping"] == [{"scale": 100}]
    assert by_id[2]["range"] == {"min": 0, "max": 100}
    assert by_id[2]["mapping"] == [{"step": 10}]
    assert by_id[3]["range"] == {"min": 0, "max": 100}


def test_me220fw_does_not_invent_unavailable_local_battery_dp():
    local_ids = [d["id"] for entity in _device()["entities"] for d in entity["dps"]]
    assert 7 not in local_ids, "Battery DP 7 is cloud metadata, absent from tested local protocol 3.5"
