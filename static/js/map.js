// RUDRAM Interactive Leaflet GIS Map Layer Architecture
let rudramMap = null;
let layerGroups = {};
let userLocationMarker = null;
let userLocationCircle = null;
let activeRiskZoneCircles = [];

function getResponsiveRiskRadius(riskLevel, riskScore, zoom) {
    const lvl = (riskLevel || '').toUpperCase();
    const score = parseFloat(riskScore || 0);
    const isCritical = lvl === 'CRITICAL' || score >= 80;
    const isHigh = lvl === 'HIGH' || score >= 60;

    let baseMeters = isCritical ? 4500 : (isHigh ? 3200 : 2200);

    let scale = 1.0;
    if (zoom <= 6) {
        scale = 3.8;
    } else if (zoom === 7) {
        scale = 2.8;
    } else if (zoom === 8) {
        scale = 2.0;
    } else if (zoom === 9) {
        scale = 1.5;
    } else if (zoom === 10) {
        scale = 1.2;
    } else if (zoom === 11) {
        scale = 1.0;
    } else if (zoom === 12) {
        scale = 0.75;
    } else if (zoom === 13) {
        scale = 0.50;
    } else if (zoom === 14) {
        scale = 0.35;
    } else if (zoom >= 15) {
        scale = 0.22;
    }

    return baseMeters * scale;
}

function updateAllRiskZoneRadii() {
    if (!rudramMap || !activeRiskZoneCircles || !activeRiskZoneCircles.length) return;
    const currentZoom = rudramMap.getZoom();
    activeRiskZoneCircles.forEach(item => {
        if (item && item.circle && item.level !== undefined) {
            const newRadius = getResponsiveRiskRadius(item.level, item.score, currentZoom);
            item.circle.setRadius(newRadius);
        }
    });
}

let gStreetTiles = null;
let gDarkTiles = null;
let gSatTiles = null;
let currentTileMode = 'LIGHT';
let activeBaseTile = null;

function initRudramGISMap(containerId = 'gisMap', centerLat = 20.2961, centerLon = 85.8245, zoom = 12) {
    const mapElement = document.getElementById(containerId);
    if (!mapElement) return null;

    // Check if map is already initialized on this container
    if (rudramMap) {
        rudramMap.remove();
        rudramMap = null;
    }

    // Initialize Leaflet Map
    rudramMap = L.map(containerId, {
        center: [centerLat, centerLon],
        zoom: zoom,
        zoomControl: true
    });

    // Custom Leaflet Panes for Strict Visual Hierarchy
    const riskPane = rudramMap.createPane('riskPane');
    riskPane.style.zIndex = 400;

    const floodPane = rudramMap.createPane('floodPane');
    floodPane.style.zIndex = 450;

    const routePane = rudramMap.createPane('routePane');
    routePane.style.zIndex = 500;

    const weatherPane = rudramMap.createPane('weatherPane');
    weatherPane.style.zIndex = 600;

    const riverPane = rudramMap.createPane('riverPane');
    riverPane.style.zIndex = 620;

    const markerPane = rudramMap.createPane('markerPane');
    markerPane.style.zIndex = 650;

    // 1. Base Tile Layers (CARTO Voyager Base Tiles with Environment Key)
    const rawCartoKey = (window.RUDRAM_CONFIG?.CARTO_BASEMAP_API_KEY || window.CARTO_BASEMAP_API_KEY || '').trim();
    const cartoApiKey = rawCartoKey.replace(/^["']|["']$/g, '').trim();
    const cartoKeyParam = cartoApiKey ? `?key=${encodeURIComponent(cartoApiKey)}` : '';

    gStreetTiles = L.tileLayer(`https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png${cartoKeyParam}`, {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, &copy; <a href="https://carto.com/attributions/">CARTO</a>',
        subdomains: 'abcd',
        maxZoom: 20
    }).addTo(rudramMap);
    activeBaseTile = gStreetTiles;
    currentTileMode = 'LIGHT';

    gDarkTiles = L.tileLayer(`https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png${cartoKeyParam}`, {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, &copy; <a href="https://carto.com/attributions/">CARTO</a>',
        subdomains: 'abcd',
        maxZoom: 19
    });

    gSatTiles = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
        attribution: 'Esri, Maxar, Earthstar Geographics',
        maxZoom: 19
    });

    // 2. Initialize Layer Groups for all layers including weather
    const layers = [
        'flood_risk', 'flood_extent', 'rainfall', 'weather', 'population',
        'vulnerable_pop', 'roads', 'hospitals', 'shelters', 'police',
        'fire_stations', 'schools', 'bridges', 'rivers', 'dams', 'canals',
        'critical_infra', 'fire_hotspots', 'satellite_sar', 'damage_detection', 'evacuation_routes'
    ];

    layers.forEach(layerKey => {
        layerGroups[layerKey] = L.layerGroup();
    });

    // Default Enabled Layers on Load
    layerGroups['weather'].addTo(rudramMap);
    layerGroups['flood_risk'].addTo(rudramMap);
    layerGroups['flood_extent'].addTo(rudramMap);
    layerGroups['shelters'].addTo(rudramMap);
    layerGroups['hospitals'].addTo(rudramMap);
    layerGroups['rivers'].addTo(rudramMap);
    layerGroups['dams'].addTo(rudramMap);
    layerGroups['bridges'].addTo(rudramMap);
    layerGroups['evacuation_routes'].addTo(rudramMap);

    // 3. Populate Spatial Features
    loadFloodPolygons();
    loadSheltersLayer();
    loadInfrastructureLayer();
    loadRiversAndDamsLayer();
    loadEvacuationRoutesLayer();
    loadFireHotspotsLayer();

    // 4. Layer Control
    const overlayMaps = {
        "⛅ Weather Telemetry": layerGroups['weather'],
        "🌊 Flood Risk Zones": layerGroups['flood_risk'],
        "🛰️ SAR Inundation Extent": layerGroups['flood_extent'],
        "🏠 Emergency Shelters": layerGroups['shelters'],
        "🏥 Hospitals & Trauma Centers": layerGroups['hospitals'],
        "🚒 Fire & Rescue Stations": layerGroups['fire_stations'],
        "👮 Police Stations": layerGroups['police'],
        "🌊 Rivers & Watercourses": layerGroups['rivers'],
        "🏗️ Dams & Reservoirs": layerGroups['dams'],
        "🌉 River Bridges": layerGroups['bridges'],
        "🔥 NASA FIRMS Fire Hotspots": layerGroups['fire_hotspots'],
        "🏃 Evacuation Safe Routes": layerGroups['evacuation_routes'],
        "👥 Exposed Population Heatmap": layerGroups['population'],
    };

    const baseMaps = {
        "☀️ Standard Streets (Light)": gStreetTiles,
        "🌙 Dark Command Center": gDarkTiles,
        "🛰️ Satellite Imagery": gSatTiles
    };

    L.control.layers(baseMaps, overlayMaps, { collapsed: false }).addTo(rudramMap);
    initMapInfoControl();
    initMapModeControl();

    // Responsive risk zone circle radius update on zoom
    rudramMap.on('zoomend', updateAllRiskZoneRadii);

    // Map container size update listener
    window.addEventListener('resize', () => {
        if (rudramMap) rudramMap.invalidateSize();
    });
    setTimeout(() => {
        if (rudramMap) rudramMap.invalidateSize();
    }, 300);

    // Opacity control listener
    const opacitySlider = document.getElementById('layerOpacitySlider');
    if (opacitySlider) {
        opacitySlider.addEventListener('input', (e) => {
            const val = parseFloat(e.target.value);
            layerGroups['flood_extent'].eachLayer(layer => {
                if (layer.setStyle) layer.setStyle({ fillOpacity: val * 0.5, opacity: val });
            });
        });
    }

    window.rudramMap = rudramMap;
    return rudramMap;
}

