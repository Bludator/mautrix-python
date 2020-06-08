# Copyright (c) 2020 Tulir Asokan
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
from typing import Optional, Type
import logging

from mautrix.types import RoomID
from mautrix.appservice import IntentAPI
from mautrix.api import Method, Path, PathBuilder
from mautrix.util.logging import TraceLogger

from .puppet import BasePuppet
from .user import BaseUser


class NotificationDisabler:
    puppet_cls: Type[BasePuppet]
    config_enabled: bool = False
    log: TraceLogger = logging.getLogger("mau.notification_disabler")

    room_id: RoomID
    intent: Optional[IntentAPI]
    enabled: bool

    def __init__(self, room_id: RoomID, user: BaseUser) -> None:
        self.room_id = room_id
        self.enabled = False
        puppet = self.puppet_cls.get_by_custom_mxid(user.mxid)
        if puppet and puppet.is_real_user:
            self.intent = puppet.intent

    @property
    def _path(self) -> PathBuilder:
        return Path.pushrules["global"].override["net.maunium.silence_while_backfilling"]

    @property
    def _rule(self) -> dict:
        return {
            "actions": ["dont_notify"],
            "conditions": [{
                "kind": "event_match",
                "key": "room_id",
                "pattern": self.room_id,
            }]
        }

    async def __aenter__(self) -> None:
        if not self.intent or not self.config_enabled:
            return
        self.enabled = True
        try:
            self.log.debug(f"Disabling notifications in {self.room_id} for {self.intent.mxid}")
            await self.intent.api.request(Method.PUT, self._path, content=self._rule)
        except Exception:
            self.log.warning(f"Failed to disable notifications in {self.room_id} "
                             f"for {self.intent.mxid} while backfilling", exc_info=True)
            raise

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if not self.enabled:
            return
        try:
            self.log.debug(f"Re-enabling notifications in {self.room_id} for {self.intent.mxid}")
            await self.intent.api.request(Method.DELETE, self._path)
        except Exception:
            self.log.warning(f"Failed to re-enable notifications in {self.room_id} "
                             f"for {self.intent.mxid} after backfilling", exc_info=True)