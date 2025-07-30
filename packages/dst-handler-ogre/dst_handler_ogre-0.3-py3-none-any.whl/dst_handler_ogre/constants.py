from enum import Enum


class Resolution(Enum):
    FIVE_MINUTES = "5min"
    TEN_MINUTES = "10min"
    QUARTER_HOUR = "15min"
    HALF_HOUR = "30min"
    HOUR = "1h"


FREQUENCY_ENTRY_DICT = {
    Resolution.HOUR: 1,
    Resolution.HALF_HOUR: 2,
    Resolution.QUARTER_HOUR: 4,
    Resolution.TEN_MINUTES: 6,
    Resolution.FIVE_MINUTES: 12,
}


class Timezone(Enum):
    EET: str = "EET"
    UTC: str = "UTC"