function resetMapView() {
    const mapObj = window.rudramMap || (typeof rudramMap !== 'undefined' ? rudramMap : null);
    if (!mapObj) return;
    if (typeof activeLocation !== 'undefined' && activeLocation.lat && activeLocation.lon) {
        mapObj.flyTo([activeLocation.lat, activeLocation.lon], activeLocation.zoom || 7, { duration: 1.2 });
    } else {
        mapObj.flyTo([20.2961, 85.8245], 7, { duration: 1.2 });
    }
}
window.resetMapView = resetMapView;

// Weather Marker Pin Icon Generator
function getWeatherIconEmoji(wcode, rain = 0) {
    if (wcode === 0 || wcode === 1) return '☀️';
    if (wcode === 2 || wcode === 3) return '☁️';
    if (wcode >= 45 && wcode <= 48) return '🌫️';
    if (wcode >= 51 && wcode <= 57) return '🌦️';
    if (wcode >= 61 && wcode <= 67) return '🌧️';
    if (wcode >= 71 && wcode <= 77) return '❄️';
    if (wcode >= 80 && wcode <= 82) return '🌦️';
    if (wcode >= 85 && wcode <= 86) return '🌨️';
    if (wcode >= 95 && wcode <= 99) return '⛈️';
    if (rain > 5) return '🌧️';
    return '⛅';
}

