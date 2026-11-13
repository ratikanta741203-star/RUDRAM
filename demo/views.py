from rest_framework.views import APIView
from rest_framework.response import Response
from demo.demo_engine import demo_engine
from django.core.management import call_command

class RunDemoScenarioAPIView(APIView):
    """
    POST /api/demo/run-scenario/
    Triggers the 1-click Flood Emergency Hackathon Demo Flow.
    """
    def post(self, request):
        intensity = request.data.get('intensity', 'CRITICAL')
        result = demo_engine.run_scenario(intensity=intensity)
        return Response(result)

class ResetDemoAPIView(APIView):
    """
    POST /api/demo/reset/
    Reseeds the database to pristine baseline demo state.
    """
    def post(self, request):
        try:
            call_command('seed_demo')
            return Response({'success': True, 'message': 'Demo database successfully reset to calibrated Bhubaneswar baseline.'})
        except Exception as e:
            return Response({'success': False, 'error': str(e)}, status=500)
