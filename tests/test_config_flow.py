from types import MappingProxyType
from unittest.mock import patch

import pytest
from homeassistant import config_entries, data_entry_flow
from homeassistant.core import HomeAssistant
from homeassistant.helpers import discovery_flow

from custom_components.delayed_charging.config_flow import (
    DelayedChargingConfigFlow,
    DelayedChargingOptionsFlow,
)
from custom_components.delayed_charging.const import (
    CONF_COUNTRY_ID,
    CONF_THRESH,
    DEFAULT_COUNTRY_ID,
    DEFAULT_THRESH,
    DOMAIN,
)


@pytest.fixture
def mock_config_flow():
    return DelayedChargingConfigFlow()


async def test_async_step_user_valid_input(
    hass: HomeAssistant, mock_config_flow: DelayedChargingConfigFlow, coordinator_update_patch: None
):
    """Test async_step_user with valid input."""
    user_input = {
        CONF_COUNTRY_ID: DEFAULT_COUNTRY_ID,
        CONF_THRESH: DEFAULT_THRESH,
    }

    with patch.object(
        mock_config_flow,
        "async_create_entry",
        wraps=mock_config_flow.async_create_entry,
    ) as mock_create_entry:
        result: config_entries.ConfigFlowResult = await mock_config_flow.async_step_user(user_input)

        assert result.get("type") == data_entry_flow.FlowResultType.CREATE_ENTRY
        assert result.get("title") == "Delayed Charging"
        assert result.get("data") == user_input
        mock_create_entry.assert_called_once_with(title="Delayed Charging", data=user_input, options=user_input)


async def test_async_step_user_show_form(hass: HomeAssistant, mock_config_flow: DelayedChargingConfigFlow):
    """Test async_step_user shows form when no input is provided."""
    result: config_entries.ConfigFlowResult = await mock_config_flow.async_step_user(None)

    assert result.get("type") == data_entry_flow.FlowResultType.FORM
    assert result.get("step_id") == "user"
    schema = getattr(result.get("data_schema"), "schema")
    assert CONF_COUNTRY_ID in schema
    assert CONF_THRESH in schema


async def test_async_get_options_flow(hass: HomeAssistant):
    """Test async_get_options_flow returns the correct options flow."""
    config_entry = config_entries.ConfigEntry(
        version=1,
        minor_version=0,
        unique_id="1",
        discovery_keys=MappingProxyType({"a": (discovery_flow.DiscoveryKey(domain=DOMAIN, key="a", version=1),)}),
        subentries_data=None,
        domain=DOMAIN,
        title="Delayed Charging",
        data={},
        options={},
        entry_id="1",
        source=config_entries.SOURCE_USER,
    )

    flow = DelayedChargingConfigFlow.async_get_options_flow(config_entry)
    assert isinstance(flow, DelayedChargingOptionsFlow)


async def test_async_step_init_valid_input(hass: HomeAssistant, coordinator_update_patch: None):
    """Test async_step_init with valid input."""
    options_flow = DelayedChargingOptionsFlow()
    await hass.config_entries.async_add(
        config_entries.ConfigEntry(
            unique_id="1",
            discovery_keys=MappingProxyType({"a": (discovery_flow.DiscoveryKey(domain=DOMAIN, key="a", version=1),)}),
            subentries_data=None,
            version=1,
            minor_version=0,
            domain=DOMAIN,
            title="Delayed Charging",
            data={},
            options={},
            entry_id="1",
            source=config_entries.SOURCE_USER,
        )
    )
    options_flow.hass = hass
    options_flow.handler = "1"

    user_input = {
        CONF_COUNTRY_ID: DEFAULT_COUNTRY_ID,
        CONF_THRESH: DEFAULT_THRESH,
    }

    with patch.object(
        options_flow,
        "async_create_entry",
        wraps=options_flow.async_create_entry,
    ) as mock_create_entry:
        result: config_entries.ConfigFlowResult = await options_flow.async_step_init(user_input)

        assert result.get("type") == data_entry_flow.FlowResultType.CREATE_ENTRY
        assert result.get("data") == user_input
        mock_create_entry.assert_called_once_with(data=user_input)


async def test_async_step_init_show_form(hass: HomeAssistant, coordinator_update_patch: None):
    """Test async_step_init shows form when no input is provided."""
    options_flow = DelayedChargingOptionsFlow()
    await hass.config_entries.async_add(
        config_entries.ConfigEntry(
            version=1,
            minor_version=0,
            unique_id="1",
            discovery_keys=MappingProxyType({"a": (discovery_flow.DiscoveryKey(domain=DOMAIN, key="a", version=1),)}),
            subentries_data=None,
            domain=DOMAIN,
            title="Delayed Charging",
            data={},
            options={},
            entry_id="1",
            source=config_entries.SOURCE_USER,
        )
    )
    options_flow.hass = hass
    options_flow.handler = "1"

    result: config_entries.ConfigFlowResult = await options_flow.async_step_init(None)

    assert result.get("type") == data_entry_flow.FlowResultType.FORM
    assert result.get("step_id") == "init"
    schema = getattr(result.get("data_schema"), "schema")
    assert CONF_COUNTRY_ID in schema
    assert CONF_THRESH in schema