function renderWeatherMarkersOnMap(locations) {
    if (!layerGroups['weather']) return;
    layerGroups['weather'].clearLayers();

    const isLive = true;

    locations.forEach(loc => {
        const isAvail = loc.is_available !== false;
        const emoji = isAvail ? getWeatherIconEmoji(loc.weather_code || 0, loc.rainfall || 0) : '⚠️';
        const tempDisplay = isAvail && loc.temperature !== null && loc.temperature !== undefined ? `${loc.temperature}°` : '--';
        const condition = loc.condition || (isAvail ? 'Moderate Weather' : 'Live weather unavailable');
        const rainDisplay = isAvail && loc.rainfall !== null && loc.rainfall !== undefined ? `${loc.rainfall} mm/h` : 'N/A';
        const humidityDisplay = isAvail && loc.humidity !== null && loc.humidity !== undefined ? `${loc.humidity}%` : 'N/A';
        const windDisplay = isAvail && loc.wind_speed !== null && loc.wind_speed !== undefined ? `${loc.wind_speed} km/h` : 'N/A';
        const tempValDisplay = isAvail && loc.temperature !== null && loc.temperature !== undefined ? `${loc.temperature}°C` : 'N/A';
        const locName = loc.city || loc.name || 'Unknown Location';
        const isState = loc.type === 'state';

        const customIcon = L.divIcon({
            className: 'custom-weather-icon',
            html: `<div class="weather-marker-pin"><span class="weather-emoji">${emoji}</span><span class="weather-temp">${tempDisplay}</span></div>`,
            iconSize: [60, 26],
            iconAnchor: [30, 13]
        });

        const marker = L.marker([loc.lat, loc.lon], { icon: customIcon, pane: 'weatherPane' });

        const actionButton = isState
            ? `<button class="btn btn-sm btn-outline-info w-100 py-1" onclick="selectIndianState('${locName}', ${loc.lat}, ${loc.lon}, ${loc.zoom || 7}, '${loc.capital || ''}')">Explore ${locName} Districts ➔</button>`
            : `<button class="btn btn-sm btn-outline-info w-100 py-1" onclick="handleWeatherMarkerClick('${locName}', ${loc.lat}, ${loc.lon})">Analyze Telemetry ➔</button>`;

        const popupContent = `
            <div class="p-2" style="min-width: 230px;">
                <div class="d-flex align-items-center justify-content-between mb-1">
                    <h6 class="fw-bold text-info mb-0">${locName.toUpperCase()}</h6>
                    <span class="badge bg-success font-monospace" style="font-size: 0.65rem;">LIVE API</span>
                </div>
                <div class="text-white mb-2 fs-6">${emoji} <strong>${condition}</strong></div>
                <div class="small text-secondary mb-1">Temperature: <strong class="text-warning">${tempValDisplay}</strong></div>
                <div class="small text-secondary mb-1">Rainfall: <strong class="text-primary">${rainDisplay}</strong></div>
                <div class="small text-secondary mb-1">Humidity: <strong class="text-info">${humidityDisplay}</strong></div>
                <div class="small text-secondary mb-1">Wind Speed: <strong class="text-light">${windDisplay}</strong></div>
                <div class="small text-secondary mb-1">Coordinates: <strong class="text-muted">${loc.lat.toFixed(4)}° N, ${loc.lon.toFixed(4)}° E</strong></div>
                <div class="small text-secondary mb-2">Updated: <strong class="text-warning">${new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</strong></div>
                ${actionButton}
            </div>
        `;

        marker.bindPopup(popupContent);
        marker.on('click', () => {
            if (isState && window.selectIndianState) {
                window.selectIndianState(locName, loc.lat, loc.lon, loc.zoom || 7, loc.capital || '');
            } else if (window.handleWeatherMarkerClick) {
                window.handleWeatherMarkerClick(locName, loc.lat, loc.lon);
            }
        });

        layerGroups['weather'].addLayer(marker);
    });
}

let isFetchingAllIndia = false;
let activeStateFetchPromise = null;
let activeStateFetchName = '';

async function loadAllIndiaLiveWeather() {
    if (!layerGroups['weather']) return;
    if (isFetchingAllIndia) return;
    isFetchingAllIndia = true;
    try {
        const res = await fetch('/api/weather/india/');
        if (res.ok) {
            const data = await res.json();
            const locations = data.hubs || data.locations || [];
            renderWeatherMarkersOnMap(locations);
            updateHighAlertCard(locations, 'ALL INDIA');
        }
    } catch (e) {
        console.warn("Failed to fetch live All India weather:", e);
    } finally {
        isFetchingAllIndia = false;
    }
}

async function loadStateDistrictsLiveWeather(stateName) {
    if (!layerGroups['weather']) return [];
    if (activeStateFetchName === stateName && activeStateFetchPromise) {
        return activeStateFetchPromise;
    }
    activeStateFetchName = stateName;
    activeStateFetchPromise = (async () => {
        let fetchedDistricts = [];
        try {
            const res = await fetch(`/api/weather/state/?state=${encodeURIComponent(stateName)}`);
            if (res.ok) {
                const data = await res.json();
                fetchedDistricts = data.districts || data.hubs || [];
                renderWeatherMarkersOnMap(fetchedDistricts);
                updateHighAlertCard(fetchedDistricts, stateName);
            }
        } catch (e) {
            console.warn(`Failed to fetch live district weather for ${stateName}:`, e);
        } finally {
            activeStateFetchPromise = null;
            activeStateFetchName = '';
        }
        return fetchedDistricts;
    })();
    return activeStateFetchPromise;
}

window.loadAllIndiaLiveWeather = loadAllIndiaLiveWeather;
window.loadStateDistrictsLiveWeather = loadStateDistrictsLiveWeather;

