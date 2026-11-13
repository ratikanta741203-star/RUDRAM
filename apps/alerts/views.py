from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from apps.alerts.models import Alert, AlertApprovalRequest
from apps.alerts.serializers import AlertSerializer
from apps.core.models import AuditLog
from apps.accounts.permissions import is_strict_admin, is_operator, is_admin_or_operator, IsAdminUserOrCommander

def alerts_view(request):
    alerts = Alert.objects.all()
    critical_count = alerts.filter(severity='CRITICAL', is_active=True).count()
    high_count = alerts.filter(severity='HIGH', is_active=True).count()
    warning_count = alerts.filter(severity='WARNING', is_active=True).count()
    
    user_role = 'CITIZEN'
    if request.user.is_authenticated:
        if is_strict_admin(request.user):
            user_role = 'ADMIN'
        elif is_operator(request.user):
            user_role = 'EMERGENCY_OPERATOR'

    my_requests = []
    all_requests = []
    if user_role == 'ADMIN':
        all_requests = AlertApprovalRequest.objects.all()
    elif user_role == 'EMERGENCY_OPERATOR':
        my_requests = AlertApprovalRequest.objects.filter(operator=request.user)

    context = {
        'alerts': alerts,
        'critical_count': critical_count,
        'high_count': high_count,
        'warning_count': warning_count,
        'user_role': user_role,
        'my_requests': my_requests,
        'all_requests': all_requests,
        'page_title': 'Emergency Alert Notification & Broadcast Center'
    }
    return render(request, 'alerts/index.html', context)

