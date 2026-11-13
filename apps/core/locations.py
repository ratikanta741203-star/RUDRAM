"""
Indian States, Union Territories, and Major Meteorological & Disaster Monitoring Hubs.
"""

INDIAN_STATES_DATA = [
    {"name": "Andhra Pradesh", "code": "AP", "capital": "Amaravati", "lat": 16.5062, "lon": 80.6480, "zoom": 7},
    {"name": "Arunachal Pradesh", "code": "AR", "capital": "Itanagar", "lat": 27.0844, "lon": 93.6053, "zoom": 7},
    {"name": "Assam", "code": "AS", "capital": "Dispur", "lat": 26.1445, "lon": 91.7362, "zoom": 7},
    {"name": "Bihar", "code": "BR", "capital": "Patna", "lat": 25.5941, "lon": 85.1376, "zoom": 7},
    {"name": "Chhattisgarh", "code": "CG", "capital": "Raipur", "lat": 21.2514, "lon": 81.6296, "zoom": 7},
    {"name": "Goa", "code": "GA", "capital": "Panaji", "lat": 15.4909, "lon": 73.8278, "zoom": 9},
    {"name": "Gujarat", "code": "GJ", "capital": "Gandhinagar", "lat": 23.2156, "lon": 72.6369, "zoom": 7},
    {"name": "Haryana", "code": "HR", "capital": "Chandigarh", "lat": 30.7333, "lon": 76.7794, "zoom": 8},
    {"name": "Himachal Pradesh", "code": "HP", "capital": "Shimla", "lat": 31.1048, "lon": 77.1734, "zoom": 7},
    {"name": "Jharkhand", "code": "JH", "capital": "Ranchi", "lat": 23.3441, "lon": 85.3096, "zoom": 7},
    {"name": "Karnataka", "code": "KA", "capital": "Bengaluru", "lat": 12.9716, "lon": 77.5946, "zoom": 7},
    {"name": "Kerala", "code": "KL", "capital": "Thiruvananthapuram", "lat": 8.5241, "lon": 76.9366, "zoom": 7},
    {"name": "Madhya Pradesh", "code": "MP", "capital": "Bhopal", "lat": 23.2599, "lon": 77.4126, "zoom": 6},
    {"name": "Maharashtra", "code": "MH", "capital": "Mumbai", "lat": 19.0760, "lon": 72.8777, "zoom": 6},
    {"name": "Manipur", "code": "MN", "capital": "Imphal", "lat": 24.8170, "lon": 93.9368, "zoom": 8},
    {"name": "Meghalaya", "code": "ML", "capital": "Shillong", "lat": 25.5788, "lon": 91.8933, "zoom": 8},
    {"name": "Mizoram", "code": "MZ", "capital": "Aizawl", "lat": 23.7271, "lon": 92.7176, "zoom": 8},
    {"name": "Nagaland", "code": "NL", "capital": "Kohima", "lat": 25.6751, "lon": 94.1086, "zoom": 8},
    {"name": "Odisha", "code": "OD", "capital": "Bhubaneswar", "lat": 20.2961, "lon": 85.8245, "zoom": 7},
    {"name": "Punjab", "code": "PB", "capital": "Chandigarh", "lat": 30.7333, "lon": 76.7794, "zoom": 7},
    {"name": "Rajasthan", "code": "RJ", "capital": "Jaipur", "lat": 26.9124, "lon": 75.7873, "zoom": 6},
    {"name": "Sikkim", "code": "SK", "capital": "Gangtok", "lat": 27.3389, "lon": 88.6065, "zoom": 9},
    {"name": "Tamil Nadu", "code": "TN", "capital": "Chennai", "lat": 13.0827, "lon": 80.2707, "zoom": 7},
    {"name": "Telangana", "code": "TS", "capital": "Hyderabad", "lat": 17.3850, "lon": 78.4867, "zoom": 7},
    {"name": "Tripura", "code": "TR", "capital": "Agartala", "lat": 23.8315, "lon": 91.2868, "zoom": 8},
    {"name": "Uttar Pradesh", "code": "UP", "capital": "Lucknow", "lat": 26.8467, "lon": 80.9462, "zoom": 6},
    {"name": "Uttarakhand", "code": "UK", "capital": "Dehradun", "lat": 30.3165, "lon": 78.0322, "zoom": 7},
    {"name": "West Bengal", "code": "WB", "capital": "Kolkata", "lat": 22.5726, "lon": 88.3639, "zoom": 7},
    # Union Territories
    {"name": "Andaman and Nicobar Islands", "code": "AN", "capital": "Port Blair", "lat": 11.6234, "lon": 92.7265, "zoom": 7},
    {"name": "Chandigarh", "code": "CH", "capital": "Chandigarh", "lat": 30.7333, "lon": 76.7794, "zoom": 11},
    {"name": "Dadra and Nagar Haveli and Daman and Diu", "code": "DN", "capital": "Daman", "lat": 20.4283, "lon": 72.8397, "zoom": 10},
    {"name": "Delhi", "code": "DL", "capital": "New Delhi", "lat": 28.6139, "lon": 77.2090, "zoom": 10},
    {"name": "Jammu and Kashmir", "code": "JK", "capital": "Srinagar", "lat": 34.0837, "lon": 74.7973, "zoom": 7},
    {"name": "Ladakh", "code": "LA", "capital": "Leh", "lat": 34.1526, "lon": 77.5771, "zoom": 7},
    {"name": "Lakshadweep", "code": "LD", "capital": "Kavaratti", "lat": 10.5667, "lon": 72.6417, "zoom": 9},
    {"name": "Puducherry", "code": "PY", "capital": "Puducherry", "lat": 11.9416, "lon": 79.8083, "zoom": 10},
]

