#!/usr/bin/env python3
"""Turn the raw KiCad exports in fab/ into files JLCPCB and a human can use.

Run after exporting from KiCad (Gerbers + fab/bom.csv + fab/positions.csv):

    python3 scripts/jlcpcb_files.py

Writes:
  fab/jlcpcb_assembly/BOM_SMT.csv          SMD parts only, JLCPCB column names
  fab/jlcpcb_assembly/CPL_SMT.csv          placement file for the SMD parts
  fab/jlcpcb_assembly/CPL_ALL_incl_THT.csv same, with the through-hole parts
  fab/BOM_full_with_wires.csv              everything you need to buy
  fab/boop_gerbers.zip                     the Gerbers, ready to upload
"""
import csv
import pathlib
import zipfile

FAB = pathlib.Path(__file__).resolve().parent.parent / "fab"
OUT = FAB / "jlcpcb_assembly"
OUT.mkdir(exist_ok=True)


def is_tht(footprint):
    return footprint.startswith("Connector_")


with open(FAB / "bom.csv") as f:
    bom = list(csv.DictReader(f))
with open(FAB / "positions.csv") as f:
    pos = list(csv.DictReader(f))

# Only parts that are in the schematic BOM (skips the mounting holes).
bom_refs = {r.strip() for row in bom for r in row["Designator"].split(",")}
smt_bom = [r for r in bom if not is_tht(r["Footprint"])]
smt_refs = {r.strip() for row in smt_bom for r in row["Designator"].split(",")}

with open(OUT / "BOM_SMT.csv", "w", newline="") as f:
    w = csv.writer(f, quoting=csv.QUOTE_ALL)
    w.writerow(["Comment", "Designator", "Footprint", "LCSC Part #"])
    for r in smt_bom:
        w.writerow([r["Comment"], r["Designator"],
                    r["Footprint"].split(":")[-1], r["LCSC Part #"]])


def write_cpl(rows, path):
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Designator", "Mid X", "Mid Y", "Layer", "Rotation"])
        for r in rows:
            w.writerow([r["Ref"], f"{float(r['PosX']):.4f}mm",
                        f"{float(r['PosY']):.4f}mm",
                        "Top" if r["Side"] == "top" else "Bottom",
                        f"{float(r['Rot']):.0f}"])


write_cpl([r for r in pos if r["Ref"] in smt_refs], OUT / "CPL_SMT.csv")
write_cpl([r for r in pos if r["Ref"] in bom_refs], OUT / "CPL_ALL_incl_THT.csv")

# ---- full shopping list ---------------------------------------------------
rows = []
for r in bom:
    n = len([x for x in r["Designator"].split(",") if x.strip()])
    tht = is_tht(r["Footprint"])
    rows.append([r["Comment"], r["Designator"], n, r["Footprint"].split(":")[-1],
                 r["LCSC Part #"], "No - hand solder" if tht else "Yes", ""])

DUPONT = "Dupont wire, female-female, 20cm, 22AWG (1P)"
extra = [
    # (comment, designator, qty, footprint, lcsc, assembled, note)
    (DUPONT, "W1,W2", 2, "Wire", "C368922", "No",
     "J2 -> motherboard power switch header (polarity does not matter)"),
    (DUPONT, "W3,W4", 2, "Wire", "C368922", "No",
     "J4 -> motherboard reset switch header (polarity does not matter)"),
    (DUPONT, "W5,W6", 2, "Wire", "C368922", "No",
     "J8 -> motherboard power LED header: PLED+ to the pin marked +"),
    (DUPONT, "W7,W8", 2, "Wire", "C368922", "No",
     "Optional 5V feed. Cut one end off each, crimp into the XH housing below. "
     "Other ends go to motherboard USB header pin 1 (VCC, red) and pin 7 (GND, black)"),
    ("JST XHP-2 housing (mates with J1)", "P1", 1, "", "C144401", "No",
     "For the 5V feed cable"),
    ("JST SXH-001T-P0.6 crimp terminal", "P1", 2, "", "C140573", "No",
     "For the 5V feed cable, 22-28 AWG, needs a crimp tool"),
    ("M3 standoff (length to suit your case)", "H1-H4", 4, "", "", "No",
     "Not stocked by JLCPCB, buy anywhere"),
    ("M3 screw (or nut + screw)", "H1-H4", 8, "", "", "No",
     "Nylon is the safe choice, GND pour touches the hole edges"),
    ("(no wire needed)", "J3,J5,J9", 3, "", "", "",
     "Plug straight into the case power, reset and power LED leads"),
]
rows.extend(list(e) for e in extra)

with open(FAB / "BOM_full_with_wires.csv", "w", newline="") as f:
    w = csv.writer(f, quoting=csv.QUOTE_ALL)
    w.writerow(["Comment", "Designator", "Quantity", "Footprint",
                "LCSC Part #", "Assembled by JLCPCB", "Notes"])
    w.writerows(rows)

# ---- Gerber zip ------------------------------------------------------------
zpath = FAB / "boop_gerbers.zip"
with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
    for p in sorted((FAB / "gerbers").iterdir()):
        z.write(p, p.name)

print(f"{len(smt_refs)} SMD parts, {len(bom_refs) - len(smt_refs)} hand-solder parts, "
      f"{sum(1 for r in rows if r[4] == 'C368922' for _ in [0])} wire lines, zip: {zpath.name}")
