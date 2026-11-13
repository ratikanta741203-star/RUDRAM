from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from apps.resources.models import Resource, ResourceAllocation, RescueTeam, ApprovalRequest
from apps.resources.serializers import ResourceSerializer, ResourceAllocationSerializer, RescueTeamSerializer
from apps.accounts.permissions import is_strict_admin, is_operator, is_admin_or_operator, IsAdminOrOperatorOrReadOnly
from apps.core.models import AuditLog


def resources_view(request):
    """
    Resources & Rescue Operations page.
    Renders public inventory and operational controls according to User Role:
    - CITIZEN: View-only
    - EMERGENCY OPERATOR: Operational controls + approval request submission + Operator Request History
    - ADMIN: Direct management + link to Admin Command Center approvals
    """
    resources = Resource.objects.all()
    allocations = ResourceAllocation.objects.all()[:15]
    rescue_teams = RescueTeam.objects.all()

    total_avail = sum(r.quantity_available for r in resources)
    total_req = sum(r.quantity_required for r in resources)
    total_alloc = sum(r.quantity_allocated for r in resources)

    user_role = 'CITIZEN'
    operator_requests = None
    pending_count = 0

    if request.user.is_authenticated:
        if is_strict_admin(request.user):
            user_role = 'ADMIN'
            pending_count = ApprovalRequest.objects.filter(status='PENDING').count()
        elif is_operator(request.user):
            user_role = 'EMERGENCY_OPERATOR'
            operator_requests = ApprovalRequest.objects.filter(requested_by=request.user)[:15]

    context = {
        'resources': resources,
        'allocations': allocations,
        'rescue_teams': rescue_teams,
        'total_avail': total_avail,
        'total_req': total_req,
        'total_alloc': total_alloc,
        'user_role': user_role,
        'operator_requests': operator_requests,
        'pending_count': pending_count,
        'page_title': 'Resource Inventory & Rescue Operations'
    }
    return render(request, 'resources/index.html', context)


def dispatch_resource_view(request):
    """
    POST /resources/dispatch/
    - CITIZEN: 403 Forbidden
    - OPERATOR: Creates PENDING ApprovalRequest (no database change until Admin approves)
    - ADMIN: Direct dispatch & inventory deduction
    """
    if request.method != 'POST':
        return redirect('resources')

    if not request.user.is_authenticated or not is_admin_or_operator(request.user):
        raise PermissionDenied("Access Denied: Operational privileges required.")

    res_id = request.POST.get('resource_id')
    qty = int(request.POST.get('quantity', 0))
    zone = request.POST.get('destination_zone', 'Emergency Field Zone')
    reason = request.POST.get('notes', 'Priority emergency relief dispatch')

    resource = get_object_or_404(Resource, pk=res_id)

    if is_operator(request.user):
        # Create Pending Approval Request (Do NOT update Resource DB directly)
        ApprovalRequest.objects.create(
            requested_by=request.user,
            request_type='RESOURCE_DISPATCH',
            target_model='Resource',
            target_object_id=resource.id,
            target_object_name=resource.name,
            requested_changes={'quantity': qty, 'destination_zone': zone, 'notes': reason},
            current_values={'quantity_available': resource.quantity_available, 'quantity_allocated': resource.quantity_allocated},
            reason=reason,
            status='PENDING'
        )
        AuditLog.objects.create(
            user_name=request.user.username,
            action='REQUEST_DISPATCH',
            target_model='ApprovalRequest',
            details=f"Operator requested dispatch of {qty} {resource.unit} of {resource.name} to {zone} (Pending Admin Approval)"
        )
        messages.info(request, f"Dispatch request for {qty} {resource.unit} of {resource.name} submitted for Admin approval. Stock will remain unchanged until approved.")
        return redirect('resources')

    # ADMIN Direct Dispatch
    if resource.quantity_available < qty:
        messages.error(request, f"Insufficient stock: Only {resource.quantity_available} {resource.unit} available.")
        return redirect('resources')

    resource.quantity_available -= qty
    resource.quantity_allocated += qty
    resource.save()

    ResourceAllocation.objects.create(
        resource=resource,
        quantity=qty,
        destination_zone=zone,
        requester_name=request.user.username,
        status='DISPATCHED',
        notes=reason
    )

    AuditLog.objects.create(
        user_name=request.user.username,
        action='DISPATCH_RESOURCE',
        target_model='ResourceAllocation',
        details=f"Admin dispatched {qty} {resource.unit} of {resource.name} to {zone}"
    )

    messages.success(request, f"Successfully dispatched {qty} {resource.unit} of {resource.name} to {zone}.")
    return redirect('resources')