function setUserLocationOnMap(lat, lon, locationName = "Your Location", accuracy = 0) {
    if (!rudramMap) return;

    if (userLocationMarker) {
        rudramMap.removeLayer(userLocationMarker);
    }
    if (userLocationCircle) {
        rudramMap.removeLayer(userLocationCircle);
    }

    const radiusMeters = accuracy > 0 ? Math.max(accuracy, 100) : 500;

    userLocationCircle = L.circle([lat, lon], {
        radius: radiusMeters,
        color: '#38bdf8',
        fillColor: '#38bdf8',
        fillOpacity: 0.15,
        weight: 1.5
    }).addTo(rudramMap);

    const userIcon = L.divIcon({
        className: 'user-loc-icon',
        html: `<div style="background:#38bdf8; border:3px solid #ffffff; width:22px; height:22px; border-radius:50%; box-shadow:0 0 14px rgba(56,189,248,0.9); animation: pulseCritical 1.8s infinite;"></div>`,
        iconSize: [22, 22],
        iconAnchor: [11, 11]
    });

    const accLabel = accuracy > 0 ? ` &bull; Accuracy: ±${accuracy}m` : '';

    userLocationMarker = L.marker([lat, lon], { icon: userIcon })
        .addTo(rudramMap)
        .bindPopup(`<div class="p-2 text-center"><span class="badge bg-info mb-1">REAL GPS LOCATION</span><h6 class="fw-bold mb-0 text-white">${locationName}</h6><div class="small text-muted mt-1">Lat: ${Number(lat).toFixed(4)}°, Lon: ${Number(lon).toFixed(4)}°${accLabel}</div></div>`)
        .openPopup();

    rudramMap.flyTo([lat, lon], 13, { duration: 1.2 });
}

function setSelectedLocationOnMap(lat, lon, locationName = "Searched Location", weatherData = null, stateName = "") {
    if (!rudramMap) return;

    if (userLocationMarker) {
        rudramMap.removeLayer(userLocationMarker);
    }
    if (userLocationCircle) {
        rudramMap.removeLayer(userLocationCircle);
    }

    userLocationCircle = L.circle([lat, lon], {
        radius: 1500,
        color: '#06b6d4',
        fillColor: '#06b6d4',
        fillOpacity: 0.15,
        weight: 1.5
    }).addTo(rudramMap);

    const searchIcon = L.divIcon({
        className: 'search-loc-icon',
        html: `<div style="background:#06b6d4; border:3px solid #ffffff; width:24px; height:24px; border-radius:50%; box-shadow:0 0 16px rgba(6,182,212,0.9); animation: pulseCritical 1.8s infinite;"></div>`,
        iconSize: [24, 24],
        iconAnchor: [12, 12]
    });

    const curr = weatherData && weatherData.current ? weatherData.current : {};
    const tempStr = curr.temperature !== undefined ? `${curr.temperature}°C` : '--';
    const rainStr = curr.rainfall !== undefined ? `${curr.rainfall} mm/h` : '--';
    const humStr = curr.humidity !== undefined ? `${curr.humidity}%` : '--';
    const windStr = curr.wind_speed !== undefined ? `${curr.wind_speed} km/h` : '--';
    const condStr = curr.condition || 'Live Telemetry Active';
    const updatedStr = weatherData && weatherData.last_updated ? weatherData.last_updated.replace('T', ' ') : 'Just now';
    const stateStr = stateName || (locationName.includes(',') ? locationName.split(',').pop().trim() : 'India');

    const popupContent = `
        <div class="p-2" style="min-width: 210px;">
            <div class="d-flex align-items-center justify-content-between mb-1">
                <span class="badge bg-info text-dark fw-bold">SEARCHED LOCATION</span>
                <span class="badge bg-secondary">${stateStr}</span>
            </div>
            <h6 class="fw-bold mb-1 text-white">${locationName}</h6>
            <div class="text-info mb-2 small"><strong>${condStr}</strong></div>
            <div class="small text-secondary mb-1">Temperature: <strong class="text-warning">${tempStr}</strong></div>
            <div class="small text-secondary mb-1">Rainfall: <strong class="text-primary">${rainStr}</strong></div>
            <div class="small text-secondary mb-1">Humidity: <strong class="text-info">${humStr}</strong></div>
            <div class="small text-secondary mb-1">Wind Speed: <strong class="text-light">${windStr}</strong></div>
            <div class="small text-muted mt-2" style="font-size: 0.7rem;">Last updated: ${updatedStr}</div>
        </div>
    `;

    userLocationMarker = L.marker([lat, lon], { icon: searchIcon })
        .addTo(rudramMap)
        .bindPopup(popupContent);

    userLocationMarker.openPopup();
    rudramMap.flyTo([lat, lon], 12, { duration: 1.2 });
}

window.setUserLocationOnMap = setUserLocationOnMap;
window.setSelectedLocationOnMap = setSelectedLocationOnMap;

