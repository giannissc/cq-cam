"""
# G-code Letter and Word Address Syntax

G-code (also RS-274/NGC) is the most widely-used computer numerical control (CNC) programming language. 
It is used mainly in computer-aided manufacturing to control automated machine tools, as well as from a 3D-printing slicer app.
Here we concentrate on a subset of G-code relevant for 3-axis CNC machining. Explanations of commands that are out of scope will be included for completeness and it will be indicated that they are out of scope.

A G-code command (word address) is formed by single letter (letter address) followed by 2 digits. A word may either give a command or provide an argument to a command.  Multiple words on the same line are called command blocks
```
 G 01 XYZ
⌊ ⌋  letter address
⌊   ⌋  word  address
⌊       ⌋  command block
```

G-code word addresses are used to configure the machine state and control the motors. The two primary letter addresses are M-codes and G-codes. M-codes are known as machine codes (or more accurately miscellaneous codes) and G-codes are called preparatory codes. M-codes allow for state changes of the machine components and the running program. G-codes control the motion of the motors and the internal configuration of the machine. In addition to the G and M address there are other letter addresses that are used in conjunction with them

Below is a comprehensive list of the available letter addresses:
- A <inch/mm> - 4th Axis: G0, G1, G2, G3, G81, G82, G83, G84, G85, G86, G88, G89 (out of scope)
- B <inch/mm> - 5th Axis: G0, G1, G2, G3, G81, G82, G83, G84, G85, G86, G88, G89 (out of scope)
- C <inch/mm> - 6th Axis: G0, G1, G2, G3, G81, G82, G83, G84, G85, G86, G88, G89 (out of scope)
- D <0-200> - Radius Offset: G41, G42
- E <0.0001-0.25>- Engraving Feed Rate: G187 (out of scope)
- F <inch/mm> - Feed Rate: G1, G2, G3
- G <0-187> - Preparatory Function
- H <0-200> - Tool Length Offset: G43, G44
- I <inch/mm> - Arc Center in X Axis: G2, G3, G87
- J <inch/mm> - Arc Center in Y Axis: G2, G3, G87
- K <inch/mm> - Arc Center in Z Axis: G2, G3, G87
- L <0-32767> - Canned Cycle Loop Count: G81, G82, G83, G84, G85, G86, G88, G89
- M <> - Miscellanesous Functions
- N <0-99999> - Number of Block
- O <0-99999> - Program Number
- P <0.001-1000.0> - Dwell Time: G4, G82, G86, G88, G89
- Q <0.001-100.0> - Feed Increment: G83
- R <inch/mm> - Circular Interpolation/Canned Cycle Data: G81, G82, G83, G84, G85, G86, G87, G88, G89
- S <1-99999> - Spindle Speed: M3, M4
- T <1-20>- Tool Selection: M6
- X <inch/mm> - X Axis: G0, G1, G2, G3, G81, G82, G83, G84, G85, G86, G88, G89
- Y <inch/mm> - Y Axis: G0, G1, G2, G3, G81, G82, G83, G84, G85, G86, G88, G89
- Z <inch/mm> - Y Axis: G0, G1, G2, G3, G81, G82, G83, G84, G85, G86, G88, G89

inch: 4 fractional positions
mm: 3 fractional positions
"""
from abc import ABC
from enum import Enum

import cadquery as cq

from cq_cam.utils.utils import optimize_float


class AddressVector:
    __slots__ = ("x", "y", "z")

    def __init__(self, x=None, y=None, z=None):
        self.x = x
        self.y = y
        self.z = z

    def __eq__(self, other) -> bool:
        try:
            return self.x == other.x and self.y == other.y and self.z == other.z
        except AttributeError:
            return NotImplemented

    def __str__(self) -> str:
        return f"({self.x} {self.y} {self.z})"

    @classmethod
    def from_vector(cls, v: cq.Vector):
        return cls(v.x, v.y, v.z)

    def to_vector(self, origin: cq.Vector, relative=False):
        if relative:
            x = 0 if self.x is None else self.x - origin.x
            y = 0 if self.y is None else self.y - origin.y
            z = 0 if self.z is None else self.z - origin.z
        else:
            x = origin.x if self.x is None else self.x
            y = origin.y if self.y is None else self.y
            z = origin.z if self.z is None else self.z
        return cq.Vector(x, y, z)