class AlertListCreateAPIView(APIView):
    """
    GET /api/alerts/ (Public/Authenticated Read)
    POST /api/alerts/ (ADMIN ONLY - Direct Create)
    """
    def get(self, request):
        active_only = request.query_params.get('active_only', 'false').lower() == 'true'
        queryset = Alert.objects.filter(is_active=True) if active_only else Alert.objects.all()
        serializer = AlertSerializer(queryset, many=True)
        return Response({'success': True, 'count': queryset.count(), 'alerts': serializer.data})

    def post(self, request):
        if not is_strict_admin(request.user):
            return Response(
                {'success': False, 'error': 'Access Denied: Administrative privileges required to broadcast alerts directly. Operators must submit a change request.'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = AlertSerializer(data=request.data)
        if serializer.is_valid():
            alert = serializer.save()
            AuditLog.objects.create(
                user_name=request.user.username if request.user.is_authenticated else 'Admin',
                action='Broadcast Emergency Alert',
                target_model='Alert',
                target_id=str(alert.id),
                details=f"Issued [{alert.severity}] alert: {alert.title}"
            )
            return Response({'success': True, 'alert': serializer.data}, status=status.HTTP_201_CREATED)
        return Response({'success': False, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class AlertDismissAPIView(APIView):
    """
    POST /api/alerts/<id>/dismiss/ (ADMIN ONLY - Direct Deactivate)
    """
    def post(self, request, pk):
        if not is_strict_admin(request.user):
            return Response(
                {'success': False, 'error': 'Access Denied: Administrative privileges required to deactivate alerts directly.'},
                status=status.HTTP_403_FORBIDDEN
            )

        alert = get_object_or_404(Alert, pk=pk)
        alert.is_active = False
        alert.save()
        
        AuditLog.objects.create(
            user_name=request.user.username if request.user.is_authenticated else 'Admin',
            action='Dismiss Alert',
            target_model='Alert',
            target_id=str(alert.id),
            details=f"Dismissed alert: {alert.title}"
        )
        return Response({'success': True, 'message': 'Alert deactivated.'})

class AlertRequestChangeAPIView(APIView):
    """
    POST /api/alerts/request-change/ (EMERGENCY OPERATOR ONLY)
    Submits an alert change request for Admin review.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        if not is_admin_or_operator(request.user):
            return Response(
                {'success': False, 'error': 'Access Denied: Emergency Operator or Admin privileges required.'},
                status=status.HTTP_403_FORBIDDEN
            )

        action = request.data.get('requested_action', 'CREATE').upper()
        reason = request.data.get('reason', '').strip()
        alert_id = request.data.get('alert_id')

        if not reason:
            return Response({'success': False, 'error': 'A detailed reason is required for submitting an Alert Change Request.'}, status=status.HTTP_400_BAD_REQUEST)

        target_alert = None
        if alert_id:
            target_alert = Alert.objects.filter(pk=alert_id).first()

        req = AlertApprovalRequest.objects.create(
            operator=request.user,
            requested_action=action,
            alert=target_alert,
            title=request.data.get('title', ''),
            message=request.data.get('message', ''),
            severity=request.data.get('severity', 'CRITICAL'),
            disaster_type=request.data.get('disaster_type', 'FLOOD'),
            location_name=request.data.get('location_name', ''),
            recommended_action=request.data.get('recommended_action', ''),
            reason=reason,
            status='PENDING'
        )

        AuditLog.objects.create(
            user_name=request.user.username,
            action='Submit Alert Change Request',
            target_model='AlertApprovalRequest',
            target_id=str(req.id),
            details=f"Submitted {action} request for alert '{req.title or (target_alert.title if target_alert else '')}' (Status: PENDING)"
        )

        return Response({
            'success': True,
            'message': 'Alert Change Request submitted successfully. Pending Admin review.',
            'request_id': req.id,
            'status': 'PENDING'
        }, status=status.HTTP_201_CREATED)

class AdminAlertReviewAPIView(APIView):
    """
    POST /api/admin/alert-requests/<id>/review/ (ADMIN ONLY)
    Allows or Rejects an Emergency Operator Alert Change Request.
    """
    permission_classes = [IsAdminUserOrCommander]

    def post(self, request, pk):
        review_action = request.data.get('action', '').upper()
        if review_action not in ['ALLOW', 'REJECT']:
            return Response({'success': False, 'error': 'Invalid action. Must be ALLOW or REJECT.'}, status=status.HTTP_400_BAD_REQUEST)

        req = get_object_or_404(AlertApprovalRequest, pk=pk)
        if req.status != 'PENDING':
            return Response({'success': False, 'error': f'Request already reviewed (Status: {req.status}).'}, status=status.HTTP_400_BAD_REQUEST)

        if review_action == 'ALLOW':
            req.status = 'APPROVED'
            req.reviewed_by = request.user
            req.reviewed_at = timezone.now()
            req.save()

            # Execute approved action automatically
            if req.requested_action == 'CREATE':
                new_alert = Alert.objects.create(
                    title=req.title or 'Approved Emergency Alert',
                    severity=req.severity,
                    disaster_type=req.disaster_type,
                    location_name=req.location_name or 'Odisha Regional Sector',
                    message=req.message,
                    recommended_action=req.recommended_action or 'Follow official emergency guidelines.',
                    source=f"Issued by Operator ({req.operator.username}) — Admin Approved"
                )
                req.alert = new_alert
                req.save()

            elif req.requested_action == 'DEACTIVATE' and req.alert:
                req.alert.is_active = False
                req.alert.save()

            AuditLog.objects.create(
                user_name=request.user.username,
                action='Approve Alert Change Request',
                target_model='AlertApprovalRequest',
                target_id=str(req.id),
                details=f"ALLOWED {req.requested_action} request from operator {req.operator.username}"
            )
            return Response({'success': True, 'status': 'APPROVED', 'message': f'Request ALLOWED and {req.requested_action} executed.'})

        else:
            req.status = 'REJECTED'
            req.reviewed_by = request.user
            req.reviewed_at = timezone.now()
            req.save()

            AuditLog.objects.create(
                user_name=request.user.username,
                action='Reject Alert Change Request',
                target_model='AlertApprovalRequest',
                target_id=str(req.id),
                details=f"REJECTED {req.requested_action} request from operator {req.operator.username}"
            )
            return Response({'success': True, 'status': 'REJECTED', 'message': 'Request REJECTED.'})
