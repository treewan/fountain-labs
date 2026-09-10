#!/usr/bin/env python3
"""Makers the robolist board cannot see.

That board only lists a company once one of its robots is indexed, and only
under the category the robot sits in. Three things fall through: companies with
a stub page and no model on file, companies filed under another category, and
companies it does not carry at all. The effect is systematic rather than random
— it is the newest and best-funded Western startups that are missing, which is
exactly the half an investor is looking for.

These rows are hand-assembled from funding coverage, September 2026. Every
figure here was read off a report rather than recalled, and every website was
fetched and checked against the company's own page — sunday.xyz, the obvious
guess for Sunday Robotics, turned out to be a parked domain for sale. Where a
site could not be reached and confirmed from here, the field is left empty
rather than guessed.

Two companies that would otherwise belong are deliberately absent: Cartwheel
Robotics shut down in May 2026 and K-Scale Labs in November 2025. A company
that no longer exists does not buy parts.
"""

# name, country, HQ, founded, website, raised, what they build, why robolist misses it
EXTRA = [
["Sunday Robotics", "United States", "Mountain View, United States", "2024", "https://www.sunday.ai",
 "$200M",
 "Memo, a wheeled home robot that learns household chores from demonstration. $35M Series A in November 2025, then $165M in March 2026 at a $1.15B valuation.",
 "stub"],
["Skild AI", "United States", "Pittsburgh, United States", "2023", "https://www.skild.ai",
 "$2B+",
 "Skild Brain, a single foundation model meant to control any robot without retraining. $1.4B Series C in January 2026 at over $14B.",
 "stub"],
["Generalist AI", "United States", "San Mateo, United States", "2024", "https://generalistai.com",
 "~$600M",
 "GEN-0 and GEN-1, robot foundation models; the first to show scaling laws hold in the physical domain. $3B valuation as of August 2026.",
 "category"],
["DYNA Robotics", "United States", "Redwood City, United States", "2024", "https://www.dyna.co",
 "$143.5M",
 "DYNA-1: two industrial arms on a wheeled base, running sixteen-hour days in hotels, restaurants and laundromats.",
 "absent"],
["Persona AI", "United States", "Houston, United States", "2024", "https://personainc.ai",
 "$42M",
 "Humanoid welders for shipyards. MOU with HD Korea Shipbuilding and HD Hyundai Robotics; prototypes due end of 2026.",
 "absent"],
["Foundation", "United States", "San Francisco, United States", "2024", "https://foundation.bot",
 "$24M in contracts",
 "Phantom MK1 for industrial and defence work. The figure is US Army, Navy and Air Force research contracts, not a venture round.",
 "absent"],
["Clone Robotics", "Poland", "Warsaw, Poland", "2021", "https://clonerobotics.com",
 "~$17M",
 "Protoclone V1, a synthetic-muscle android with more than 200 degrees of freedom and 500 sensors.",
 "absent"],
["Collaborative Robotics", "United States", "Santa Clara, United States", "2022", "https://www.co.bot",
 "$150M+",
 "Proxie, a mobile manipulator, from the team that scaled Amazon Robotics past 500,000 units.",
 "absent"],
["Reflex Robotics", "United States", "New York, United States", "", "https://www.reflexrobotics.com",
 "$7M",
 "A wheeled humanoid for repetitive manual work, with a remote operator taking over the hard parts.",
 "absent"],
["Nimble Robotics", "United States", "San Francisco, United States", "2017", "https://nimble.ai",
 "$221M",
 "Autonomous fulfilment. $106M Series C at a $1B valuation, led by FedEx alongside a commercial agreement.",
 "absent"],
["Prosper Robotics", "United Kingdom", "London, United Kingdom", "2021", "",
 "",
 "Alfie, a teleoperated home robot. Angel money and the founder's own capital; no institutional round disclosed and nothing sold commercially yet.",
 "absent"],
["Astribot", "China", "Shenzhen, China", "2022", "https://www.astribot.com",
 "~$140M",
 "S1 and the cable-driven T1 at about $13,000. Founding team came out of Tencent's Robotics X lab. 2026 raises past ¥1B at a valuation above ¥10B.",
 "absent"],
]

WHY = {
    "stub": "On robolist with no model indexed",
    "category": "On robolist under another category",
    "absent": "Not on robolist",
}


def rows():
    out = []
    for name, country, hq, founded, web, raised, desc, why in EXTRA:
        row = {"n": name, "c": country, "s": 0, "r": 0, "d": desc, "src": why}
        if hq:
            row["hq"] = hq
        if founded:
            row["f"] = founded
        if web:
            row["w"] = web
        if raised:
            row["cap"] = raised
        out.append(row)
    return out
