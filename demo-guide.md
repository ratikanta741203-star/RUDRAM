# RUDRAM Hackathon Demonstration Guide (5–10 Minutes Script)

Follow this structured presentation flow during jury evaluation:

---

## 1. Opening: Vision & Command Center (1 min)
1. Open **`/dashboard/`**.
2. Point out the **Common Operating Picture (COP)**: Active Disasters, AI Risk Score (84%), Exposed Population (18,400), and available high-ground shelters.
3. Click the **"⚡ START FLOOD DEMO"** button to simulate heavy monsoon rainfall and trigger real-time telemetry updates.

---

## 2. AI Risk Prediction & SHAP Breakdown (2 mins)
1. Navigate to **`/risk/`**.
2. Click **"Fill Monsoon Preset"** and press **"RUN XGBOOST & RANDOM FOREST INFERENCE"**.
3. Showcase the **Explainable Contributing Factors Table**: Show how 24h rainfall volume (186.4mm) and low elevation (14.0m) drive the CRITICAL 84.5% flood probability.

---

## 3. GIS Multi-Hazard Studio & Shelters (2 mins)
1. Open **`/map/`** to display the 21 togglable vector layers (Inundation polygons, Kuakhai River, Bridges, Hospitals, FIRMS Fire Hotspots).
2. Go to **`/shelters/`** and click **"FIND BEST SHELTER FOR MY LOCATION"**.
3. Highlight the multi-criteria spatial algorithm ranking **BJB Autonomous College Shelter** #1 due to high elevation and on-site ICU.

---

## 4. Safe Evacuation Routing (1.5 mins)
1. Open **`/evacuation/`**.
2. Click **"CALCULATE SAFE EVACUATION PATHS"**.
3. Show the comparison:
   - **Route A**: 4.8 km (12 min) — *Hazardous (42% Safety)* due to Daya canal submerged culvert.
   - **Route B**: 6.2 km (16 min) — *RECOMMENDED (94% Safety)* via elevated Janpath Ridge.

---

## 5. Satellite Analysis Lab & Copilot (2 mins)
1. Navigate to **`/satellite/`**.
2. Click **"ANALYZE DAMAGE"** and watch the 5-step non-freezing Sentinel-1 SAR workflow complete.
3. Drag the **Before / After Split Viewer Slider** to visually demonstrate pre-flood dry land vs. active radar flood extent.
4. Navigate to **`/assistant/`** and ask a question in the AI Copilot console.

---

## 6. Official Situation Report Export (30 secs)
1. Go to **`/reports/`** and click **"GENERATE & DOWNLOAD OFFICIAL SITUATION REPORT (PDF)"**.
2. Show the generated ReportLab PDF briefing document with full incident statistics and AI response directives.
