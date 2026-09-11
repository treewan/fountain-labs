#!/usr/bin/env python3
"""Companies from the FOUNTAIN China supply chain survey, 11-25 September 2026.

These are on the itinerary, not in either published source, and the reason is
consistent: almost all of them are unlisted. The Chinese half of the index is a
list of listed companies, so an unlisted Tier-2 cannot appear in it however
central it is. Two are robot makers rather than component suppliers and are
added to that layer instead.

Category and city are read off the itinerary's own visit themes and routing.
Nothing else is asserted — no ticker, no founding year, no headcount — because
the trip has not happened yet. The rows carry the visit date so they can be
filled in from what the visits actually find.
"""

# name, Chinese name, category, city, what the visit is for, visit date
SURVEY = [
["Hypersen", "海伯森", "Sensors", "Shenzhen",
 "Six-axis force/torque sensing, actuator design and hand transmission.", "2026-09-15"],
["Quanzhibo", "泉智博", "Other Components", "Dongguan",
 "Category not yet established; visited in place of Luxshare to assess product fit and manufacturing readiness.",
 "2026-09-16"],
["QiTeng RoboSkin", "启腾", "Sensors", "Dongguan",
 "Robot outer skin.", "2026-09-16"],
["Daimon", "戴盟", "Hand Units", "Shenzhen",
 "Tactile manipulation and dexterous hands.", "2026-09-16"],
["Topband Battery", "拓邦锂电", "Power & Battery", "Shenzhen",
 "Robot battery stack: pack and BMS capability, safety validation.", "2026-09-17"],
["Wuji Hands", "舞肌科技", "Hand Units", "Shenzhen",
 "Dexterous hand mechanics, control and integration path.", "2026-09-17"],
["ENCOS", "", "Actuators", "Nanjing",
 "Integrated actuator engineering: customisation, life tests, cost/volume curve.", "2026-09-19"],
["Kunwei", "坤维传感", "Sensors", "Suzhou",
 "Force/torque sensing, calibration data, and a contract-manufacturing NPI plan.", "2026-09-20"],
]

# Robot makers on the same trip. They belong to the demand side, not the index:
# the visits benchmark their architecture, not their parts.
SURVEY_MAKERS = [
["Hexfellow", "China", "Guangzhou, China",
 "Robot OEM. Visited to benchmark industrialisation and go through its BOM, make-buy split and partnership fit.",
 "2026-09-14"],
["Flexiv", "China", "Shanghai, China",
 "Adaptive robots built around force control. Visited to compare its force-control stack against the humanoid programmes.",
 "2026-09-18"],
]


def rows():
    """Survey rows in the shape the index uses."""
    out = []
    for en, cn, cat, city, note, when in SURVEY:
        out.append({
            "en": en, "cn": cn, "cat": cat, "co": "China", "city": city,
            "yr": "", "stk": "", "cu": [], "note": note,
            "ev": "survey", "seen": when,
        })
    return out
