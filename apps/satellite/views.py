from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from apps.satellite.models import SatelliteAnalysis, DamageZone
from apps.satellite.serializers import SatelliteAnalysisSerializer
from services.gee_service import gee_service

def satellite_view(request):
    analyses = SatelliteAnalysis.objects.all()
    latest = analyses.first()
    context = {
        'analyses': analyses,
        'latest': latest,
        'page_title': 'RUDRAM Satellite Analysis Lab & SAR Inundation Engine'
    }
    return render(request, 'satellite/index.html', context)

class SatelliteSearchAPIView(APIView):
    """
    POST /api/satellite/search/
    Searches available Sentinel-1 GRD and Sentinel-2 L2A granules for selected AOI.
    """
    def post(self, request):
        aoi = request.data.get('aoi', {'lat': 20.2961, 'lon': 85.8245})
        pre_date = request.data.get('pre_event_date', '2026-08-01')
        post_date = request.data.get('post_event_date', '2026-08-14')

        result = gee_service.search_granules(aoi, pre_date, post_date)
        return Response(result, status=status.HTTP_200_OK)

class SatelliteFloodDetectionAPIView(APIView):
    """
    POST /api/satellite/flood-detection/
    Runs Sentinel-1 SAR backscatter thresholding workflow via Earth Engine.
    """
    def post(self, request):
        aoi = request.data.get('aoi', {'lat': 20.2961, 'lon': 85.8245})
        pre_date = request.data.get('pre_event_date', '2026-08-01')
        post_date = request.data.get('post_event_date', '2026-08-14')

        result = gee_service.analyze_sentinel1_flood(aoi, pre_date, post_date)

        if not result.get('success', False):
            return Response(result, status=status.HTTP_200_OK)

        # Save real GEE analysis to database
        analysis = SatelliteAnalysis.objects.create(
            title=f"Sentinel-1 Flood Assessment ({post_date})",
            sensor='SENTINEL_1',
            status='COMPLETED',
            aoi_name=request.data.get('aoi_name', 'Bhubaneswar Floodplain Sector'),
            pre_event_date=pre_date,
            post_event_date=post_date,
            flooded_area_sqkm=result.get('flooded_area_sqkm', 0),
            damaged_area_sqkm=result.get('affected_area_sqkm', 0),
            affected_population=result.get('estimated_affected_population', 0),
            submerged_roads_km=result.get('submerged_roads_km', 0),
            confidence=result.get('confidence', 0.95),
            is_demo=False,
            metrics=result,
            geojson_data=result.get('geojson', {})
        )

        return Response({
            'success': True,
            'analysis': SatelliteAnalysisSerializer(analysis).data,
            'details': result
        }, status=status.HTTP_200_OK)

class SatelliteChangeDetectionAPIView(APIView):
    """
    POST /api/satellite/change-detection/
    """
    def post(self, request):
        aoi = request.data.get('aoi', {'lat': 20.2961, 'lon': 85.8245})
        pre_date = request.data.get('pre_event_date', '2026-08-01')
        post_date = request.data.get('post_event_date', '2026-08-14')

        result = gee_service.analyze_sentinel2_optical(aoi, pre_date, post_date)
        return Response(result, status=status.HTTP_200_OK)

class SatelliteDamageDetectionAPIView(APIView):
    """
    POST /api/satellite/damage-detection/
    U-Net / Deep Learning Multi-Class Damage Segmentation Inference Interface.
    """
    def post(self, request):
        return Response({
            'success': True,
            'model_architecture': 'PyTorch ResNet-34 U-Net Feature Pyramid Network',
            'classes': {
                '0_background': 'Unchanged Land (62%)',
                '1_water_flood': 'Inundated Standing Water (26%)',
                '2_damaged_structures': 'Submerged/Damaged Buildings (4%)',
                '3_sediment_wash': 'Siltation / Agricultural Runoff (8%)'
            },
            'iou_accuracy': 0.884,
            'f1_score': 0.912,
            'status': 'SIMULATED AI SEGMENTATION (DEMO LAB MODE)',
            'is_demo': True
        })