def update_stock_view(request):
    """
    POST /resources/update-stock/
    - CITIZEN: 403 Forbidden
    - OPERATOR: Creates PENDING ApprovalRequest
    - ADMIN: Direct inventory update
    """
    if request.method != 'POST':
        return redirect('resources')

    if not request.user.is_authenticated or not is_admin_or_operator(request.user):
        raise PermissionDenied("Access Denied: Operational privileges required.")

    res_id = request.POST.get('resource_id')
    qty_avail = int(request.POST.get('quantity_available', 0))
    qty_req = int(request.POST.get('quantity_required', 0))
    location = request.POST.get('warehouse_location', '')

    resource = get_object_or_404(Resource, pk=res_id)

    if is_operator(request.user):
        ApprovalRequest.objects.create(
            requested_by=request.user,
            request_type='RESOURCE_STOCK_UPDATE',
            target_model='Resource',
            target_object_id=resource.id,
            target_object_name=resource.name,
            requested_changes={'quantity_available': qty_avail, 'quantity_required': qty_req, 'warehouse_location': location},
            current_values={'quantity_available': resource.quantity_available, 'quantity_required': resource.quantity_required, 'warehouse_location': resource.warehouse_location},
            reason='Operator inventory adjustment request',
            status='PENDING'
        )
        AuditLog.objects.create(
            user_name=request.user.username,
            action='REQUEST_STOCK_UPDATE',
            target_model='ApprovalRequest',
            details=f"Operator requested stock update for {resource.name} (Pending Admin Approval)"
        )
        messages.info(request, f"Stock update request for {resource.name} submitted for Admin approval.")
        return redirect('resources')

    # ADMIN Direct Update
    resource.quantity_available = qty_avail
    resource.quantity_required = qty_req
    if location:
        resource.warehouse_location = location
    resource.save()

    AuditLog.objects.create(
        user_name=request.user.username,
        action='UPDATE_RESOURCE_STOCK',
        target_model='Resource',
        details=f"Admin updated stock for {resource.name}: Available={qty_avail}"
    )

    messages.success(request, f"Stock for {resource.name} updated successfully.")
    return redirect('resources')


def update_team_status_view(request):
    """
    POST /resources/team-status/
    - CITIZEN: 403 Forbidden
    - OPERATOR: Creates PENDING ApprovalRequest
    - ADMIN: Direct status update
    """
    if request.method != 'POST':
        return redirect('resources')

    if not request.user.is_authenticated or not is_admin_or_operator(request.user):
        raise PermissionDenied("Access Denied: Operational privileges required.")

    team_id = request.POST.get('team_id')
    new_status = request.POST.get('status', 'AVAILABLE')

    team = get_object_or_404(RescueTeam, pk=team_id)

    if is_operator(request.user):
        ApprovalRequest.objects.create(
            requested_by=request.user,
            request_type='TEAM_STATUS_UPDATE',
            target_model='RescueTeam',
            target_object_id=team.id,
            target_object_name=team.name,
            requested_changes={'status': new_status},
            current_values={'status': team.status},
            reason=f"Operator team status change to {new_status}",
            status='PENDING'
        )
        AuditLog.objects.create(
            user_name=request.user.username,
            action='REQUEST_TEAM_STATUS_UPDATE',
            target_model='ApprovalRequest',
            details=f"Operator requested status change for {team.name} to {new_status} (Pending Admin Approval)"
        )
        messages.info(request, f"Status update request for {team.name} ({new_status}) submitted for Admin approval.")
        return redirect('resources')

    # ADMIN Direct Update
    team.status = new_status
    team.save()

    AuditLog.objects.create(
        user_name=request.user.username,
        action='UPDATE_TEAM_STATUS',
        target_model='RescueTeam',
        details=f"Admin updated rescue team {team.name} status to {new_status}"
    )

    messages.success(request, f"Status for {team.name} updated to {new_status}.")
    return redirect('resources')