function addOrUpdateLocationRiskZone(lat, lon, locationName, riskData) {
    if (!rudramMap || !layerGroups['flood_risk'] || !riskData) return;

    const score = parseFloat(riskData.risk_score || riskData.risk_percentage || (riskData.prediction ? riskData.prediction.risk_score : 0));
    const level = (riskData.risk_level || (riskData.prediction ? riskData.prediction.risk_level : (score >= 70 ? 'CRITICAL' : score >= 50 ? 'HIGH' : score >= 30 ? 'MODERATE' : 'LOW'))).toUpperCase();

    if (score < 50 && level !== 'HIGH' && level !== 'CRITICAL') return;

    let strokeColor = '#ef4444';
    let fillColor = '#f87171';
    let fillOp = 0.25;
    let weight = 2;
    let dashArray = '4, 4';
    let badgeClass = 'bg-danger text-white';

    if (level === 'CRITICAL' || score >= 70) {
        strokeColor = '#dc2626';
        fillColor = '#b91c1c';
        fillOp = 0.35;
        weight = 3;
        dashArray = null;
    }

    const currentZoom = rudramMap ? rudramMap.getZoom() : 11;
    const radius = getResponsiveRiskRadius(level, score, currentZoom);
    const isDemo = riskData.is_demo || (riskData.explanation && riskData.explanation.is_demo);
    const sourceLabel = riskData.source || (isDemo ? 'RUDRAM Demo Dataset' : 'Live Multi-Factor AI Risk Engine');
    const modeBadge = isDemo ? '<span class="badge bg-warning text-dark me-1">DEMO DATASET</span>' : '<span class="badge bg-danger text-white me-1">AI RED ZONE</span>';

    const circle = L.circle([lat, lon], {
        radius: radius,
        color: strokeColor,
        fillColor: fillColor,
        fillOpacity: fillOp,
        weight: weight,
        dashArray: dashArray,
        pane: 'riskPane'
    });

    circle.bindTooltip(`<strong>${level} RISK</strong> &bull; ${locationName} (${score.toFixed(0)}%)`, {
        permanent: false,
        direction: 'top',
        className: 'leaflet-risk-tooltip'
    });

    const popupContent = `
        <div class="p-2" style="min-width: 250px; font-family: system-ui, -apple-system, sans-serif;">
            <div class="d-flex align-items-center justify-content-between mb-2">
                <span class="badge ${badgeClass} fw-bold" style="font-size: 0.75rem;">${level} RISK (${score.toFixed(1)}%)</span>
                <div>${modeBadge}</div>
            </div>
            <h6 class="fw-bold text-white mb-1" style="font-size: 0.9rem;">${locationName}</h6>
            <div class="small text-info mb-2" style="font-size: 0.75rem;">Multi-Factor XGBoost / RF Analysis</div>

            <div class="p-2 bg-dark bg-opacity-75 rounded border border-secondary border-opacity-25 mb-2" style="font-size: 0.78rem;">
                <div class="text-info fw-semibold mb-1">AI Contributory Risk Factors:</div>
                <div class="text-light">• Heavy Precipitation &amp; Accumulation</div>
                <div class="text-light">• Soil Saturation Runoff Potential</div>
                <div class="text-light">• Hydrological Basin Vulnerability</div>
            </div>

            <div class="small text-secondary border-top border-secondary border-opacity-25 pt-2" style="font-size: 0.75rem;">
                <div>Action Directive: <strong class="text-warning">${riskData.recommended_action || 'Evacuate low-lying sectors'}</strong></div>
                <div>Data Source: <strong class="text-info">${sourceLabel}</strong></div>
            </div>
        </div>
    `;

    circle.bindPopup(popupContent);
    circle.addTo(layerGroups['flood_risk']);
    activeRiskZoneCircles.push({ circle: circle, level: level, score: score });
}

window.addOrUpdateLocationRiskZone = addOrUpdateLocationRiskZone;

