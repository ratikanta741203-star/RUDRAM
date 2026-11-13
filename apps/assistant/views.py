from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from apps.assistant.models import EmergencyRecommendation
from apps.assistant.serializers import EmergencyRecommendationSerializer
from apps.disasters.models import Disaster
from apps.shelters.models import Shelter
from apps.resources.models import Resource, RescueTeam

def assistant_view(request):
    recommendations = EmergencyRecommendation.objects.all()[:5]
    context = {
        'recommendations': recommendations,
        'page_title': 'RUDRAM AI Emergency Response Copilot'
    }
    return render(request, 'assistant/chat.html', context)

class AssistantAnalyzeAPIView(APIView):
    """
    POST /api/assistant/analyze/
    Analyzes live multi-hazard state and synthesizes actionable disaster response recommendations.
    """
    def post(self, request):
        risk_score = float(request.data.get('risk_score', 84))
        rainfall_mm = float(request.data.get('rainfall_mm', 186.4))
        location_name = request.data.get('location_name', 'Bhubaneswar Catchment')
        exposed_pop = int(request.data.get('exposed_population', 18400))

        # Synthesize rule-based / LLM disaster recommendations
        if risk_score >= 80:
            priority = 'CRITICAL'
            summary = f"CRITICAL FLOOD EMERGENCY DETECTED: Risk score is {risk_score}% in {location_name} with {rainfall_mm}mm precipitation. Immediate evacuation and life-safety response required."
            actions = [
                {'action': 'Issue Emergency Siren & Geo-Targeted Alert Broadcast', 'target': 'Zone A & Rasulgarh Embankment settlements', 'priority': 'P0 (Immediate)'},
                {'action': f'Initiate mandatory evacuation for ~{exposed_pop} exposed residents', 'target': 'Designate High-Ground Shelters: BJB College & Capital High School', 'priority': 'P0 (Immediate)'},
                {'action': 'Deploy 2x ODRAF Battalions and 1x NDRF Unit with 12 motorized boats', 'target': 'Kuakhai/Daya confluence staging base', 'priority': 'P1 (30 Mins)'},
                {'action': 'Dispatch 1,500 Packets Dry Ration & 3,000L Potable Water', 'target': 'Sector 4 Shelter staging point', 'priority': 'P1 (45 Mins)'},
                {'action': 'Impose traffic restriction on NH16 Submerged Service Lane & Daya Embankment Road', 'target': 'Traffic Enforcement & Police Units', 'priority': 'P1 (Immediate)'},
                {'action': 'Request Hirakud Dam flood discharge moderation from Central Water Commission', 'target': 'Inter-State River Basin Command', 'priority': 'P2 (1 Hour)'}
            ]
            rationale = "Rapid rise of river gauge (+0.14m/hr) coupled with saturated catchment soil moisture index (0.91) indicates impending embankment overtopping within 3-4 hours."
        elif risk_score >= 50:
            priority = 'HIGH'
            summary = f"HIGH FLOOD WARNING: Risk score is {risk_score}%. Waterlogging and flash flood conditions probable in low-lying sectors."
            actions = [
                {'action': 'Pre-position dewatering pumps and clearance teams at vulnerable culverts', 'target': 'BMC Stormwater Division', 'priority': 'P1'},
                {'action': 'Alert designated shelters and verify generator backup & water supplies', 'target': 'District Relief Officer', 'priority': 'P1'},
                {'action': 'Issue heavy rainfall advisory to schools and commercial transit', 'target': 'Public Alert System', 'priority': 'P2'}
            ]
            rationale = "Rainfall intensity exceeds stormwater drainage conveyance capacity."
        else:
            priority = 'MEDIUM'
            summary = f"NORMAL / ELEVATED SURVEILLANCE: Risk score is {risk_score}%. Maintain meteorological monitoring."
            actions = [
                {'action': 'Monitor Open-Meteo & IMD radar updates', 'target': 'Control Room', 'priority': 'P3'},
                {'action': 'Ensure emergency supplies inventory readiness in central warehouse', 'target': 'Logistics Team', 'priority': 'P3'}
            ]
            rationale = "Hydrological metrics remain within nominal reservoir and drainage thresholds."

        rec = EmergencyRecommendation.objects.create(
            situation_summary=summary,
            priority=priority,
            action_items=actions,
            rationale=rationale,
            is_rule_based_demo=True
        )

        return Response({
            'success': True,
            'mode': 'RULE_BASED_AI_ASSISTANT',
            'is_demo': True,
            'label': 'AI-GENERATED ACTIONABLE RECOMMENDATIONS (Transparent Expert Rules Engine)',
            'recommendation': EmergencyRecommendationSerializer(rec).data
        }, status=status.HTTP_200_OK)

from apps.assistant.engine import rudram_search_engine

class AssistantChatAPIView(APIView):
    """
    POST /api/assistant/chat/
    Project-Aware Python Search Engine & RAG Pipeline for Natural-Language Disaster Intelligence Queries.
    """
    def post(self, request):
        query = request.data.get('message', '').strip()
        if not query:
            return Response({'success': False, 'error': 'Query message required'}, status=status.HTTP_400_BAD_REQUEST)

        # Execute Project-Aware Search & Retrieval Engine
        result = rudram_search_engine.query(query)

        return Response({
            'success': True,
            'reply': result['reply'],
            'source': result['source'],
            'data_timestamp': result['data_timestamp'],
            'confidence': result['confidence'],
            'mode': result['mode']
        }, status=status.HTTP_200_OK)
