from django.test import TestCase, Client, override_settings
from django.contrib.auth.models import User
from unittest.mock import patch
from apps.disasters.models import Disaster
from apps.shelters.models import Shelter
from apps.resources.models import Resource
from apps.alerts.models import Alert
from apps.risk.models import RiskPrediction
from services.open_meteo import open_meteo_service, get_weather_description

class RudramSystemIntegrationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin_user = User.objects.create_superuser(username='testadmin', email='testadmin@rudram.gov.in', password='password123')
        self.disaster = Disaster.objects.create(
            title="Test Flood Event",
            disaster_type="FLOOD",
            severity="CRITICAL",
            status="ACTIVE",
            location_name="Test Catchment Basin",
            latitude=20.2961,
            longitude=85.8245,
            risk_score=85,
            exposed_population=12000
        )
        self.shelter = Shelter.objects.create(
            name="Test High-Ground Shelter",
            address="Unit 1, Test City",
            latitude=20.2900,
            longitude=85.8200,
            total_capacity=1000,
            current_occupancy=250,
            has_medical_station=True,
            status="OPEN"
        )

    def test_health_check_api(self):
        res = self.client.get('/api/health/')
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data['status'], 'healthy')
        self.assertEqual(data['database'], 'connected')

    def test_weather_current_api(self):
        res = self.client.get('/api/weather/current/?latitude=20.2961&longitude=85.8245')
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data['success'])
        self.assertIn('current', data)
        self.assertIn('temperature', data['current'])
        self.assertIn('humidity', data['current'])
        self.assertIn('rainfall', data['current'])
        self.assertIn('wind_speed', data['current'])
        self.assertIn('weather_code', data['current'])

    def test_weather_forecast_api(self):
        forecast = {'success': True, 'hourly': {}, 'daily': {}}
        with patch('apps.weather.views.open_meteo_service.get_forecast', return_value=forecast):
            res = self.client.get('/api/weather/forecast/?latitude=20.2961&longitude=85.8245&forecast_days=3')
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data['success'])
        self.assertIn('hourly', data)
        self.assertIn('daily', data)

    def test_weather_invalid_coordinates(self):
        # Latitude out of bounds
        res_lat = self.client.get('/api/weather/current/?latitude=91&longitude=85.8245')
        self.assertEqual(res_lat.status_code, 400)
        self.assertFalse(res_lat.json()['success'])

        # Longitude out of bounds
        res_lon = self.client.get('/api/weather/current/?latitude=20.2961&longitude=200')
        self.assertEqual(res_lon.status_code, 400)
        self.assertFalse(res_lon.json()['success'])

        # Non-numeric
        res_str = self.client.get('/api/weather/current/?latitude=abc&longitude=xyz')
        self.assertEqual(res_str.status_code, 400)
        self.assertFalse(res_str.json()['success'])

    def test_weather_invalid_forecast_days(self):
        # Days = 0
        res_0 = self.client.get('/api/weather/forecast/?latitude=20.2961&longitude=85.8245&forecast_days=0')
        self.assertEqual(res_0.status_code, 400)
        self.assertFalse(res_0.json()['success'])

        # Days = 17
        res_17 = self.client.get('/api/weather/forecast/?latitude=20.2961&longitude=85.8245&forecast_days=17')
        self.assertEqual(res_17.status_code, 400)
        self.assertFalse(res_17.json()['success'])

        # Non-integer days
        res_bad = self.client.get('/api/weather/forecast/?latitude=20.2961&longitude=85.8245&forecast_days=abc')
        self.assertEqual(res_bad.status_code, 400)
        self.assertFalse(res_bad.json()['success'])

    def test_weather_code_helper(self):
        self.assertEqual(get_weather_description(0), "Clear Sky")
        self.assertEqual(get_weather_description(65), "Heavy Rain")
        self.assertEqual(get_weather_description(95), "Thunderstorm")

    @override_settings(SITE_URL='https://rudram.example')
    def test_dashboard_page(self):
        res = self.client.get('/dashboard/')
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'RUDRAM')
        self.assertEqual(res.content.decode().count('<h1'), 1)
        self.assertContains(res, 'rel="canonical" href="https://rudram.example/dashboard/"')
        self.assertContains(res, '"@type": "Organization"')
        self.assertContains(res, 'https://rudram.example/static/images/rudram-social.png')

    @override_settings(SITE_URL='https://rudram.example')
    def test_seo_public_files(self):
        robots = self.client.get('/robots.txt')
        self.assertEqual(robots.status_code, 200)
        self.assertContains(robots, 'Sitemap: https://rudram.example/sitemap.xml')

        sitemap = self.client.get('/sitemap.xml')
        self.assertEqual(sitemap.status_code, 200)
        self.assertContains(sitemap, 'https://rudram.example/dashboard/')

        llms = self.client.get('/llms.txt')
        self.assertEqual(llms.status_code, 200)
        self.assertContains(llms, 'RUDRAM 2.0')

    def test_population_page_does_not_show_sample_totals_without_data(self):
        response = self.client.get('/population/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No population exposure records are available.')
        self.assertNotContains(response, '128,500')
        self.assertNotContains(response, '18,400')
        self.assertNotContains(response, '1,800 capacity units')

    @override_settings(DEBUG=False)
    def test_custom_404_page(self):
        res = self.client.get('/page-that-does-not-exist/')
        self.assertEqual(res.status_code, 404)
        self.assertContains(res, "We couldn't find that page", status_code=404)
        self.assertEqual(res.content.decode().count('<h1'), 1)

    def test_map_page(self):
        res = self.client.get('/map/')
        self.assertEqual(res.status_code, 200)

    def test_risk_predict_api(self):
        payload = {
            'location_name': 'Test Urban Sector',
            'latitude': 20.2961,
            'longitude': 85.8245,
            'rainfall_24h_mm': 180.0,
            'elevation_m': 15.0,
            'distance_to_water_km': 1.0,
            'river_water_level_m': 14.5
        }
        res = self.client.post('/api/risk/predict/', data=payload, content_type='application/json')
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data['success'])
        self.assertIn('risk_score', data['explanation'])
        self.assertGreater(data['explanation']['risk_score'], 50)

    def test_shelters_recommend_api(self):
        res = self.client.get('/api/shelters/recommend/?lat=20.2961&lon=85.8245')
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data['success'])
        self.assertIsNotNone(data['best_match'])

    def test_evacuation_route_api(self):
        payload = {
            'start_lat': 20.2961,
            'start_lon': 85.8245,
            'end_lat': 20.2545,
            'end_lon': 85.8390
        }
        res = self.client.post('/api/evacuation/route/', data=payload, content_type='application/json')
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data['success'])
        self.assertIn('routes', data['result'])

    def test_assistant_chat_api(self):
        payload = {'message': 'What is the safest evacuation route?'}
        res = self.client.post('/api/assistant/chat/', data=payload, content_type='application/json')
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data['success'])
        self.assertIn('reply', data)

    def test_alerts_api(self):
        res = self.client.get('/api/alerts/')
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data['success'])

    def test_satellite_flood_detection_api(self):
        payload = {
            'aoi': {'lat': 20.2961, 'lon': 85.8245},
            'pre_event_date': '2026-08-01',
            'post_event_date': '2026-08-14',
            'aoi_name': 'Test Floodplain'
        }
        analysis = {
            'success': True,
            'flooded_area_sqkm': 2.4,
            'affected_area_sqkm': 3.0,
            'estimated_affected_population': 1080,
            'submerged_roads_km': 1.9,
            'confidence': 0.95,
            'geojson': {'type': 'FeatureCollection', 'features': []}
        }
        with patch('apps.satellite.views.gee_service.analyze_sentinel1_flood', return_value=analysis):
            res = self.client.post('/api/satellite/flood-detection/', data=payload, content_type='application/json')
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data['success'])

    def test_reports_export_pdf(self):
        self.client.force_login(self.admin_user)
        res = self.client.get('/api/reports/export-pdf/')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res['Content-Type'], 'application/pdf')

    def test_reports_export_csv(self):
        self.client.force_login(self.admin_user)
        res = self.client.get('/api/reports/export-csv/?type=shelters')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res['Content-Type'], 'text/csv')

    def test_demo_scenario_trigger(self):
        res = self.client.post('/api/demo/run-scenario/', data={'intensity': 'CRITICAL'}, content_type='application/json')
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data['success'])

    def test_gpm_rainfall_api_valid_coords(self):
        res = self.client.get('/api/rainfall/gpm/?latitude=20.2961&longitude=85.8245')
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn(data.get('status'), ['LIVE', 'DEMO', 'UNAVAILABLE'])
        self.assertIn('satellite_rain_rate_mm_hr', data)
        self.assertIn('accumulated_24h_mm', data)
        self.assertIn('units', data)
        self.assertEqual(data['units']['accumulation'], 'mm')

    def test_gpm_rainfall_api_invalid_coords(self):
        res = self.client.get('/api/rainfall/gpm/?latitude=999&longitude=85.8245')
        self.assertEqual(res.status_code, 400)
        data = res.json()
        self.assertFalse(data['success'])

    def test_rainfall_trend_with_gpm(self):
        res = self.client.get('/api/rainfall/?latitude=20.2961&longitude=85.8245')
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data['success'])
        self.assertIn('gpm_satellite', data)
        self.assertIn('satellite_rain_rate_mm_hr', data['gpm_satellite'])

    def test_location_search_valid_indian_city(self):
        res = self.client.get('/api/location/search/?q=Cuttack')
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['country_code'], 'in')
        self.assertIn('Cuttack', data['display_name'])
        self.assertIsInstance(data['latitude'], float)
        self.assertIsInstance(data['longitude'], float)

    def test_location_search_outside_india(self):
        no_results = {'success': True, 'results': []}
        with patch('services.google_maps_service.google_maps_service.search_places', return_value=no_results):
            res = self.client.get('/api/location/search/?q=Paris')
        self.assertEqual(res.status_code, 400)
        data = res.json()
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'Please search for a location in India.')

    def test_location_search_empty_query(self):
        res = self.client.get('/api/location/search/?q=')
        self.assertEqual(res.status_code, 400)
        data = res.json()
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'Please enter a location name.')