function loadFloodPolygons() {
    if (layerGroups['flood_extent']) layerGroups['flood_extent'].clearLayers();
    if (layerGroups['flood_risk']) layerGroups['flood_risk'].clearLayers();
    activeRiskZoneCircles = [];

    fetch('/api/risk/zones/')
        .then(res => res.json())
        .then(data => {
            if (data.success && Array.isArray(data.zones)) {
                const currentZoom = rudramMap ? rudramMap.getZoom() : 11;
                data.zones.forEach(zone => {
                    let strokeColor = '#f59e0b';
                    let fillColor = '#fbbf24';
                    let fillOp = 0.20;
                    let weight = 1.5;
                    let dashArray = null;
                    let badgeClass = 'bg-warning text-dark';

                    if (zone.risk_level === 'CRITICAL' || zone.risk_score >= 80) {
                        strokeColor = '#dc2626';
                        fillColor = '#b91c1c';
                        fillOp = 0.35;
                        weight = 3;
                        badgeClass = 'bg-danger text-white';
                    } else if (zone.risk_level === 'HIGH' || zone.risk_score >= 60) {
                        strokeColor = '#ef4444';
                        fillColor = '#f87171';
                        fillOp = 0.25;
                        weight = 2;
                        dashArray = '4, 4';
                        badgeClass = 'bg-danger text-white';
                    }

                    let centerLat = zone.center_lat;
                    let centerLon = zone.center_lon;

                    if ((!centerLat || !centerLon) && zone.polygon_geojson && zone.polygon_geojson.geometry && zone.polygon_geojson.geometry.coordinates) {
                        const coords = zone.polygon_geojson.geometry.coordinates[0];
                        if (coords && coords.length > 0) {
                            let sumLat = 0, sumLon = 0;
                            coords.forEach(pt => { sumLon += pt[0]; sumLat += pt[1]; });
                            centerLat = sumLat / coords.length;
                            centerLon = sumLon / coords.length;
                        }
                    }

                    if (centerLat && centerLon) {
                        const radius = getResponsiveRiskRadius(zone.risk_level, zone.risk_score, currentZoom);
                        const circle = L.circle([centerLat, centerLon], {
                            radius: radius,
                            color: strokeColor,
                            fillColor: fillColor,
                            fillOpacity: fillOp,
                            weight: weight,
                            dashArray: dashArray,
                            pane: 'riskPane'
                        });

                        const isDemo = data.is_demo || zone.is_demo;
                        const sourceLabel = zone.source || (isDemo ? 'RUDRAM Demo Dataset' : 'Live Sensor Telemetry');
                        const modeBadge = isDemo ? '<span class="badge bg-warning text-dark">DEMO DATASET</span>' : '<span class="badge bg-success text-white">LIVE SENSORS</span>';

                        const popupContent = `
                            <div class="p-2" style="min-width: 250px; font-family: system-ui, -apple-system, sans-serif;">
                                <div class="d-flex align-items-center justify-content-between mb-2">
                                    <span class="badge ${badgeClass} fw-bold" style="font-size: 0.75rem;">${zone.risk_level} RISK (${zone.risk_score}%)</span>
                                    <div>${modeBadge}</div>
                                </div>
                                <h6 class="fw-bold text-white mb-1" style="font-size: 0.9rem;">${zone.name}</h6>
                                <div class="small text-info mb-2" style="font-size: 0.75rem;">${zone.district}, Odisha &bull; AI Multi-Hazard Risk Analysis</div>

                                <div class="p-2 bg-dark bg-opacity-75 rounded border border-secondary border-opacity-25 mb-2" style="font-size: 0.78rem;">
                                    <div class="text-info fw-semibold mb-1">AI Contributory Risk Factors:</div>
                                    <div class="text-light">• Heavy Monsoon Rainfall Accumulation</div>
                                    <div class="text-light">• Elevation: ${zone.elevation_m || '12'}m a.s.l.</div>
                                    <div class="text-light">• Nearest River: ${zone.nearest_river || 'Mahanadi / Catchment Stream'} (${zone.river_distance || '0.5 km'})</div>
                                    <div class="text-light">• Historical Flood: Detected in Catchment</div>
                                </div>

                                <div class="small text-secondary border-top border-secondary border-opacity-25 pt-2" style="font-size: 0.75rem;">
                                    <div>Exposed Population: <strong class="text-white">${(zone.population_count || 12500).toLocaleString()}</strong></div>
                                    <div>Vulnerable Buildings: <strong class="text-warning">${zone.vulnerable_buildings || 420}</strong></div>
                                    <div>Data Source: <strong class="text-info">${sourceLabel}</strong></div>
                                </div>
                            </div>
                        `;
                        circle.bindTooltip(`<strong>${zone.risk_level} RISK (${zone.risk_score}%)</strong> &bull; ${zone.name}`, {
                            permanent: false,
                            direction: 'top',
                            className: 'leaflet-risk-tooltip'
                        });
                        circle.bindPopup(popupContent);
                        if (layerGroups['flood_risk']) {
                            circle.addTo(layerGroups['flood_risk']);
                            activeRiskZoneCircles.push({ circle: circle, level: zone.risk_level, score: zone.risk_score });
                        }
                    }
                });
            }
        })
        .catch(err => console.error('Error loading AI Risk Zones:', err));
}

function loadSheltersLayer() {
    if (layerGroups['shelters']) layerGroups['shelters'].clearLayers();
}

function loadInfrastructureLayer() {
    if (layerGroups['hospitals']) layerGroups['hospitals'].clearLayers();
}

function loadRiversAndDamsLayer() {
    if (layerGroups['rivers']) layerGroups['rivers'].clearLayers();
    if (layerGroups['bridges']) layerGroups['bridges'].clearLayers();
}

function loadEvacuationRoutesLayer() {
    if (layerGroups['evacuation_routes']) layerGroups['evacuation_routes'].clearLayers();
}

function loadFireHotspotsLayer() {
    if (layerGroups['fire_hotspots']) layerGroups['fire_hotspots'].clearLayers();
}

function initMapInfoControl() {
    if (!rudramMap) return;

    const MapInfoControl = L.Control.extend({
        options: { position: 'topleft' },
        onAdd: function (map) {
            const container = L.DomUtil.create('div', 'leaflet-bar leaflet-control leaflet-control-custom');
            container.style.backgroundColor = '#ffffff';
            container.style.width = '34px';
            container.style.height = '34px';
            container.style.display = 'flex';
            container.style.alignItems = 'center';
            container.style.justifyContent = 'center';
            container.style.cursor = 'pointer';
            container.style.boxShadow = '0 2px 6px rgba(0,0,0,0.2)';
            container.title = 'Map Info';
            container.innerHTML = '<i data-lucide="info" style="width: 18px; height: 18px; color: #0d6efd;"></i>';

            L.DomEvent.disableClickPropagation(container);
            L.DomEvent.on(container, 'click', function (e) {
                L.DomEvent.stopPropagation(e);
                toggleMapInfoCard();
            });

            return container;
        }
    });

    rudramMap.addControl(new MapInfoControl());
    if (window.lucide) lucide.createIcons();
}

function initMapModeControl() {
    if (!rudramMap) return;

    const MapModeControl = L.Control.extend({
        options: { position: 'topleft' },
        onAdd: function (map) {
            const container = L.DomUtil.create('div', 'leaflet-bar leaflet-control leaflet-control-custom');
            container.id = 'mapModeBtn';
            container.style.backgroundColor = '#ffffff';
            container.style.width = '34px';
            container.style.height = '34px';
            container.style.display = 'flex';
            container.style.alignItems = 'center';
            container.style.justifyContent = 'center';
            container.style.cursor = 'pointer';
            container.style.boxShadow = '0 2px 6px rgba(0,0,0,0.2)';
            container.title = 'Map Mode';
            container.innerHTML = '<i data-lucide="layers" style="width: 18px; height: 18px; color: #0d6efd;"></i>';

            L.DomEvent.disableClickPropagation(container);
            L.DomEvent.on(container, 'click', function (e) {
                L.DomEvent.stopPropagation(e);
                toggleMapModeCard();
            });

            return container;
        }
    });

    rudramMap.addControl(new MapModeControl());
    if (window.lucide) lucide.createIcons();
}