class ResourceListAPIView(APIView):
    def get(self, request):
        resources = Resource.objects.all()
        serializer = ResourceSerializer(resources, many=True)
        return Response({'success': True, 'resources': serializer.data})


class ResourceAllocateAPIView(APIView):
    """
    POST /api/resources/allocate/
    - CITIZEN: 403 Forbidden
    - OPERATOR: Creates PENDING ApprovalRequest (returns 202 Accepted)
    - ADMIN: Direct dispatch (returns 201 Created)
    """
    permission_classes = [IsAdminOrOperatorOrReadOnly]

    def post(self, request):
        if not is_admin_or_operator(request.user):
            return Response({'success': False, 'error': 'Access Denied: Operational privileges required.'}, status=status.HTTP_403_FORBIDDEN)

        res_id = request.data.get('resource_id')
        qty = int(request.data.get('quantity', 0))
        zone = request.data.get('destination_zone', 'Impact Zone A')
        notes = request.data.get('notes', 'Priority emergency relief deployment')

        resource = get_object_or_404(Resource, pk=res_id)

        if is_operator(request.user):
            req_obj = ApprovalRequest.objects.create(
                requested_by=request.user,
                request_type='RESOURCE_DISPATCH',
                target_model='Resource',
                target_object_id=resource.id,
                target_object_name=resource.name,
                requested_changes={'quantity': qty, 'destination_zone': zone, 'notes': notes},
                current_values={'quantity_available': resource.quantity_available, 'quantity_allocated': resource.quantity_allocated},
                reason=notes,
                status='PENDING'
            )
            return Response({
                'success': True,
                'pending': True,
                'approval_request_id': req_obj.id,
                'message': 'Dispatch request submitted for Admin approval. Inventory remains unchanged.'
            }, status=status.HTTP_202_ACCEPTED)

        # ADMIN Direct Dispatch
        if resource.quantity_available < qty:
            return Response({
                'success': False,
                'error': f"Insufficient stock: Only {resource.quantity_available} {resource.unit} available."
            }, status=status.HTTP_400_BAD_REQUEST)

        resource.quantity_available -= qty
        resource.quantity_allocated += qty
        resource.save()

        allocation = ResourceAllocation.objects.create(
            resource=resource,
            quantity=qty,
            destination_zone=zone,
            requester_name=request.user.username,
            status='DISPATCHED',
            notes=notes
        )

        AuditLog.objects.create(
            user_name=request.user.username,
            action='Allocate Emergency Resource',
            target_model='ResourceAllocation',
            target_id=str(allocation.id),
            details=f"Admin dispatched {qty} {resource.unit} of {resource.name} to {zone}"
        )

        return Response({
            'success': True,
            'allocation': ResourceAllocationSerializer(allocation).data,
            'remaining_available': resource.quantity_available
        }, status=status.HTTP_201_CREATED)


class RescueTeamListAPIView(APIView):
    def get(self, request):
        teams = RescueTeam.objects.all()
        serializer = RescueTeamSerializer(teams, many=True)
        return Response({'success': True, 'rescue_teams': serializer.data})
