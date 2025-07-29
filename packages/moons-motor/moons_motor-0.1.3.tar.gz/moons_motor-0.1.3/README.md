# Moons Motor

This is a python library for control moons motor through serial port.

## Compatibility

Now only support Windows.

## Installing

Install through `pip`

```bash
python -m pip install moons_motor

```

## Usage

```python
from motor import MoonsStepper, StepperModules
import simulate
from time import sleep

motor = MoonsStepper(StepperModules.STM17S_3RN, "0403", "6001", "TESTA")

MoonsStepper.list_all_ports()
motor.connect()

motor.start_jog("", 10)
sleep(5)
motor.stop_jog()

```

## Tested Motor

1. STM17S-3RN

## Reference
