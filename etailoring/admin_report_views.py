from datetime import datetime, timedelta
from decimal import Decimal
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.db.models import Sum, Count, Avg, Q
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from .models import Order, Task, Commission, Customer, Tailor, Fabric, Accessory
from .admin_report_generator import AdminReportGenerator


@login_required
@staff_member_required
def admin_reports_page(request):
    """Show the admin reports dashboard"""
    try:
        # Get basic stats for the dashboard
        total_customers = Customer.objects.count()
        total_tailors = Tailor.objects.count()
        total_orders = Order.objects.count()
        total_tasks = Task.objects.count()
        
        # Get recent activity
        recent_orders = Order.objects.order_by('-created_at')[:5]
        recent_tasks = Task.objects.order_by('-assigned_at')[:5]
        
        context = {
            'total_customers': total_customers,
            'total_tailors': total_tailors,
            'total_orders': total_orders,
            'total_tasks': total_tasks,
            'recent_orders': recent_orders,
            'recent_tasks': recent_tasks,
            'now': timezone.now(),
        }
        
        return render(request, 'admin_reports.html', context)
        
    except Exception as e:
        return HttpResponse(f"Error loading admin reports page: {str(e)}", status=500)


@login_required
@staff_member_required
def generate_admin_report(request, report_type):
    """Generate admin report PDF"""
    try:
        # Get date range parameters
        date_from_str = request.GET.get('date_from')
        date_to_str = request.GET.get('date_to')
        period = request.GET.get('period', 'last_month')
        # Output format (pdf or csv)
        format_type = request.GET.get('format', 'pdf')
        
        # Parse date range
        if date_from_str and date_to_str:
            try:
                date_from = datetime.strptime(date_from_str, '%Y-%m-%d').date()
                date_to = datetime.strptime(date_to_str, '%Y-%m-%d').date()
            except ValueError:
                return HttpResponse("Invalid date format. Use YYYY-MM-DD.", status=400)
        else:
            # Use predefined periods
            today = timezone.now().date()
            if period == 'last_week':
                date_from = today - timedelta(days=7)
                date_to = today
            elif period == 'last_quarter':
                date_from = today - timedelta(days=90)
                date_to = today
            elif period == 'ytd':
                date_from = today.replace(month=1, day=1)
                date_to = today
            elif period == 'all_time':
                date_from = timezone.datetime(2020, 1, 1).date()
                date_to = today
            else:  # last_month
                date_from = today - timedelta(days=30)
                date_to = today
        
        # Convert to datetime with timezone
        date_from = timezone.make_aware(datetime.combine(date_from, datetime.min.time()))
        date_to = timezone.make_aware(datetime.combine(date_to, datetime.max.time()))
        
        # Handle special parameters for specific report types
        kwargs = {}
        # Always pass requested format through to the generator
        kwargs['format'] = format_type
        if report_type == 'tailor':
            tailor_id = request.GET.get('tailor_id')
            if not tailor_id:
                return HttpResponse("Tailor ID required for tailor reports", status=400)
            kwargs['tailor_id'] = tailor_id
        elif report_type == 'custom':
            metrics = request.GET.getlist('metrics')
            kwargs['metrics'] = metrics
            # format already set in kwargs above
        
        # Generate report
        report_generator = AdminReportGenerator(
            report_type=report_type,
            date_from=date_from,
            date_to=date_to,
            generated_by=request.user,
            **kwargs
        )
        
        data = report_generator.generate_report()
        filename = report_generator.get_filename()

        # Choose content type based on requested format
        if format_type == 'csv':
            content_type = 'text/csv'
            # ensure filename ends with .csv
            if not filename.lower().endswith('.csv'):
                filename = filename.rsplit('.', 1)[0] + '.csv'
        else:
            content_type = 'application/pdf'
            if not filename.lower().endswith('.pdf'):
                filename = filename.rsplit('.', 1)[0] + '.pdf'

        response = HttpResponse(data, content_type=content_type)
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
        
    except Exception as e:
        return HttpResponse(f"Error generating report: {str(e)}", status=500)


