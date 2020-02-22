import attr
import enum
import numpy as np
from datetime import datetime
from enum import auto
from typing import List, Dict
from betfairstreamer.utils import parse_betfair_date


class BettingType(enum.Enum):
    ODDS = auto()
    LINE = auto()
    RANGE = auto()
    ASIAN_HANDICAP_DOUBLE_LINE = auto()
    ASIAN_HANDICAP_SINGLE_LINE = auto()


class Status(enum.Enum):
    INACTIVE = auto()
    OPEN = auto()
    SUSPENDED = auto()
    CLOSED = auto()


class PriceLadderType(enum.Enum):
    CLASSIC = auto()
    FINEST = auto()
    LINE_RANGE = auto()


class RunnerStatus(enum.Enum):
    ACTIVE = auto()
    WINNER = auto()
    LOSER = auto()
    REMOVED = auto()
    REMOVED_VACANT = auto()
    HIDDEN = auto()
    PLACED = auto()


@attr.s(slots=True, weakref_slot=False)
class PriceLadderDefinition:
    type = attr.ib(type=PriceLadderType)

    @classmethod
    def from_betfair_dict(cls, betfair_dict):
        return cls(type=betfair_dict.get("type", None))


@attr.s(slots=True, weakref_slot=False)
class KeyLineSelection:
    id = attr.ib(type=int)
    hc = attr.ib(type=float)

    @classmethod
    def from_betfair_dict(cls, betfair_dict):
        return cls(id=betfair_dict.get("id", None), hc=betfair_dict.get("hc", None))


@attr.s(slots=True, weakref_slot=False)
class KeyLineDefinition:
    kl = attr.ib(type=List[KeyLineSelection])

    @classmethod
    def from_betfair_dict(cls, betfair_dict):
        return cls(kl=[KeyLineSelection.from_betfair_dict(d) for d in betfair_dict.get("kl", [])])


@attr.s(slots=True, weakref_slot=False)
class RunnerDefinition:
    id = attr.ib(type=int)
    sort_priority = attr.ib(type=int)
    removal_date = attr.ib(type=datetime)
    hc = attr.ib(type=float)
    adjustment_factor = attr.ib(type=float)
    bsp = attr.ib(type=float)
    status = attr.ib(type=RunnerStatus)
    price_ladder_definition = attr.ib(type=PriceLadderDefinition)
    key_line_definition = attr.ib(type=KeyLineDefinition)
    hc = attr.ib(type=float)

    @classmethod
    def from_betfair_dict(cls, betfair_dict):
        return cls(
            id=betfair_dict.get("id", None),
            sort_priority=betfair_dict.get("sortPriority", None),
            removal_date=parse_betfair_date(betfair_dict.get("removalDate", None)),
            hc=betfair_dict.get("hc", None),
            adjustment_factor=betfair_dict.get("adjustmentFactor", None),
            bsp=betfair_dict.get("bsp", None),
            status=RunnerStatus[betfair_dict.get("status", "REMOVED")],
            price_ladder_definition=PriceLadderDefinition.from_betfair_dict(
                betfair_dict.get("priceLadderDefinition", {})
            ),
            key_line_definition=KeyLineDefinition.from_betfair_dict(
                betfair_dict.get("keylineDefinition", {})
            ),
        )