function toggleMapModeCard() {
    let card = document.getElementById('mapModeCard');
    if (!card) {
        card = document.createElement('div');
        card.id = 'mapModeCard';
        card.className = 'shadow-sm border rounded p-2';
        card.style.position = 'absolute';
        card.style.top = '100px';
        card.style.left = '10px';
        card.style.zIndex = '1000';
        card.style.width = '170px';
        card.style.backgroundColor = '#ffffff';
        card.style.color = '#212529';
        card.style.fontSize = '0.82rem';
        card.style.fontFamily = 'system-ui, -apple-system, sans-serif';
        card.style.border = '1px solid #dee2e6';
        card.style.display = 'none';

        const mapContainer = document.getElementById('gisMap') || document.getElementById('map') || document.body;
        if (mapContainer.style.position !== 'absolute' && mapContainer.style.position !== 'relative') {
            mapContainer.style.position = 'relative';
        }
        mapContainer.appendChild(card);
    }

    if (card.style.display === 'none' || !card.style.display) {
        renderMapModeCardContent(card);
        card.style.display = 'block';
    } else {
        card.style.display = 'none';
    }
}

function renderMapModeCardContent(card) {
    card.innerHTML = `
        <div class="d-flex align-items-center justify-content-between pb-1 mb-2 border-bottom border-light-subtle">
            <strong style="color: #0d6efd; font-size: 0.8rem; letter-spacing: 0.5px;">MAP MODE</strong>
            <button type="button" class="btn-close" style="font-size: 0.6rem;" onclick="toggleMapModeCard()"></button>
        </div>
        <div class="d-flex flex-column gap-1">
            <label class="d-flex align-items-center gap-2 p-1 rounded" style="cursor: pointer;" onclick="switchMapMode('LIGHT')">
                <input type="radio" name="mapModeRadio" value="LIGHT" ${currentTileMode === 'LIGHT' ? 'checked' : ''}>
                <span class="fw-semibold" style="font-size: 0.78rem; color: #212529;">LIGHT</span>
            </label>
            <label class="d-flex align-items-center gap-2 p-1 rounded" style="cursor: pointer;" onclick="switchMapMode('DARK')">
                <input type="radio" name="mapModeRadio" value="DARK" ${currentTileMode === 'DARK' ? 'checked' : ''}>
                <span class="fw-semibold" style="font-size: 0.78rem; color: #212529;">DARK</span>
            </label>
            <label class="d-flex align-items-center gap-2 p-1 rounded" style="cursor: pointer;" onclick="switchMapMode('SATELLITE')">
                <input type="radio" name="mapModeRadio" value="SATELLITE" ${currentTileMode === 'SATELLITE' ? 'checked' : ''}>
                <span class="fw-semibold" style="font-size: 0.78rem; color: #212529;">SATELLITE</span>
            </label>
        </div>
    `;
}

function switchMapMode(mode) {
    if (!rudramMap) return;
    if (activeBaseTile) {
        rudramMap.removeLayer(activeBaseTile);
    }
    if (mode === 'DARK') {
        activeBaseTile = gDarkTiles;
    } else if (mode === 'SATELLITE') {
        activeBaseTile = gSatTiles;
    } else {
        activeBaseTile = gStreetTiles;
        mode = 'LIGHT';
    }
    if (activeBaseTile) {
        activeBaseTile.addTo(rudramMap);
    }
    currentTileMode = mode;

    const card = document.getElementById('mapModeCard');
    if (card) renderMapModeCardContent(card);
}

window.toggleMapModeCard = toggleMapModeCard;
window.switchMapMode = switchMapMode;

document.addEventListener('click', function (e) {
    const modeCard = document.getElementById('mapModeCard');
    const modeBtn = document.getElementById('mapModeBtn');
    if (modeCard && modeCard.style.display !== 'none') {
        if (!modeCard.contains(e.target) && (!modeBtn || !modeBtn.contains(e.target))) {
            modeCard.style.display = 'none';
        }
    }
});

