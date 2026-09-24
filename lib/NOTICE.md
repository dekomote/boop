# Third-party libraries

The files in this folder are unmodified copies of parts of the official KiCad
libraries (symbols and footprints), trimmed down to the few footprints this
board uses:

- `symbols/`: Device, Connector_Generic, Relay, Isolator, power
- `footprints/`: Capacitor_SMD, Connector_JST, Connector_PinHeader_2.54mm,
  Connector_PinSocket_2.54mm, Diode_SMD, Package_DIP, Package_SO,
  Package_TO_SOT_SMD, Relay_SMD, Resistor_SMD

They are licensed under CC BY-SA 4.0 with the KiCad libraries exception, which
lets you use them in your own designs without the licence applying to the
design itself. If you modify or redistribute the libraries on their own, they
stay under the KiCad library licence:
https://www.kicad.org/libraries/license/

The one exception is `footprints/MountingHole.pretty/MountingHole_3.2mm.kicad_mod`,
which was generated for this project and is covered by the project licence.
