#!/usr/bin/env python3
"""The component makers outside the Chinese listed index.

The index the page started from is a list of Chinese listed companies, which
makes it a map of one supply base rather than of the part. The incumbents that
every teardown names — Harmonic Drive on strain wave, THK on crossed roller
bearings, maxon on frameless motors, NVIDIA on compute — were simply absent,
and so were six subsystems nobody had a row for: magnets, encoders, brakes,
edge compute, thermal, interconnect.

Rows here are read from published component guides, not from a filing, so they
carry what those guides carry: the part, the country, and how firm the link to
a humanoid actually is. No listing or founding data is asserted for them —
where the source did not supply it, the field stays empty rather than being
filled from memory.

EVIDENCE, strongest first, following the classification the Black Scarab guide
publishes:
    integration  a named platform is documented as using this part
    partnership  both parties have disclosed the relationship
    commercial   sells a product built for this use, no specific platform named
    capacity     named as a capacity holder in the category

Country is taken from the source. Where two sources disagree, the field is left
empty and the row is flagged, the same way the Chinese index rows are handled.
"""

# name, category, country, note, evidence
GLOBAL = [
# ---- Transmission: reducers -------------------------------------------------
["Harmonic Drive Systems", "Reducers", "Japan",
 "Strain wave reducers. Above 50% of the world market in the gear that makes a compact joint possible.", "capacity"],
["Harmonic Drive LLC", "Reducers", "United States",
 "CSG lightweight component sets and precision servo actuators; the US arm of the same technology.", "commercial"],
["Nabtesco", "Reducers", "Japan",
 "RV and cycloidal precision reduction gears, the heavy-load alternative to strain wave.", "capacity"],
["Sumitomo Drive Technologies", "Reducers", "Japan", "Cycloidal reducers.", "commercial"],
["Spinea", "Reducers", "Slovakia", "Cycloidal reducers.", "commercial"],
["Neugart", "Reducers", "Germany", "Planetary gearheads.", "commercial"],
["Wittenstein", "Reducers", "Germany", "Planetary gearheads and servo actuators.", "commercial"],
["Nidec", "Reducers", "Japan", "Planetary gearheads, motors and fans across the same bill of materials.", "commercial"],
["Schaeffler", "Reducers", "Germany",
 "Strain wave actuators codeveloped with NEURA Robotics, UK-based Humanoid and Leju Robotics — three humanoid partnerships in five months. Also supplies bearings and force/torque sensing.", "partnership"],
# ---- Transmission: bearings, screws, brakes ---------------------------------
["THK", "Bearings", "Japan", "Crossed roller bearings and linear motion; Unitree confirms the type but not the vendor.", "commercial"],
["SKF", "Bearings", "Sweden", "Crossed roller and precision bearings.", "commercial"],
["NSK", "Bearings", "Japan", "Crossed roller and precision bearings.", "commercial"],
["IKO", "Bearings", "Japan", "Crossed roller bearings.", "commercial"],
["Rollvis", "Screws", "Switzerland",
 "Planetary roller screws. The reference price the Chinese entrants are measured against — roughly double.", "commercial"],
["Ewellix", "Screws", "Sweden", "Ball and roller screws, linear actuators.", "commercial"],
["Bosch Rexroth", "Screws", "Germany", "Ball and roller screws at industrial scale.", "commercial"],
["HIWIN", "Screws", "Taiwan", "Ball screws and linear motion.", "commercial"],
["mayr", "Brakes", "Germany", "Holding brakes — what keeps a joint where it is when power stops.", "commercial"],
["Kendrion", "Brakes", "Netherlands", "Holding brakes.", "commercial"],
["Miki Pulley", "Brakes", "Japan", "Holding brakes and couplings.", "commercial"],
# ---- Actuation: modules, motors, drives -------------------------------------
["maxon", "Actuators", "Switzerland",
 "Frameless and brushless motors with matched gearheads; documented in Pollen's Reachy 2.", "integration"],
["FAULHABER", "Motors", "Germany",
 "DC, BLDC, linear and stepper motors; the SXR family is built for robotic hands.", "commercial"],
["Kollmorgen", "Motors", "United States", "Frameless torque motors and integrated actuators.", "commercial"],
["Moog", "Actuators", "United States", "Integrated actuator modules.", "commercial"],
["TQ RoboDrive", "Actuators", "Germany", "Frameless motors and integrated actuator modules.", "commercial"],
["Synapticon", "Drives & Control", "Germany", "Integrated actuators and servo drives with safety functions.", "commercial"],
["Hyundai Mobis", "Actuators", "South Korea",
 "Cited as the first proof point that a car Tier 1 can take the humanoid actuator module.", "commercial"],
["Elmo Motion Control", "Drives & Control", "Israel", "Compact servo drives.", "commercial"],
["Copley Controls", "Drives & Control", "United States", "Servo drives.", "commercial"],
["Infineon", "Drives & Control", "Germany", "Motor control and power silicon, current sensing, BMS.", "commercial"],
["STMicroelectronics", "Drives & Control", "Switzerland", "Motor control MCUs and power silicon.", "commercial"],
["Texas Instruments", "Drives & Control", "United States", "Motor drivers, current sensing and BMS silicon.", "commercial"],
["Renesas", "Drives & Control", "Japan", "Real-time MCUs for joint control.", "commercial"],
["NXP", "Drives & Control", "Netherlands", "Real-time MCUs and current sensing.", "commercial"],
# ---- Actuation: the magnet, which is the constraint --------------------------
["JL MAG Rare-Earth", "Magnets", "China",
 "Sintered NdFeB. Set up a humanoid magnetic component business unit in early 2025.", "commercial"],
["Ningbo Yunsheng", "Magnets", "China",
 "Sintered NdFeB. Supply to AGI Bot has entered mass production.", "integration"],
["Zhenghai Magnetic Material", "Magnets", "China", "High-performance sintered NdFeB.", "commercial"],
["Zhong Ke San Huan", "Magnets", "China",
 "One of the three highest-volume sintered NdFeB producers.", "capacity"],
["Proterial", "Magnets", "Japan",
 "High-performance NdFeB, formerly Hitachi Metals. The main non-Chinese volume.", "capacity"],
["Shin-Etsu Chemical", "Magnets", "Japan", "High-performance NdFeB.", "capacity"],
["TDK", "Magnets", "Japan", "NdFeB magnets; also IMUs through InvenSense.", "capacity"],
["VAC", "Magnets", "Germany", "Vacuumschmelze — the European NdFeB producer.", "capacity"],
# ---- Sensing: position feedback ---------------------------------------------
["HEIDENHAIN", "Encoders", "Germany",
 "Rotary and inductive encoders built into joints — KCI 120, ECI 119, ECA 4000.", "commercial"],
["Renishaw / RLS", "Encoders", "United Kingdom",
 "AksIM absolute magnetic and Orbis rotary encoders; documented in PAL's REEM-C.", "integration"],
["Balluff", "Encoders", "Germany", "Incremental and absolute encoders.", "commercial"],
["ams OSRAM", "Encoders", "Austria", "Magnetic position sensor ICs.", "commercial"],
["Celera Motion", "Encoders", "United States", "Optical encoders for compact joints.", "commercial"],
["Netzer", "Encoders", "Israel", "Electric encoders, hollow-shaft and frameless.", "commercial"],
# ---- Sensing: force, touch, sight, motion -----------------------------------
["ATI Industrial Automation", "Sensors", "United States", "Six-axis force/torque sensors.", "commercial"],
["Bota Systems", "Sensors", "Switzerland", "Compact six-axis force/torque sensors.", "commercial"],
["Resense", "Sensors", "Switzerland", "Miniature six-axis force/torque sensors.", "commercial"],
["GelSight", "Sensors", "United States", "Optical elastomer tactile imaging — touch read as a picture.", "commercial"],
["XELA Robotics", "Sensors", "",
 "uSkin three-axis tactile arrays.", "commercial", "Country disagrees across sources: Japan in one guide, Germany in another"],
["Pressure Profile Systems", "Sensors", "United States", "RoboTact and Digitacts embedded force sensing.", "commercial"],
["Tekscan", "Sensors", "United States", "Tactile pressure arrays.", "commercial"],
["SynTouch", "Sensors", "United States", "Tactile sensing for robotics and prosthetics.", "commercial"],
["Sony Semiconductor", "Sensors", "Japan", "Image sensors.", "commercial"],
["onsemi", "Sensors", "United States", "Image sensors.", "commercial"],
["OmniVision", "Sensors", "United States", "Image sensors.", "commercial"],
["Intel RealSense", "Sensors", "United States",
 "Depth cameras; D435i in the head and D405 at the wrist are documented on Unitree G1.", "integration"],
["Stereolabs", "Sensors", "United States", "Stereo depth cameras.", "commercial"],
["Luxonis", "Sensors", "United States", "Embedded depth and vision modules.", "commercial"],
["Basler", "Sensors", "Germany", "Industrial cameras.", "commercial"],
["IDS Imaging", "Sensors", "Germany", "Industrial cameras.", "commercial"],
["Ouster", "Sensors", "United States", "Lidar; relationship with Field AI confirmed.", "partnership"],
["Livox", "Sensors", "China", "Lidar; MID-360 documented on Unitree G1.", "integration"],
["Hesai", "Sensors", "China", "Lidar.", "commercial"],
["RoboSense", "Sensors", "China", "Lidar.", "commercial"],
["Bosch Sensortec", "Sensors", "Germany", "IMUs.", "commercial"],
["TDK InvenSense", "Sensors", "Japan", "IMUs.", "commercial"],
["Analog Devices", "Sensors", "United States", "IMUs, current sensing, multimodal tactile in prototype.", "commercial"],
["Knowles", "Sensors", "United States", "MEMS microphones.", "commercial"],
# ---- Manipulation ------------------------------------------------------------
["Shadow Robot", "Hand Units", "United Kingdom",
 "Tendon-driven dexterous hands with tactile options; also custom tactile sensing.", "commercial"],
["SCHUNK", "Hand Units", "Germany", "SVH five-finger hand and grippers.", "commercial"],
["Wonik Robotics", "Hand Units", "South Korea", "Allegro Hand, the research standard.", "commercial"],
["qb robotics", "Hand Units", "Italy", "SoftHand underactuated gripping.", "commercial"],
["Inspire Robots", "Hand Units", "",
 "Dexterous hand offered as an option on PAL's Kangaroo.",
 "integration", "Country disagrees across sources"],
["Seed Robotics", "Hand Units", "",
 "Dexterous hand offered as an option on PAL's Kangaroo.",
 "integration", "Country disagrees across sources"],
["Tesollo", "Hand Units", "",
 "DG-5F five-finger hand.", "commercial", "Country disagrees across sources"],
["Vibram", "Materials", "Italy", "Soles; partnership with Agility Robotics confirmed.", "partnership"],
# ---- Compute and power --------------------------------------------------------
["NVIDIA", "Compute", "United States",
 "Jetson Thor, up to 2,070 sparse FP4 TFLOPS and 128 GB. Confirmed on Boston Dynamics, Agility, Figure, 1X and Unitree H2.", "integration"],
["Qualcomm", "Compute", "United States", "Edge AI compute.", "commercial"],
["AMD", "Compute", "United States", "Edge AI compute.", "commercial"],
["Intel", "Compute", "United States", "Compute; an option on Unitree and Fourier platforms.", "commercial"],
["LG Energy Solution", "Power & Battery", "South Korea", "Cells.", "commercial"],
["Samsung SDI", "Power & Battery", "South Korea",
 "Cells; partnership with Hyundai and Kia's robotics lab confirmed.", "partnership"],
["Molicel", "Power & Battery", "Taiwan", "High-rate cells; claims P50B in humanoid use.", "commercial"],
["Panasonic Energy", "Power & Battery", "Japan", "Cells.", "commercial"],
["EVE Energy", "Power & Battery", "China", "Cells.", "commercial"],
["Vicor", "Power & Battery", "United States", "DC-DC conversion modules.", "commercial"],
["Sensata", "Power & Battery", "United States", "Contactors and current sensing.", "commercial"],
["Littelfuse", "Power & Battery", "United States", "Fusing and circuit protection.", "commercial"],
# ---- Structure, interconnect, thermal, safety, assembly -----------------------
["BASF", "Materials", "Germany",
 "Engineering polymers and elastomers; partnership on Fourier's GR-2 confirmed.", "partnership"],
["Covestro", "Materials", "Germany", "Polycarbonate blends, TPU, thermally conductive polymers.", "commercial"],
["Celanese", "Materials", "United States", "Engineering polymers.", "commercial"],
["Henkel", "Materials", "Germany", "Structural adhesives and thermal interface materials.", "commercial"],
["3M", "Materials", "United States", "Adhesives, tapes and thermal interface materials.", "commercial"],
["Bossard", "Materials", "Switzerland", "High-strength fasteners and inserts.", "commercial"],
["Böllhoff", "Materials", "Germany", "Fasteners and inserts.", "commercial"],
["Trelleborg", "Materials", "Sweden", "Elastomers and seals.", "commercial"],
["Molex", "Interconnect", "United States", "Connectors and harness.", "commercial"],
["TE Connectivity", "Interconnect", "United States", "Connectors, harness and contactors.", "commercial"],
["Amphenol", "Interconnect", "United States", "Connectors.", "commercial"],
["Hirose", "Interconnect", "Japan", "Miniature connectors.", "commercial"],
["Samtec", "Interconnect", "United States", "Board-to-board and cable assemblies.", "commercial"],
["LEMO", "Interconnect", "Switzerland", "Push-pull circular connectors.", "commercial"],
["igus", "Interconnect", "Germany", "Cable carriers and continuous-flex cable.", "commercial"],
["LAPP", "Interconnect", "Germany", "Continuous-flex cable and harness.", "commercial"],
["Boyd", "Thermal", "United States", "Cold plates, heat pipes and vapour chambers.", "commercial"],
["ebm-papst", "Thermal", "Germany", "Fans and blowers.", "commercial"],
["Sunon", "Thermal", "Taiwan", "Fans and blowers.", "commercial"],
["Delta Electronics", "Thermal", "Taiwan", "Fans, blowers and power conversion.", "commercial"],
["Asia Vital Components", "Thermal", "Taiwan", "Heat pipes and vapour chambers.", "commercial"],
["Parker Chomerics", "Thermal", "United States", "Thermal interface materials and cold plates.", "commercial"],
["Pilz", "Drives & Control", "Germany", "Functional safety control.", "commercial"],
["Beckhoff", "Drives & Control", "Germany", "TwinSAFE functional safety and EtherCAT control.", "commercial"],
["SICK", "Sensors", "Germany", "Safety sensing.", "commercial"],
["Jabil", "Assemblies", "United States",
 "Contract manufacturing for Figure and Apptronik.", "integration"],
]

