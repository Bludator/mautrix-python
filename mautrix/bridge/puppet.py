# Copyright (c) 2021 Tulir Asokan
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
from __future__ import annotations
from typing import Dict, Any
from collections import defaultdict
from abc import ABC, abstractmethod
import asyncio
import logging

from mautrix.types import UserID
from mautrix.appservice import AppService, IntentAPI
from mautrix.util.logging import TraceLogger

from .custom_puppet import CustomPuppetMixin
from .. import bridge as br


class BasePuppet(CustomPuppetMixin, ABC):
    log: TraceLogger = logging.getLogger("mau.puppet")
    _async_get_locks: Dict[Any, asyncio.Lock] = defaultdict(lambda: asyncio.Lock())
    az: AppService
    loop: asyncio.AbstractEventLoop
    mx: br.BaseMatrixHandler

    is_registered: bool
    mxid: str
    intent: IntentAPI

    @classmethod
    @abstractmethod
    async def get_by_mxid(cls, mxid: UserID) -> BasePuppet:
        pass

    @classmethod
    @abstractmethod
    async def get_by_custom_mxid(cls, mxid: UserID) -> BasePuppet:
        pass
