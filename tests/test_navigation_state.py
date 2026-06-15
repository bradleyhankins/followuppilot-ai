from __future__ import annotations

from app import (
    DEFAULT_VIEW,
    NAVIGATION_KEY,
    open_lead_in_workspace,
    route_for_view,
    set_view_state,
)


def test_set_view_state_updates_view_and_navigation_widget_key():
    state: dict[str, object] = {"view": "Manager Dashboard", NAVIGATION_KEY: "Manager Dashboard"}

    view = set_view_state(state, "Lead Workspace")

    assert view == "Lead Workspace"
    assert state["view"] == "Lead Workspace"
    assert state[NAVIGATION_KEY] == "Lead Workspace"


def test_invalid_view_state_falls_back_to_manager_dashboard():
    state: dict[str, object] = {}

    view = set_view_state(state, "Unknown")

    assert view == DEFAULT_VIEW
    assert state["view"] == DEFAULT_VIEW
    assert state[NAVIGATION_KEY] == DEFAULT_VIEW


def test_open_lead_in_workspace_sets_selected_lead_and_controlled_view():
    state: dict[str, object] = {"view": "Manager Dashboard", NAVIGATION_KEY: "Manager Dashboard"}

    lead_id = open_lead_in_workspace(state, "FUP-1004 - Taylor Brooks (Windows)")

    assert lead_id == "FUP-1004"
    assert state["selected_lead_id"] == "FUP-1004"
    assert state["view"] == "Lead Workspace"
    assert state[NAVIGATION_KEY] == "Lead Workspace"


def test_open_lead_after_sidebar_render_defers_navigation_widget_sync():
    state: dict[str, object] = {"view": "Manager Dashboard", NAVIGATION_KEY: "Manager Dashboard"}

    open_lead_in_workspace(
        state,
        "FUP-1004 - Taylor Brooks (Windows)",
        sync_navigation_widget=False,
    )

    assert state["selected_lead_id"] == "FUP-1004"
    assert state["view"] == "Lead Workspace"
    assert state[NAVIGATION_KEY] == "Manager Dashboard"
    assert route_for_view(state["view"]) == "Lead Workspace"


def test_programmatic_lead_workspace_navigation_is_not_overridden_by_old_dashboard_value():
    state: dict[str, object] = {"view": "Manager Dashboard", NAVIGATION_KEY: "Manager Dashboard"}

    open_lead_in_workspace(state, "FUP-1010 - Quinn Harper (Home Inspection)")

    assert route_for_view(state["view"]) == "Lead Workspace"
    assert state[NAVIGATION_KEY] == "Lead Workspace"


def test_route_for_view_is_exclusive_and_known():
    assert route_for_view("Manager Dashboard") == "Manager Dashboard"
    assert route_for_view("Lead Workspace") == "Lead Workspace"
    assert route_for_view("Follow-Up Builder") == "Follow-Up Builder"
    assert route_for_view("About This Demo") == "About This Demo"
    assert route_for_view("Not a real page") == DEFAULT_VIEW