function toggleMapInfoCard() {
    let card = document.getElementById('mapInfoCard');
    if (!card) {
        card = document.createElement('div');
        card.id = 'mapInfoCard';
        card.className = 'shadow-sm border rounded p-3';
        card.style.position = 'absolute';
        card.style.top = '60px';
        card.style.left = '10px';
        card.style.zIndex = '1000';
        card.style.width = '240px';
        card.style.backgroundColor = '#ffffff';
        card.style.color = '#212529';
        card.style.fontSize = '0.82rem';
        card.style.fontFamily = 'system-ui, -apple-system, sans-serif';
        card.style.border = '1px solid #dee2e6';
        card.style.display = 'none';

        const mapContainer = document.getElementById('gisMap') || document.getElementById('map') || document.body;
        if (mapContainer.style.position !== 'absolute' && mapContainer.style.position !== 'relative') {
            mapContainer.style.position = 'relative';
        }
        mapContainer.appendChild(card);
    }

    if (card.style.display === 'none' || !card.style.display) {
        const now = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        card.innerHTML = `
            <div class="d-flex align-items-center justify-content-between pb-2 mb-2 border-bottom border-light-subtle">
                <strong style="color: #0d6efd; font-size: 0.88rem;">MAP INFO</strong>
                <button type="button" class="btn-close" style="font-size: 0.7rem;" onclick="toggleMapInfoCard()"></button>
            </div>
            <div class="mb-1" style="color: #495057;"><strong style="color: #212529;">Weather:</strong> Live Open-Meteo data</div>
            <div class="mb-1" style="color: #495057;"><strong style="color: #212529;">Risk:</strong> RUDRAM AI risk score</div>
            <div class="mb-1" style="color: #495057;"><strong style="color: #212529;">Alerts:</strong> High-risk locations</div>
            <div class="mb-1" style="color: #495057;"><strong style="color: #212529;">Map:</strong> Live GIS data</div>
            <div class="mt-2 pt-2 border-top border-light-subtle text-muted" style="font-size: 0.72rem;">
                Updated: <span>${now}</span>
            </div>
        `;
        card.style.display = 'block';
    } else {
        card.style.display = 'none';
    }
}
window.toggleMapInfoCard = toggleMapInfoCard;

function updateHighAlertCard(locations, modeName = 'ALL INDIA') {
    const titleEl = document.getElementById('highAlertTitle');
    const badgeEl = document.getElementById('highAlertBadge');
    const listEl = document.getElementById('highAlertsList');

    if (titleEl) {
        titleEl.textContent = modeName === 'ALL INDIA' ? 'HIGH ALERTS — INDIA' : `HIGH ALERTS — ${modeName.toUpperCase()}`;
    }

    if (!listEl) return;

    if (!locations || locations.length === 0) {
        listEl.innerHTML = '<div class="p-3 text-center text-muted small">No high-risk locations currently detected.</div>';
        if (badgeEl) { badgeEl.textContent = 'LIVE'; badgeEl.className = 'badge bg-success font-monospace'; }
        return;
    }

    const hasLiveError = locations.every(loc => loc.is_available === false);
    if (hasLiveError) {
        listEl.innerHTML = '<div class="p-3 text-center text-warning small fw-bold">LIVE DATA UNAVAILABLE</div>';
        if (badgeEl) { badgeEl.textContent = 'UNAVAILABLE'; badgeEl.className = 'badge bg-warning text-dark font-monospace'; }
        return;
    }

    const validAlerts = locations.filter(loc => loc.is_available !== false);
    validAlerts.sort((a, b) => (b.risk_score || 0) - (a.risk_score || 0));

    const highRiskItems = validAlerts.slice(0, 8);

    if (highRiskItems.length === 0) {
        listEl.innerHTML = '<div class="p-3 text-center text-muted small">No high-risk locations currently detected.</div>';
        if (badgeEl) { badgeEl.textContent = 'LIVE'; badgeEl.className = 'badge bg-success font-monospace'; }
        return;
    }

    if (badgeEl) { badgeEl.textContent = 'LIVE'; badgeEl.className = 'badge bg-success font-monospace'; }

    let html = '';
    highRiskItems.forEach(loc => {
        const locName = loc.name || loc.city || 'Unknown';
        const riskLevel = loc.risk_level || (loc.risk_score >= 75 ? 'CRITICAL' : 'HIGH');
        const riskBadgeClass = riskLevel === 'CRITICAL' ? 'bg-danger' : (riskLevel === 'HIGH' ? 'bg-warning text-dark' : 'bg-info text-dark');
        const rainVal = loc.rainfall != null ? loc.rainfall : (loc.rain || 0);
        const windVal = loc.wind_speed != null ? loc.wind_speed : 0;
        const scoreVal = loc.risk_score ? Math.round(loc.risk_score) : 60;
        const lat = loc.lat || loc.latitude || 20.2961;
        const lon = loc.lon || loc.longitude || 85.8245;
        const zoom = loc.zoom || 7;
        const capital = loc.capital || '';

        const clickHandler = loc.type === 'state'
            ? `onclick="selectIndianState('${locName}', ${lat}, ${lon}, ${zoom}, '${capital}')"`
            : `onclick="handleWeatherMarkerClick('${locName}', ${lat}, ${lon})"`;

        html += `
            <div class="high-alert-item" ${clickHandler} style="cursor: pointer;">
                <div class="d-flex align-items-center justify-content-between">
                    <strong class="text-white small">${locName}</strong>
                    <span class="badge ${riskBadgeClass} font-monospace" style="font-size: 0.7rem;">${riskLevel}</span>
                </div>
                <div class="d-flex justify-content-between small text-muted mt-1" style="font-size: 0.72rem;">
                    <span>Rain: <strong class="text-primary">${rainVal} mm</strong></span>
                    <span>Wind: <strong>${windVal} km/h</strong></span>
                    <span>Risk: <strong class="text-danger">${scoreVal}%</strong></span>
                </div>
            </div>
        `;
    });

    listEl.innerHTML = html;
}
window.updateHighAlertCard = updateHighAlertCard;
