"""
Verified Historical Disaster Knowledge & Preparedness Dataset for RUDRAM.
Sources: OSDMA (Odisha State Disaster Management Authority), Special Relief Commissioner (SRC) Odisha, IMD, NDMA.
"""

DISASTER_KNOWLEDGE_DATA = {
    "flood": {
        "type": "flood",
        "title": "FLOOD HISTORY & SAFETY",
        "badge": "HISTORICAL & SAFETY",
        "subtitle": "Odisha River Basin Flood Dynamics & Preparedness",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d3/2008_Orissa_floods_relief_work.jpg/800px-2008_Orissa_floods_relief_work.jpg",
        "image_source": "OSDMA / Indian Air Force Relief Mission Archive",
        "image_year": "2008 Odisha Floods",
        "history": [
            {
                "event": "1982 Mahanadi Delta Severe Inundation",
                "year": 1982,
                "region": "Mahanadi, Kathajodi, and Daya River Basins (Cuttack, Puri, Kendrapara)",
                "description": "Massive breach in river embankments following unprecedented upstream discharge, inundating over 1.4 million hectares of agricultural land across coastal districts.",
                "lesson": "Established the imperative for systematic embankment reinforcement, automated river gauge monitoring, and emergency multi-purpose flood shelters."
            },
            {
                "event": "2008 State-Wide High-Inundation Event",
                "year": 2008,
                "region": "Baitarani, Subarnarekha & Mahanadi Basins (Bhadrak, Jajpur, Kendrapara, Cuttack)",
                "description": "Prolonged monsoon depression triggered simultaneous severe flooding in 19 districts, affecting over 4 million residents across 6,000 villages.",
                "lesson": "Accelerated OSDMA's multi-hazard shelter construction program and automated satellite-based flood extent mapping."
            },
            {
                "event": "2020 High-Discharge Coastal Basin Flood",
                "year": 2020,
                "region": "Bhubaneswar Lowlands, Khordha, Puri, Jagatsinghpur",
                "description": "Peak discharge exceeding 10.5 lakh cusecs at Mundali weir caused extensive backwater inundation in urban depressions and agricultural deltas.",
                "lesson": "Demonstrated the critical necessity for real-time GIS river elevation telemetry and dynamic safe evacuation route mapping."
            }
        ],
        "safety_guide": {
            "before": [
                "Prepare an emergency kit with clean water, non-perishable food, flashlights, and first-aid supplies.",
                "Identify nearby safe multi-purpose shelters and elevated evacuation routes.",
                "Keep important personal identification and land records in waterproof, sealed containers.",
                "Monitor official weather bulletins from OSDMA, IMD, and local disaster control rooms."
            ],
            "during": [
                "Evacuate immediately to designated high ground or multi-purpose flood shelters when alerted.",
                "NEVER walk, swim, or drive through moving floodwaters (15cm of moving water can knock you down).",
                "Disconnect main electrical switches and gas supply valves before evacuating lowlands.",
                "Keep emergency battery radios active for official rescue instructions and NDRF/ODRAF updates."
            ],
            "after": [
                "Do not consume flood-exposed or unboiled water; use water purification tablets.",
                "Stay clear of fallen electric wires, submerged poles, and structural walls showing cracks.",
                "Inspect home electrical wiring and gas appliances thoroughly before turning power back on.",
                "Return to low-lying residential areas only after official clearance from local authorities."
            ]
        }
    },
    "cyclone": {
        "type": "cyclone",
        "title": "CYCLONE HISTORY & SAFETY",
        "badge": "HISTORICAL & SAFETY",
        "subtitle": "Bay of Bengal Tropical Cyclone History & Emergency Protocols",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c1/Cyclone_Fani_2019-05-02_0730Z.jpg/800px-Cyclone_Fani_2019-05-02_0730Z.jpg",
        "image_source": "IMD / Special Relief Commissioner, Odisha (SRC)",
        "image_year": "2019 Very Severe Cyclonic Storm Fani",
        "history": [
            {
                "event": "1999 Odisha Super Cyclone (05B)",
                "year": 1999,
                "region": "Jagatsinghpur (Paradeep), Kendrapara, Puri, Cuttack, Khordha",
                "description": "Category 5 storm with sustained winds of 260 km/h and a 6-meter storm surge. Transformed India's disaster management paradigm.",
                "lesson": "Led directly to the landmark creation of OSDMA (India's first specialized disaster management agency) and nationwide early warning networks."
            },
            {
                "event": "2013 Very Severe Cyclonic Storm Phailin",
                "year": 2013,
                "region": "Ganjam (Gopalpur), Puri, Khordha",
                "description": "Landfall with 200 km/h winds. Zero-Casualty Mission evacuated over 1 million people into 900+ multi-purpose cyclone shelters ahead of landfall.",
                "lesson": "Recognized globally by the United Nations as a benchmark in mass evacuation efficiency and early warning dissemination."
            },
            {
                "event": "2019 Extremely Severe Cyclonic Storm Fani",
                "year": 2019,
                "region": "Puri, Bhubaneswar, Cuttack, Jagatsinghpur",
                "description": "Rare May cyclone making landfall near Puri with winds of 215 km/h, damaging power infrastructure across 14 coastal districts.",
                "lesson": "Highlighted the need for disaster-resilient subterranean power grids and automated shelter resource allocation systems."
            },
            {
                "event": "2021 Very Severe Cyclonic Storm Yaas & 2024 Severe Cyclone Dana",
                "year": 2024,
                "region": "Bhadrak, Kendrapara, Balasore, Mayurbhanj",
                "description": "Severe coastal storm surges accompanied by intense inland heavy rainfall along the northern Odisha coastline.",
                "lesson": "Reinforced coastal mangrove shelterbelt restoration and localized GIS shelter route navigation."
            }
        ],
        "safety_guide": {
            "before": [
                "Track official storm bulletins issued by IMD, Special Relief Commissioner, and OSDMA.",
                "Secure tin roofs, loose trees, external solar panels, and outdoor equipment.",
                "Store at least 3 to 5 days of drinking water, dry food provisions, and essential medicines.",
                "Fully charge mobile devices, power banks, and emergency flashlights."
            ],
            "during": [
                "Remain indoors inside a concrete structure away from glass windows and doors.",
                "If the cyclone eye passes, DO NOT go outside—winds will reverse rapidly with extreme velocity.",
                "Unplug electronic appliances to prevent damage from high-voltage electrical surges.",
                "Obey immediate evacuation orders issued by ODRAF, NDRF, and District Magistrates."
            ],
            "after": [
                "Beware of snapped high-voltage power lines, fallen trees, and loose electrical conductors.",
                "Do not drive into cyclone-damaged coastal roads or flooded underpasses.",
                "Drink only boiled or chemically chlorinated water to prevent waterborne disease outbreaks.",
                "Cooperate with local disaster management teams during relief and restoration operations."
            ]
        }
    },
    "earthquake": {
        "type": "earthquake",
        "title": "EARTHQUAKE HISTORY & SAFETY",
        "badge": "HISTORICAL & SAFETY",
        "subtitle": "Seismic Fault Fundamentals & Life-Saving Preparedness",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6f/Bhuj_earthquake_2001.jpg/800px-Bhuj_earthquake_2001.jpg",
        "image_source": "NDMA / Geological Survey of India (GSI)",
        "image_year": "2001 Bhuj Seismic Event (Indian Subcontinent Historic Benchmark)",
        "history": [
            {
                "event": "2001 Bhuj Magnitude 7.7 Earthquake",
                "year": 2001,
                "region": "Gujarat & Western Indian Subcontinent",
                "description": "Intraplate earthquake causing widespread structural collapse across western India. Landmark event for national seismic building codes.",
                "lesson": "Prompted strict national enforcement of IS 1893 seismic building regulations and formation of the National Disaster Management Authority (NDMA)."
            },
            {
                "event": "1993 Latur Magnitude 6.2 Earthquake",
                "year": 1993,
                "region": "Peninsular India Stable Continental Region",
                "description": "Shallow focus intraplate quake in peninsular shield rocks, highlighting seismic vulnerability in non-Himalayan regions.",
                "lesson": "Demonstrated the requirement for seismic hazard zone re-classification across stable peninsular landmasses."
            },
            {
                "event": "Odisha Seismic Context (Zone II & Zone III)",
                "year": 2024,
                "region": "Mahanadi Graben & Eastern Ghats Belt",
                "description": "Odisha falls predominantly under Seismic Zone II (Low Intensity) and Zone III (Moderate Intensity along Mahanadi rift faults).",
                "lesson": "Requires adherence to disaster-resilient building standards for all major public infrastructure and multi-story shelters."
            }
        ],
        "safety_guide": {
            "before": [
                "Fasten heavy furniture, water heaters, and wall-hung objects securely to structural studs.",
                "Identify safe interior places in every room (under sturdy tables, against interior load-bearing walls).",
                "Keep emergency supply kits accessible near main house exit doors.",
                "Conduct regular DROP, COVER, and HOLD ON drills with family members."
            ],
            "during": [
                "DROP to your hands and knees immediately to prevent being knocked down.",
                "COVER your head and neck under a heavy desk or table. If no table is nearby, cover head near an interior wall.",
                "HOLD ON to your shelter until shaking stops completely.",
                "If outdoors, move away from buildings, streetlights, utility wires, and overpasses. DO NOT use elevators."
            ],
            "after": [
                "Expect aftershocks—be prepared to Drop, Cover, and Hold On again.",
                "Inspect your immediate area for gas leaks, electrical fires, and structural cracks.",
                "Evacuate damaged structures calmly using stairwells; never use elevators post-earthquake.",
                "Tune in to official NDMA/OSDMA emergency radio broadcasts for public safety updates."
            ]
        }
    }
}
