#!/usr/bin/env python3

import asyncio
import logging

from monzo import Monzo
from nio import AsyncClient, AsyncClientConfig, RoomMessageText, InviteEvent

from callbacks import Callbacks
from config import Config

logger = logging.getLogger(__name__)


async def main():
    # Read config file
    config = Config("config.yaml")

    # Configuration options for the AsyncClient
    nio_client_config = AsyncClientConfig(
        max_limit_exceeded=0,
        max_timeouts=0,
        store_sync_tokens=True,
    )

    # Initialize the matrix client
    nio_client = AsyncClient(
        config.homeserver_url,
        config.user_id,
        device_id=config.device_id,
        config=nio_client_config,
        store_path="/home/brendan/Documents/matrix-monzo-next/nio_store",
    )

    # Initialise the monzo client
    monzo_client = Monzo(config.monzo_access_token)

    await nio_client.login(config.password, "monzo_bot")

    # Set up event callbacks
    callbacks = Callbacks(config, nio_client, monzo_client)
    nio_client.add_event_callback(callbacks.message, (RoomMessageText,))
    nio_client.add_event_callback(callbacks.invite, (InviteEvent,))

    # First do a sync with full_state = true to retrieve the state of the room.
    await nio_client.sync(full_state=True)

    await nio_client.sync_forever(30000)

asyncio.get_event_loop().run_until_complete(main())