# API endpoints for dashboard data
@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def admin_stats_revenue(request):
    """Get revenue statistics"""
    try:
        # Get date range (default to last 30 days)
        end_date = timezone.now()
        start_date = end_date - timedelta(days=30)
        
        orders = Order.objects.filter(created_at__range=[start_date, end_date])
        total_revenue = orders.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        
        return Response({
            'total_revenue': float(total_revenue),
            'period': 'Last 30 days'
        })
    except Exception as e:
        return Response({'error': str(e)}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def admin_stats_orders(request):
    """Get order statistics"""
    try:
        # Get active orders (not completed or cancelled)
        active_orders = Order.objects.exclude(status__in=['COMPLETED', 'CANCELLED']).count()
        
        return Response({
            'active_orders': active_orders
        })
    except Exception as e:
        return Response({'error': str(e)}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def admin_stats_commissions(request):
    """Get commission statistics"""
    try:
        # Get date range (default to last 30 days)
        end_date = timezone.now()
        start_date = end_date - timedelta(days=30)
        
        commissions = Commission.objects.filter(created_at__range=[start_date, end_date])
        total_commissions = commissions.aggregate(Sum('amount'))['amount__sum'] or 0
        
        return Response({
            'total_commissions': float(total_commissions),
            'period': 'Last 30 days'
        })
    except Exception as e:
        return Response({'error': str(e)}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def admin_stats_tailors(request):
    """Get tailor statistics"""
    try:
        # Get active tailors (those with tasks in last 30 days)
        end_date = timezone.now()
        start_date = end_date - timedelta(days=30)
        
        active_tailors = Tailor.objects.filter(
            task__assigned_at__range=[start_date, end_date]
        ).distinct().count()
        
        return Response({
            'active_tailors': active_tailors
        })
    except Exception as e:
        return Response({'error': str(e)}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def admin_charts_revenue(request):
    """Get revenue chart data"""
    try:
        # Get last 12 months of revenue data
        end_date = timezone.now()
        start_date = end_date - timedelta(days=365)
        
        # Group by month
        monthly_revenue = {}
        orders = Order.objects.filter(created_at__range=[start_date, end_date])
        
        for order in orders:
            month_key = order.created_at.strftime('%Y-%m')
            if month_key not in monthly_revenue:
                monthly_revenue[month_key] = 0
            monthly_revenue[month_key] += float(order.total_amount or 0)
        
        # Sort by month and prepare data
        sorted_months = sorted(monthly_revenue.keys())
        labels = [datetime.strptime(month, '%Y-%m').strftime('%b %Y') for month in sorted_months]
        values = [monthly_revenue[month] for month in sorted_months]
        
        return Response({
            'labels': labels,
            'values': values
        })
    except Exception as e:
        return Response({'error': str(e)}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def admin_charts_orders(request):
    """Get orders chart data"""
    try:
        # Get order status distribution
        orders = Order.objects.all()
        status_counts = {}
        
        for order in orders:
            status = order.status
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Prepare data for doughnut chart
        labels = [status.replace('_', ' ').title() for status in status_counts.keys()]
        values = list(status_counts.values())
        
        return Response({
            'labels': labels,
            'values': values
        })
    except Exception as e:
        return Response({'error': str(e)}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def admin_recent_activity(request):
    """Get recent activity data"""
    try:
        activities = []
        
        # Recent orders
        recent_orders = Order.objects.order_by('-created_at')[:5]
        for order in recent_orders:
            activities.append({
                'type': 'order',
                'description': f"New order #{order.id} from {order.customer.user.get_full_name()}",
                'timestamp': order.created_at.isoformat()
            })
        
        # Recent tasks
        recent_tasks = Task.objects.order_by('-assigned_at')[:5]
        for task in recent_tasks:
            activities.append({
                'type': 'task',
                'description': f"Task assigned to {task.tailor.user.get_full_name()}",
                'timestamp': task.assigned_at.isoformat()
            })
        
        # Recent commissions
        recent_commissions = Commission.objects.order_by('-created_at')[:5]
        for commission in recent_commissions:
            activities.append({
                'type': 'commission',
                'description': f"Commission of PHP {commission.amount} for {commission.tailor.user.get_full_name()}",
                'timestamp': commission.created_at.isoformat()
            })
        
        # Sort by timestamp and return latest 10
        activities.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return Response({
            'results': activities[:10]
        })
    except Exception as e:
        return Response({'error': str(e)}, status=500)
