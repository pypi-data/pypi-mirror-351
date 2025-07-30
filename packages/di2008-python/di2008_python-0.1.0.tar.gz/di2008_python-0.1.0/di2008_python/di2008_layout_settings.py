"""
DATAQ DI-2008 Interface -- Layout Enumerations
Adapted from original DATAQ Instruments Python Interface under the MIT License

The DI-2008 uses a serial interface with integer values. This file declares the enumerations to describe these values

This file is part of DI2008_Python, https://github.com/Computational-Mechanics-Materials-Lab/DI2008_Python

MIT License
"""

from enum import IntEnum, Enum


class DI2008Layout(IntEnum):
    """
    Describes the connected device to each port on the DAQ
    """

    # Thermocouple
    # 0b0001000000000000
    TC = 0x1000

    # For enabling the Digital Channel
    # 0b0000000000001000
    DI = 0x0008

    # Used as a sentinel to ignore
    # 0b1111111111111111
    IGNORE = 0xFFFF

    # Analog-Digital converter
    # Number doesn't matter, left as 0
    # 0b0000000000000000
    ADC = 0x0000


class DI2008TCType(IntEnum):
    """
    Enumerates the types of Thermocouple which the DI-2008 cna read
    """

    B = 0x0 << 8
    E = 0x1 << 8
    J = 0x2 << 8
    K = 0x3 << 8
    N = 0x4 << 8
    R = 0x5 << 8
    S = 0x6 << 8
    T = 0x7 << 8


class DI2008ADCRange(Enum):
    """
    Enumerates the voltage ranges for ADC, as well as the necessary multiplier for rescaling
    """

    mV10 = ((0x5 << 8), 0.01)
    mV25 = ((0x4 << 8), 0.025)
    mV50 = ((0x3 << 8), 0.05)
    mV100 = ((0x2 << 8), 0.1)
    mV250 = ((0x1 << 8), 0.25)
    mV500 = ((0x0 << 8), 0.5)
    V1 = ((0xD << 8), 1.0)
    V2_5 = ((0xC << 8), 2.5)
    V5 = ((0xB << 8), 5.0)
    V10 = ((0xA << 8), 10.0)
    V25 = ((0x9 << 8), 25.0)
    V50 = ((0x8 << 8), 50.0)


class DI2008Channels(IntEnum):
    """
    Enumerates the 8 Analog Channels
    """

    CH1 = 0x0
    CH2 = 0x1
    CH3 = 0x2
    CH4 = 0x3
    CH5 = 0x4
    CH6 = 0x5
    CH7 = 0x6
    CH8 = 0x7


class EmptySentinel:
    """
    Just an empty value so that this doesn't get treated as an integer
    """

    pass


# used to denote all 8 channels, rather than a single integer
DI2008AllChannels = EmptySentinel()


class DI2008DigitalChannel(IntEnum):
    """
    This uses an IntEnum to associate the name, "DI" with the number for it, even though this is a singleton enum. This is not used by the user, just ste on the back-end
    """

    # The digital channel is
    # 0b0000000000001000
    DI = 0x8


class DI2008ScanRateSettings(Enum):
    """
    Sentinels to manage the values related to scan rate and filtering
    """

    SRATE = 0
    DEC = 1
    FILTER = 2


class DI2008FilterModes(Enum):
    """
    Values for Filtering of the DI-2008
    """

    LAST_POINT = 0
    AVERAGE = 1
    MAXIMUM = 2
    MINIMUM = 3


# Used to denote that the PS Value is being set
DI2008PSOption = EmptySentinel()


# Potential valid values for PS
class DI2008PSSettings(IntEnum):
    """
    Potential values for the PS setting
    """

    BYTES16 = 0
    BYTES32 = 1
    BYTES64 = 2
    BYTES128 = 3
