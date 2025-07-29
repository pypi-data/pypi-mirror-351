"""REST Server for the MADSci Event Manager"""

from typing import Any, Optional

import uvicorn
from fastapi import FastAPI
from fastapi.params import Body
from madsci.client.event_client import EventClient
from madsci.common.types.event_types import Event, EventManagerDefinition
from madsci.event_manager.notifications import EmailAlerts
from pymongo import MongoClient
from pymongo.synchronous.database import Database


def create_event_server(  # noqa: C901
    event_manager_definition: Optional[EventManagerDefinition] = None,
    db_connection: Optional[Database] = None,
) -> FastAPI:
    """Creates an Event Manager's REST server."""

    if event_manager_definition is None:
        event_manager_definition = EventManagerDefinition.load_model(
            require_unique=True
        )
    if event_manager_definition.event_client_config.name is None:
        event_manager_definition.event_client_config.name = (
            f"event_manager.{event_manager_definition.name}"
        )
    logger = EventClient(
        config=event_manager_definition.event_client_config,
    )
    if db_connection is None:
        db_client = MongoClient(event_manager_definition.db_url)
        db_connection = db_client["madsci_events"]

    app = FastAPI()
    events = db_connection["events"]
    events.create_index("event_id", unique=True, background=True)

    @app.get("/")
    @app.get("/info")
    @app.get("/definition")
    async def root() -> EventManagerDefinition:
        """Return the Event Manager Definition"""
        return event_manager_definition

    @app.post("/event")
    async def log_event(event: Event) -> Event:
        """Create a new event."""
        events.insert_one(event.model_dump(mode="json"))
        if event.alert or event.log_level >= event_manager_definition.alert_level:  # noqa: SIM102
            if event_manager_definition.email_alerts:
                email_alerter = EmailAlerts(
                    config=event_manager_definition.email_alerts,
                    logger=logger,
                )
                email_alerter.send_email_alerts(event)
        return event

    @app.get("/event/{event_id}")
    async def get_event(event_id: str) -> Event:
        """Look up an event by event_id"""
        return events.find_one({"event_id": event_id})

    @app.get("/events")
    async def get_events(number: int = 100, level: int = 0) -> dict[str, Event]:
        """Get the latest events"""
        event_list = (
            events.find({"log_level": {"$gte": level}})
            .sort("event_timestamp", -1)
            .limit(number)
            .to_list()
        )
        return {event["event_id"]: event for event in event_list}

    @app.post("/events/query")
    async def query_events(selector: Any = Body()) -> dict[str, Event]:  # noqa: B008
        """Query events based on a selector. Note: this is a raw query, so be careful."""
        event_list = events.find(selector).to_list()
        return {event["event_id"]: event for event in event_list}

    return app


if __name__ == "__main__":
    event_manager_definition = EventManagerDefinition.load_model(require_unique=True)
    db_client = MongoClient(event_manager_definition.db_url)
    db_connection = db_client["madsci_events"]
    app = create_event_server(
        event_manager_definition=event_manager_definition,
        db_connection=db_connection,
    )
    uvicorn.run(
        app,
        host=event_manager_definition.host,
        port=event_manager_definition.port,
    )