@attr.s(slots=True, weakref_slot=False)
class MarketDefinition:

    venue = attr.ib(type=str)
    race_type = attr.ib(type=str)
    settled_time = attr.ib(type=datetime)
    timezone = attr.ib(type=str)
    each_way_divisor = attr.ib(type=str)
    regulators = attr.ib(type=float)
    market_type = attr.ib(type=str)
    market_base_rate = attr.ib(type=float)
    number_of_winners = attr.ib(type=float)
    country_code = attr.ib(type=str)
    line_max_unit = attr.ib(type=float)
    in_play = attr.ib(type=bool)
    bet_delay = attr.ib(type=int)
    bsp_market = attr.ib(type=bool)
    betting_type = attr.ib(type=BettingType)
    number_of_active_runners = attr.ib(type=int)
    line_min_unit = attr.ib(type=float)
    event_id = attr.ib(type=str)
    cross_matching = attr.ib(type=bool)
    runner_voidable = attr.ib(type=bool)
    turn_in_play_enabled = attr.ib(type=bool)
    price_ladder_definition = attr.ib(type=PriceLadderDefinition)
    keyline_definition = attr.ib(type=KeyLineDefinition)
    suspend_time = attr.ib(type=datetime)
    discount_allowed = attr.ib(type=bool)
    persistence_enabled = attr.ib(type=bool)
    runners = attr.ib(type=List[RunnerDefinition])
    version = attr.ib(type=int)
    event_type_id = attr.ib(type=str)
    complete = attr.ib(type=bool)
    open_date = attr.ib(type=datetime)
    market_time = attr.ib(type=datetime)
    bsp_reconciled = attr.ib(type=bool)
    line_interval = attr.ib(type=float)
    status = attr.ib(type=Status)

    @classmethod
    def from_betfair_dict(cls, betfair_dict: Dict):
        return cls(
            venue=betfair_dict.get("venue", None),
            race_type=betfair_dict.get("raceType", None),
            settled_time=betfair_dict.get("settledTime", None),
            timezone=betfair_dict.get("timezone", None),
            each_way_divisor=betfair_dict.get("eachWayDivisor", None),
            regulators=betfair_dict.get("regulators", None),
            market_type=betfair_dict.get("marketType", None),
            market_base_rate=betfair_dict.get("marketBaseRate", None),
            number_of_winners=betfair_dict.get("numberOfWinners", None),
            country_code=betfair_dict.get("countryCode", None),
            line_max_unit=betfair_dict.get("lineMaxUnit", None),
            in_play=betfair_dict.get("inPlay", None),
            bet_delay=betfair_dict.get("betDelay", None),
            bsp_market=betfair_dict.get("bspMarket", None),
            betting_type=BettingType[betfair_dict.get("bettingType", None)],
            number_of_active_runners=betfair_dict["numberOfActiveRunners"],
            line_min_unit=betfair_dict.get("lineMinUnit", None),
            event_id=betfair_dict.get("eventId", None),
            cross_matching=betfair_dict.get("crossMatching", None),
            runner_voidable=betfair_dict.get("runnerVoidAble", None),
            turn_in_play_enabled=betfair_dict["turnInPlayEnabled"],
            price_ladder_definition=PriceLadderDefinition.from_betfair_dict(
                betfair_dict.get("priceLadderDefinition", {})
            ),
            keyline_definition=KeyLineDefinition.from_betfair_dict(
                betfair_dict.get("keylineDefinition", {})
            ),
            suspend_time=parse_betfair_date(betfair_dict.get("suspend_time", "")),
            discount_allowed=betfair_dict.get("discount_allowed", None),
            persistence_enabled=betfair_dict.get("persistenceEnabled", None),
            runners=[
                RunnerDefinition.from_betfair_dict(r) for r in betfair_dict.get("runners", [])
            ],
            version=betfair_dict.get("version", None),
            event_type_id=betfair_dict.get("eventTypeId", None),
            complete=betfair_dict.get("complete", None),
            open_date=parse_betfair_date(betfair_dict.get("openDate", None)),
            market_time=parse_betfair_date(betfair_dict.get("marketTime", None)),
            bsp_reconciled=betfair_dict.get("bspReconciled", None),
            line_interval=betfair_dict.get("lineInterval", None),
            status=Status[betfair_dict.get("status", None)],
        )


@attr.s
class RunnerBook:
    price_sizes = attr.ib(type=np.array)
    metadata = attr.ib(type=np.array)
    runner_definitions = attr.ib(type=List[RunnerDefinition])
    sort_priority_mapping = attr.ib(type=Dict[int, int])

    def update(self, runner_change: Dict):
        for r in runner_change:
            batb = r.get("bdatb", {})
            batl = r.get("bdatl", {})

            sort_priority = self.sort_priority_mapping[r["id"]]

            if batb:
                new_values = np.array(batb)
                batb_index = new_values[:, 0].astype(int)
                self.price_sizes[sort_priority - 1, 0, batb_index, :] = new_values[:, 1:]

            if batl:
                new_values = np.array(batl)
                batl_index = new_values[:, 0].astype(int)

                self.price_sizes[sort_priority - 1, 1, batl_index, :] = new_values[:, 1:]

            if "ltp" in r:
                self.metadata[sort_priority - 1] = r["ltp"]

    @classmethod
    def create_instance(cls, runner_definitions: List[RunnerDefinition], runner_changes: List):
        price_sizes = -1 * np.ones(shape=(len(runner_definitions), 2, 3, 2))
        metadata = np.zeros(shape=(len(runner_definitions)))
        sort_priority_mapping = {r.id: r.sort_priority for r in runner_definitions}

        runner_book = cls(
            price_sizes=price_sizes,
            metadata=metadata,
            runner_definitions=runner_definitions,
            sort_priority_mapping=sort_priority_mapping,
        )

        runner_book.update(runner_changes)

        return runner_book


@attr.s(slots=True, weakref_slot=False)
class MarketBook:

    market_id = attr.ib(type=str)
    market_definition = attr.ib(type=MarketDefinition)
    runner_book = attr.ib(type=RunnerBook, default=None)

    def update(self, market_update):

        if "marketDefinition" in market_update:
            self.market_definition = MarketDefinition.from_betfair_dict(
                market_update["marketDefinition"]
            )

        if market_update.get("img", False):
            self.runner_book = None

        if self.runner_book is None:
            self.runner_book = RunnerBook.create_instance(
                self.market_definition.runners, market_update.get("rc", [])
            )

        self.runner_book.update(market_update.get("rc", []))

    @classmethod
    def from_betfair_dict(cls, betfair_dict):
        assert "marketDefinition" in betfair_dict, "MarketDefinition must be present!"

        market_definition = MarketDefinition.from_betfair_dict(betfair_dict["marketDefinition"])

        return cls(
            market_id=betfair_dict["id"],
            market_definition=market_definition,
            runner_book=RunnerBook.create_instance(
                runner_definitions=market_definition.runners,
                runner_changes=betfair_dict.get("rc", []),
            ),
        )
