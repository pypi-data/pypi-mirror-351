# DI2008-Python

## About
Interface for the DI-2008 in Python.

Modified from original interface in Python by DATAQ Instruments under MIT License

Maintainer: Clark Hensley ch3136@msstate.edu

## Getting Started
Install via pip from PyPI:
```sh
pip install di2008-python
```

Instantiate DI2008 Object with Dictionary of Parameters:
```py
from di2008_python import DI2008, DI2008Channels, DI2008Layout, DI2008TCType

# Enable the DI-2008 with a K-Type thermocopule in Analog Channel 1, an N-Type Thermocouple in Analog Channel 3, and the Digital Channel active
di2008 = DI2008({
    <DI-2008 SERIAL NUMBER>: {
        DI2008Channels.CH1: (DI2008Layout.TC, DI2008TCType.K),
        DI2008Channels.CH3: (DI2008Layout.TC, DI2008TCType.N),
        }
    },
    use_digital=True)
```

This interface uses named enumerations to ensure that what settings are being used is clear and concise

## Current Features:
* Thermocouples
* ADC Reading
* Digital Reading
* Changing Scan Rate, Decimation, and Filtering Mode
* Automatic ChannelStretch Synchronized Initialization

## Planned Features:
* Changing Packet Rate Size
* Interface with the `info` operator
* Enforce cleanup on stopping
* CJCDelta
* Rate Measurement
* LED Color
* Specify Digital Input as well as Output
* Reading configuration from .json/.toml files as well as raw Python dictionaries

Further information about the DI-2008 can be found on [DATAQ's website](https://www.dataq.com/products/di-2008) and via the [DI-2008 Protocol](https://www.dataq.com/resources/pdfs/misc/di-2008%20protocol.pdf).
