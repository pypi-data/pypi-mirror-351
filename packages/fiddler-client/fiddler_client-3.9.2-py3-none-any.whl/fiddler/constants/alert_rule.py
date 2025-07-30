import enum


@enum.unique
class BinSize(str, enum.Enum):
    HOUR = 'Hour'
    DAY = 'Day'
    WEEK = 'Week'
    MONTH = 'Month'


@enum.unique
class CompareTo(str, enum.Enum):
    """Comparison with Absolute(raw_value) or Relative(time_period)"""

    TIME_PERIOD = 'time_period'
    RAW_VALUE = 'raw_value'


@enum.unique
class AlertCondition(str, enum.Enum):
    GREATER = 'greater'
    LESSER = 'lesser'


@enum.unique
class Priority(str, enum.Enum):
    HIGH = 'HIGH'
    MEDIUM = 'MEDIUM'
    LOW = 'LOW'


@enum.unique
class AlertThresholdAlgo(str, enum.Enum):
    MANUAL = 'manual'
    STD_DEV_AUTO_THRESHOLD = 'standard_deviation_auto_threshold'

    def __str__(self) -> str:
        return self.value
