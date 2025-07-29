import sys
import types
from surepetcare.devices import load_device_class
from surepetcare.devices.feeder_connect import FeederConnect
from surepetcare.devices.hub import Hub
from surepetcare.enums import BowlPosition
from surepetcare.enums import FoodType
from surepetcare.enums import ProductId
from tests.mock_helpers import load_mock_data
from tests.mock_helpers import MockSurePetcareClient


def test_feeder_connect():
    client = MockSurePetcareClient({})
    # We only load the first pet
    feeder = FeederConnect(
        client, load_mock_data("tests/mock_data/mock_device_feeder_connect.json")["data"][0]
    )
    assert feeder.battery_level == 47
    assert feeder.id == 269654
    assert feeder.household_id == 7777
    assert feeder.name == "Cat feeder"
    assert feeder.online is False
    assert feeder.product_id == 4
    assert feeder.product_id == ProductId.FEEDER_CONNECT
    assert feeder.lid_delay == 4
    assert feeder.bowls[BowlPosition.LEFT].food_type == FoodType.DRY
    assert feeder.bowls[BowlPosition.RIGHT].food_type == FoodType.DRY


def test_hub():
    client = MockSurePetcareClient({})
    # We only load the first pet
    hub = Hub(client, load_mock_data("tests/mock_data/mock_device_hub.json")["data"][0])
    assert hub.household_id == 7777
    assert hub.id == 295972
    assert hub.name == "Hem-hub"
    assert hub.product_id == 1
    assert hub.product_id == ProductId.HUB
    assert hub.online is True
    assert hub.battery_level is None


def test_load_device_class(monkeypatch):

    class DummyEnum:
        name = "DUMMY_DEVICE"
        
    dummy_module = types.ModuleType("surepetcare.devices.dummy_device")
    class DummyDevice:
        pass
    setattr(dummy_module, "DummyDevice", DummyDevice)
    sys.modules["surepetcare.devices.dummy_device"] = dummy_module

    # Create a dummy enum with the expected name
    class DummyEnum:
        name = "DUMMY_DEVICE"

    device_class = load_device_class(DummyEnum)
    assert device_class is DummyDevice