ALL_INDIA_HUBS = [
    {"city": "New Delhi", "state": "Delhi", "lat": 28.6139, "lon": 77.2090, "risk": "MODERATE", "hazard": "Urban Flash Flood Watch"},
    {"city": "Mumbai", "state": "Maharashtra", "lat": 19.0760, "lon": 72.8777, "risk": "HIGH", "hazard": "Coastal High Tide Inundation"},
    {"city": "Kolkata", "state": "West Bengal", "lat": 22.5726, "lon": 88.3639, "risk": "HIGH", "hazard": "Hooghly Basin Storm Surge"},
    {"city": "Chennai", "state": "Tamil Nadu", "lat": 13.0827, "lon": 80.2707, "risk": "MODERATE", "hazard": "Bay of Bengal Depressions"},
    {"city": "Bengaluru", "state": "Karnataka", "lat": 12.9716, "lon": 77.5946, "risk": "LOW", "hazard": "Nominal Rain Runoff"},
    {"city": "Hyderabad", "state": "Telangana", "lat": 17.3850, "lon": 78.4867, "risk": "MODERATE", "hazard": "Musi Basin Overflow"},
    {"city": "Ahmedabad", "state": "Gujarat", "lat": 23.0225, "lon": 72.5714, "risk": "LOW", "hazard": "Sabarmati Level Nominal"},
    {"city": "Guwahati", "state": "Assam", "lat": 26.1445, "lon": 91.7362, "risk": "CRITICAL", "hazard": "Brahmaputra Flood Wave Alert"},
    {"city": "Bhubaneswar", "state": "Odisha", "lat": 20.2961, "lon": 85.8245, "risk": "HIGH", "hazard": "Mahanadi/Daya River Swell"},
    {"city": "Patna", "state": "Bihar", "lat": 25.5941, "lon": 85.1376, "risk": "CRITICAL", "hazard": "Ganga Basin Inundation"},
    {"city": "Jaipur", "state": "Rajasthan", "lat": 26.9124, "lon": 75.7873, "risk": "LOW", "hazard": "Arid Surface Stability"},
    {"city": "Srinagar", "state": "Jammu and Kashmir", "lat": 34.0837, "lon": 74.7973, "risk": "HIGH", "hazard": "Jhelum Catchment Alert"},
    {"city": "Dehradun", "state": "Uttarakhand", "lat": 30.3165, "lon": 78.0322, "risk": "CRITICAL", "hazard": "Cloudburst & Landslide Alert"},
    {"city": "Thiruvananthapuram", "state": "Kerala", "lat": 8.5241, "lon": 76.9366, "risk": "HIGH", "hazard": "Western Ghats Flash Rain"},
    {"city": "Bhopal", "state": "Madhya Pradesh", "lat": 23.2599, "lon": 77.4126, "risk": "LOW", "hazard": "Reservoirs Within Limit"},
    {"city": "Shimla", "state": "Himachal Pradesh", "lat": 31.1048, "lon": 77.1734, "zoom": 8, "risk": "HIGH", "hazard": "Steep Slope Runoff Warning"},
]