#############################################################################
class GCodeLetter(Enum):
    XAxis = "X"
    YAxis = "Y"
    ZAxis = "Z"
    ArcXAxis = "I"
    ArcYAxis = "J"
    ArcZAxis = "K"
    Feed = "F"
    Speed = "S"
    DwellTime = "P"
    ToolNumber = "T"
    RadiusOffset = "D"
    LengthOffset = "H"

    def __repr__(self):
        return f"{self.__class__.__name__}.{self._name_}"

    def __str__(self):
        return self._value_


#################################################################################
class GCodeWord(ABC):
    letter: GCodeLetter
    address: float | int

    def __init__(self, letter: GCodeLetter, address: float | int):
        self.letter = letter
        self.address = address

    def __str__(self):
        if self.address is not None:
            return f"{self.letter}{self.address}"
        return ""


class GCodeWordPrecision(GCodeWord, ABC):
    precision: int

    def __init__(self, letter: GCodeLetter, address: float | int, precision: int = 3):
        self.precision = precision
        super().__init__(letter, address)

    def __str__(self):
        if self.address is not None:
            address_opt = optimize_float(round(self.address, self.precision))
            return f"{self.letter}{address_opt}"
        return ""


class XAxis(GCodeWordPrecision):
    def __init__(self, address: float, precision: int = 3):
        super().__init__(GCodeLetter.XAxis, address, precision)


class YAxis(GCodeWordPrecision):
    def __init__(self, address: float, precision: int = 3):
        super().__init__(GCodeLetter.YAxis, address, precision)


class ZAxis(GCodeWordPrecision):
    def __init__(self, address: float, precision: int = 3):
        super().__init__(GCodeLetter.ZAxis, address, precision)


class ArcXAxis(GCodeWordPrecision):
    def __init__(self, address: float, precision: int = 3):
        super().__init__(GCodeLetter.ArcXAxis, address, precision)


class ArcYAxis(GCodeWordPrecision):
    def __init__(self, address: float, precision: int = 3):
        super().__init__(GCodeLetter.ArcYAxis, address, precision)


class ArcZAxis(GCodeWordPrecision):
    def __init__(self, address: float, precision: int = 3):
        super().__init__(GCodeLetter.ArcZAxis, address, precision)


class Feed(GCodeWord):
    def __init__(self, address: float):
        super().__init__(GCodeLetter.Feed, address)


class Speed(GCodeWord):
    def __init__(self, address: int):
        super().__init__(GCodeLetter.Speed, address)


class DwellTime(GCodeWord):
    def __init__(self, address: float):
        super().__init__(GCodeLetter.DwellTime, address)


class ToolNumber(GCodeWord):
    def __init__(self, address: int):
        super().__init__(GCodeLetter.ToolNumber, address)


class ToolLengthOffset(GCodeWord):
    def __init__(self, address: int):
        super().__init__(GCodeLetter.LengthOffset, address)


class ToolRadiusOffset(GCodeWord):
    def __init__(self, address: int):
        super().__init__(GCodeLetter.RadiusOffset, address)


#################################################################################
class GCodeAxisGroup(ABC):
    axis_1: GCodeWord
    axis_2: GCodeWord
    axis_3: GCodeWord

    def __init__(self, axis_1: GCodeWord, axis_2: GCodeWord, axis_3: GCodeWord):
        self.axis_1 = axis_1
        self.axis_2 = axis_2
        self.axis_3 = axis_3

    def __str__(self):
        coords = []
        axis_1 = str(self.axis_1)
        axis_2 = str(self.axis_2)
        axis_3 = str(self.axis_3)

        if axis_1 != "":
            coords.append(axis_1)
        if axis_2 != "":
            coords.append(axis_2)
        if axis_3 != "":
            coords.append(axis_3)

        return " ".join(coords)


class XYZ(GCodeAxisGroup):
    def __init__(self, end: AddressVector, precision: int = 3):
        axis_1 = XAxis(end.x, precision)
        axis_2 = YAxis(end.y, precision)
        axis_3 = ZAxis(end.z, precision)

        super().__init__(axis_1, axis_2, axis_3)


class IJK(GCodeAxisGroup):
    def __init__(self, center: AddressVector, precision: int = 3):
        axis_1 = ""
        axis_2 = ""
        axis_3 = ""
        
        if center.x != 0:
            axis_1 = ArcXAxis(center.x, precision)
        
        if center.y != 0:
            axis_2 = ArcYAxis(center.y, precision)

        if center.z != 0:
            axis_3 = ArcZAxis(center.z, precision)

        super().__init__(axis_1, axis_2, axis_3)