# Which subsystem each part category belongs to, so the index can be read as a
# bill of materials rather than as a flat list of chips.
GROUP = {
    "Actuators": "Actuation", "Motors": "Actuation", "Magnets": "Actuation",
    "Drives & Control": "Actuation",
    "Reducers": "Transmission", "Screws": "Transmission", "Bearings": "Transmission",
    "Brakes": "Transmission",
    "Sensors": "Sensing", "Encoders": "Sensing",
    "Hand Units": "Manipulation",
    "Compute": "Compute & Power", "PCBs & Logic": "Compute & Power",
    "Power & Battery": "Compute & Power", "Intelligence": "Compute & Power",
    "Materials": "Structure", "Castings": "Structure", "Assemblies": "Structure",
    "Interconnect": "Structure", "Thermal": "Structure",
    "Other Components": "Structure", "Periphery": "Structure", "Data": "Structure",
}

EVIDENCE = {
    "integration": "Documented on a named platform",
    "partnership": "Partnership both sides have disclosed",
    "commercial": "Sells for this use, no platform named",
    "capacity": "Named as a capacity holder",
}


def rows():
    """The global rows in the same shape the Chinese index rows use."""
    out = []
    for r in GLOBAL:
        name, cat, country, note, ev = r[:5]
        flag = r[5] if len(r) > 5 else None
        out.append({
            "en": name, "cn": "", "cat": cat, "co": country or "—", "city": "",
            "yr": "", "stk": "", "cu": [], "note": note, "ev": ev,
            **({"flag": flag} if flag else {}),
        })
    return out