HIGH_ALERT_LOCATIONS_DEFAULT = [
    {"name": "Guwahati (Brahmaputra Valley)", "state": "Assam", "lat": 26.1445, "lon": 91.7362, "rainfall_mm": 92.4, "wind_kmh": 31.0, "risk_level": "CRITICAL", "risk_score": 91},
    {"name": "Bhubaneswar (Daya Floodplain)", "state": "Odisha", "lat": 20.2961, "lon": 85.8245, "rainfall_mm": 48.6, "wind_kmh": 24.5, "risk_level": "HIGH", "risk_score": 84},
    {"name": "Mumbai (Mithi River Sector)", "state": "Maharashtra", "lat": 19.0760, "lon": 72.8777, "rainfall_mm": 41.2, "wind_kmh": 27.8, "risk_level": "HIGH", "risk_score": 78},
    {"name": "Dehradun (Song River Basin)", "state": "Uttarakhand", "lat": 30.3165, "lon": 78.0322, "rainfall_mm": 84.0, "wind_kmh": 18.2, "risk_level": "CRITICAL", "risk_score": 88},
    {"name": "Patna (Ganga Lowlands)", "state": "Bihar", "lat": 25.5941, "lon": 85.1376, "rainfall_mm": 56.5, "wind_kmh": 21.0, "risk_level": "CRITICAL", "risk_score": 85},
    {"name": "Wayanad (Kabini Upper Basin)", "state": "Kerala", "lat": 11.6854, "lon": 76.1320, "rainfall_mm": 64.0, "wind_kmh": 22.0, "risk_level": "HIGH", "risk_score": 76},
]

# District Geographic Coordinates per State / Union Territory
INDIAN_DISTRICTS_DATA = {
    "Odisha": [
        {"name": "Angul", "lat": 20.8400, "lon": 85.1000},
        {"name": "Balangir", "lat": 20.7100, "lon": 83.4800},
        {"name": "Balasore", "lat": 21.4934, "lon": 86.9135},
        {"name": "Bargarh", "lat": 21.3300, "lon": 83.6200},
        {"name": "Bhadrak", "lat": 21.0600, "lon": 86.5000},
        {"name": "Boudh", "lat": 20.8400, "lon": 84.3200},
        {"name": "Cuttack", "lat": 20.4625, "lon": 85.8830},
        {"name": "Deogarh", "lat": 21.5300, "lon": 84.7300},
        {"name": "Dhenkanal", "lat": 20.6600, "lon": 85.6000},
        {"name": "Gajapati", "lat": 18.8100, "lon": 84.1500},
        {"name": "Ganjam (Berhampur)", "lat": 19.3150, "lon": 84.7941},
        {"name": "Jagatsinghpur", "lat": 20.2700, "lon": 86.1700},
        {"name": "Jajpur", "lat": 20.8500, "lon": 86.3300},
        {"name": "Jharsuguda", "lat": 21.8600, "lon": 84.0300},
        {"name": "Kalahandi", "lat": 19.9000, "lon": 83.1600},
        {"name": "Kandhamal", "lat": 20.1500, "lon": 84.2200},
        {"name": "Kendrapara", "lat": 20.5000, "lon": 86.4200},
        {"name": "Keonjhar", "lat": 21.6300, "lon": 85.5800},
        {"name": "Khordha (Bhubaneswar)", "lat": 20.2961, "lon": 85.8245},
        {"name": "Koraput", "lat": 18.8100, "lon": 82.7100},
        {"name": "Malkangiri", "lat": 18.3500, "lon": 81.8800},
        {"name": "Mayurbhanj", "lat": 21.9300, "lon": 86.7200},
        {"name": "Nabarangpur", "lat": 19.2300, "lon": 82.5500},
        {"name": "Nayagarh", "lat": 20.1300, "lon": 85.1000},
        {"name": "Nuapada", "lat": 20.8300, "lon": 82.5300},
        {"name": "Puri (Konark)", "lat": 19.8135, "lon": 85.8312},
        {"name": "Rayagada", "lat": 19.1700, "lon": 83.4200},
        {"name": "Sambalpur", "lat": 21.4669, "lon": 83.9812},
        {"name": "Subarnapur", "lat": 20.8400, "lon": 83.9200},
        {"name": "Sundargarh (Rourkela)", "lat": 22.2604, "lon": 84.8536}
    ],
    "Maharashtra": [
        {"name": "Mumbai City", "lat": 18.9600, "lon": 72.8200},
        {"name": "Mumbai Suburban", "lat": 19.0760, "lon": 72.8777},
        {"name": "Thane", "lat": 19.2183, "lon": 72.9781},
        {"name": "Pune", "lat": 18.5204, "lon": 73.8567},
        {"name": "Nagpur", "lat": 21.1458, "lon": 79.0882},
        {"name": "Nashik", "lat": 19.9975, "lon": 73.7898},
        {"name": "Chhatrapati Sambhajinagar (Aurangabad)", "lat": 19.8762, "lon": 75.3433},
        {"name": "Solapur", "lat": 17.6599, "lon": 75.9064},
        {"name": "Kolhapur", "lat": 16.7050, "lon": 74.2433},
        {"name": "Amravati", "lat": 20.9374, "lon": 77.7796},
        {"name": "Nanded", "lat": 19.1383, "lon": 77.3210},
        {"name": "Sangli", "lat": 16.8524, "lon": 74.5815},
        {"name": "Satara", "lat": 17.6805, "lon": 74.0183},
        {"name": "Raigad", "lat": 18.5158, "lon": 73.1822},
        {"name": "Ratnagiri", "lat": 16.9902, "lon": 73.3120},
        {"name": "Sindhudurg", "lat": 16.1672, "lon": 73.6651}
    ],
    "West Bengal": [
        {"name": "Kolkata", "lat": 22.5726, "lon": 88.3639},
        {"name": "Howrah", "lat": 22.5958, "lon": 88.2636},
        {"name": "Hooghly", "lat": 22.9032, "lon": 88.3968},
        {"name": "North 24 Parganas", "lat": 22.7214, "lon": 88.4816},
        {"name": "South 24 Parganas", "lat": 22.1352, "lon": 88.4016},
        {"name": "Darjeeling", "lat": 27.0410, "lon": 88.2663},
        {"name": "Jalpaiguri", "lat": 26.5404, "lon": 88.7193},
        {"name": "Murshidabad", "lat": 24.1754, "lon": 88.2802},
        {"name": "Nadia", "lat": 23.4710, "lon": 88.5565},
        {"name": "Malda", "lat": 25.0108, "lon": 88.1411},
        {"name": "Paschim Medinipur", "lat": 22.4257, "lon": 87.3199},
        {"name": "Purba Medinipur", "lat": 21.9366, "lon": 87.7788}
    ],
    "Tamil Nadu": [
        {"name": "Chennai", "lat": 13.0827, "lon": 80.2707},
        {"name": "Coimbatore", "lat": 11.0168, "lon": 76.9558},
        {"name": "Madurai", "lat": 9.9252, "lon": 78.1198},
        {"name": "Tiruchirappalli", "lat": 10.7905, "lon": 78.7047},
        {"name": "Salem", "lat": 11.6643, "lon": 78.1460},
        {"name": "Tirunelveli", "lat": 8.7139, "lon": 77.7567},
        {"name": "Kanchipuram", "lat": 12.8342, "lon": 79.7036},
        {"name": "Cuddalore", "lat": 11.7480, "lon": 79.7714},
        {"name": "Kanyakumari", "lat": 8.0883, "lon": 77.5385}
    ],
    "Karnataka": [
        {"name": "Bengaluru Urban", "lat": 12.9716, "lon": 77.5946},
        {"name": "Bengaluru Rural", "lat": 13.2257, "lon": 77.5750},
        {"name": "Mysuru", "lat": 12.2958, "lon": 76.6394},
        {"name": "Dakshina Kannada (Mangaluru)", "lat": 12.9141, "lon": 74.8560},
        {"name": "Belagavi", "lat": 15.8497, "lon": 74.4977},
        {"name": "Dharwad (Hubballi)", "lat": 15.3647, "lon": 75.1240},
        {"name": "Kalaburagi", "lat": 17.3297, "lon": 76.8343},
        {"name": "Udupi", "lat": 13.3409, "lon": 74.7421},
        {"name": "Shivamogga", "lat": 13.9299, "lon": 75.5681}
    ],
    "Gujarat": [
        {"name": "Ahmedabad", "lat": 23.0225, "lon": 72.5714},
        {"name": "Surat", "lat": 21.1702, "lon": 72.8311},
        {"name": "Vadodara", "lat": 22.3072, "lon": 73.1812},
        {"name": "Rajkot", "lat": 22.3039, "lon": 70.8022},
        {"name": "Bhavnagar", "lat": 21.7645, "lon": 72.1519},
        {"name": "Jamnagar", "lat": 22.4707, "lon": 70.0577},
        {"name": "Junagadh", "lat": 21.5222, "lon": 70.4579},
        {"name": "Kachchh", "lat": 23.2420, "lon": 69.6669}
    ],
    "Uttar Pradesh": [
        {"name": "Lucknow", "lat": 26.8467, "lon": 80.9462},
        {"name": "Kanpur Nagar", "lat": 26.4499, "lon": 80.3319},
        {"name": "Varanasi", "lat": 25.3176, "lon": 82.9739},
        {"name": "Agra", "lat": 27.1767, "lon": 78.0081},
        {"name": "Prayagraj", "lat": 25.4358, "lon": 81.8463},
        {"name": "Gorakhpur", "lat": 26.7606, "lon": 83.3732},
        {"name": "Gautam Buddha Nagar (Noida)", "lat": 28.5355, "lon": 77.3910},
        {"name": "Ghaziabad", "lat": 28.6692, "lon": 77.4538},
        {"name": "Ayodhya", "lat": 26.7922, "lon": 82.1998}
    ],
    "Kerala": [
        {"name": "Thiruvananthapuram", "lat": 8.5241, "lon": 76.9366},
        {"name": "Ernakulam (Kochi)", "lat": 9.9312, "lon": 76.2673},
        {"name": "Kozhikode", "lat": 11.2588, "lon": 75.7804},
        {"name": "Wayanad", "lat": 11.6854, "lon": 76.1320},
        {"name": "Palakkad", "lat": 10.7867, "lon": 76.6548},
        {"name": "Thrissur", "lat": 10.5276, "lon": 76.2144},
        {"name": "Alappuzha", "lat": 9.4981, "lon": 76.3388},
        {"name": "Idukki", "lat": 9.8497, "lon": 76.9806}
    ],
    "Bihar": [
        {"name": "Patna", "lat": 25.5941, "lon": 85.1376},
        {"name": "Gaya", "lat": 24.7955, "lon": 85.0002},
        {"name": "Bhagalpur", "lat": 25.2425, "lon": 86.9842},
        {"name": "Muzaffarpur", "lat": 26.1209, "lon": 85.3647},
        {"name": "Purnia", "lat": 25.7771, "lon": 87.4753},
        {"name": "Darbhanga", "lat": 26.1542, "lon": 85.8918}
    ],
    "Assam": [
        {"name": "Kamrup Metropolitan (Guwahati)", "lat": 26.1445, "lon": 91.7362},
        {"name": "Dibrugarh", "lat": 27.4728, "lon": 94.9120},
        {"name": "Cachar (Silchar)", "lat": 24.8333, "lon": 92.7789},
        {"name": "Jorhat", "lat": 26.7509, "lon": 94.2037},
        {"name": "Nagaon", "lat": 26.3463, "lon": 92.6840},
        {"name": "Sonitpur (Tezpur)", "lat": 26.6338, "lon": 92.8000}
    ],
    "Delhi": [
        {"name": "Central Delhi", "lat": 28.6448, "lon": 77.2167},
        {"name": "New Delhi", "lat": 28.6139, "lon": 77.2090},
        {"name": "North Delhi", "lat": 28.7041, "lon": 77.1025},
        {"name": "South Delhi", "lat": 28.4817, "lon": 77.1873},
        {"name": "East Delhi", "lat": 28.6280, "lon": 77.2950},
        {"name": "West Delhi", "lat": 28.6667, "lon": 77.0833}
    ]
}

def get_districts_for_state(state_name_or_code: str) -> list:
    """Returns list of district objects for the given state name or code."""
    state_norm = state_name_or_code.lower().strip()
    
    for st_name, dists in INDIAN_DISTRICTS_DATA.items():
        if st_name.lower() == state_norm:
            return dists

    for st in INDIAN_STATES_DATA:
        if st['name'].lower() == state_norm or st['code'].lower() == state_norm:
            state_fullname = st['name']
            if state_fullname in INDIAN_DISTRICTS_DATA:
                return INDIAN_DISTRICTS_DATA[state_fullname]
            # Default single capital district if not explicitly detailed
            return [{"name": f"{st['capital']} ({st['name']})", "lat": st['lat'], "lon": st['lon']}]
            
    # Default fallback to Odisha districts
    return INDIAN_DISTRICTS_DATA["Odisha"]
