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
from .models import Claim
from .admin_report_generator import AdminReportGenerator
from django.views.decorators.http import require_GET
import csv
from io import BytesIO
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

try:
    # reportlab may not be installed in all environments; import lazily
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet
    REPORTLAB_AVAILABLE = True
except Exception:
    REPORTLAB_AVAILABLE = False


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
        
        # Add claimed order metrics
        claimed_count = Order.objects.filter(claimed_at__isnull=False).count()
        # Average time-to-claim in hours for claimed orders
        claimed_orders = Order.objects.filter(claimed_at__isnull=False).exclude(claimed_at=None)
        avg_time_to_claim_hours = None
        if claimed_orders.exists():
            total_seconds = 0
            count = 0
            for o in claimed_orders:
                if o.created_at and o.claimed_at:
                    diff = (o.claimed_at - o.created_at).total_seconds()
                    if diff >= 0:
                        total_seconds += diff
                        count += 1
            if count > 0:
                avg_time_to_claim_hours = (total_seconds / count) / 3600.0

        context = {
            'total_customers': total_customers,
            'total_tailors': total_tailors,
            'total_orders': total_orders,
            'total_tasks': total_tasks,
            'recent_orders': recent_orders,
            'recent_tasks': recent_tasks,
            'now': timezone.now(),
            'claimed_count': claimed_count,
            'avg_time_to_claim_hours': round(avg_time_to_claim_hours, 2) if avg_time_to_claim_hours is not None else None,
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
def admin_stats_claims(request):
    """Get claim-related statistics (claimed orders count and avg time-to-claim)."""
    try:
        end_date = timezone.now()
        start_date = end_date - timedelta(days=30)

        claimed_orders = Order.objects.filter(claimed_at__range=[start_date, end_date])
        claimed_count = claimed_orders.count()

        # Average time-to-claim in hours
        total_seconds = 0
        count = 0
        for o in claimed_orders:
            if o.created_at and o.claimed_at:
                diff = (o.claimed_at - o.created_at).total_seconds()
                if diff >= 0:
                    total_seconds += diff
                    count += 1

        avg_time_to_claim_hours = (total_seconds / count) / 3600.0 if count > 0 else None

        return Response({
            'claimed_count': claimed_count,
            'avg_time_to_claim_hours': round(avg_time_to_claim_hours, 2) if avg_time_to_claim_hours is not None else None,
            'period': 'Last 30 days'
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


@login_required
@staff_member_required
def admin_claims_page(request):
    """Render a page listing claim audit records with filtering and search."""
    try:
        # Filters
        order_id = request.GET.get('order_id')
        claimant = request.GET.get('claimant')
        claimant_phone = request.GET.get('claimant_phone')
        recorded_by = request.GET.get('recorded_by')
        date_from = request.GET.get('date_from')
        date_to = request.GET.get('date_to')

        qs = Claim.objects.select_related('order__customer__user', 'recorded_by').order_by('-recorded_at')

        if order_id:
            qs = qs.filter(order__id=order_id)
        if claimant:
            qs = qs.filter(claimant_name__icontains=claimant)
        if claimant_phone:
            qs = qs.filter(claimant_phone__icontains=claimant_phone)
        if recorded_by:
            qs = qs.filter(recorded_by__username__icontains=recorded_by)
        if date_from:
            try:
                from django.utils.dateparse import parse_date
                d = parse_date(date_from)
                if d:
                    qs = qs.filter(recorded_at__date__gte=d)
            except Exception:
                pass
        if date_to:
            try:
                from django.utils.dateparse import parse_date
                d = parse_date(date_to)
                if d:
                    qs = qs.filter(recorded_at__date__lte=d)
            except Exception:
                pass

        # Paginate results
        page = request.GET.get('page', 1)
        per_page = 25
        paginator = Paginator(qs, per_page)
        try:
            claims_page = paginator.page(page)
        except PageNotAnInteger:
            claims_page = paginator.page(1)
        except EmptyPage:
            claims_page = paginator.page(paginator.num_pages)

        context = {
            'claims': claims_page.object_list,
            'page_obj': claims_page,
            'paginator': paginator,
            'filters': {
                'order_id': order_id or '',
                'claimant': claimant or '',
                'claimant_phone': claimant_phone or '',
                'recorded_by': recorded_by or '',
                'date_from': date_from or '',
                'date_to': date_to or '',
            }
        }
        return render(request, 'admin_claims.html', context)
    except Exception as e:
        return HttpResponse(f"Error loading claims page: {str(e)}", status=500)


@login_required
@staff_member_required
@require_GET
def export_claims_report(request):
    """Export filtered claims as PDF or CSV.

    Query parameters mirror `admin_claims_page`. Use `format=pdf|csv`.
    """
    try:
        fmt = request.GET.get('format', 'pdf').lower()

        # Reuse the filtering logic from admin_claims_page
        order_id = request.GET.get('order_id')
        claimant = request.GET.get('claimant')
        claimant_phone = request.GET.get('claimant_phone')
        recorded_by = request.GET.get('recorded_by')
        date_from = request.GET.get('date_from')
        date_to = request.GET.get('date_to')

        qs = Claim.objects.select_related('order__customer__user', 'recorded_by').order_by('-recorded_at')
        if order_id:
            qs = qs.filter(order__id=order_id)
        if claimant:
            qs = qs.filter(claimant_name__icontains=claimant)
        if claimant_phone:
            qs = qs.filter(claimant_phone__icontains=claimant_phone)
        if recorded_by:
            qs = qs.filter(recorded_by__username__icontains=recorded_by)
        if date_from:
            try:
                from django.utils.dateparse import parse_date
                d = parse_date(date_from)
                if d:
                    qs = qs.filter(recorded_at__date__gte=d)
            except Exception:
                pass
        if date_to:
            try:
                from django.utils.dateparse import parse_date
                d = parse_date(date_to)
                if d:
                    qs = qs.filter(recorded_at__date__lte=d)
            except Exception:
                pass

        results = list(qs)

        if fmt == 'csv':
            # Build CSV
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="claims.csv"'
            writer = csv.writer(response)
            writer.writerow(['Claim ID', 'Order ID', 'Customer', 'Claimant Name', 'Claimant Phone', 'Recorded By', 'Recorded At', 'Notes', 'Reversed'])
            for c in results:
                cust_name = c.order.customer.user.get_full_name() if getattr(c.order, 'customer', None) and getattr(c.order.customer, 'user', None) else ''
                writer.writerow([c.id, c.order.id if c.order else '', cust_name, c.claimant_name, c.claimant_phone, c.recorded_by.get_full_name() if c.recorded_by else '', c.recorded_at.isoformat() if c.recorded_at else '', c.notes, c.reversed])
            return response

        # Default: PDF
        if not REPORTLAB_AVAILABLE:
            return HttpResponse('PDF export is not available on this server. Install reportlab.', status=500)

        buffer = BytesIO()
        # Tight margins to allow more columns
        doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=30, rightMargin=30, topMargin=70, bottomMargin=40)
        elements = []
        styles = getSampleStyleSheet()

        # Table header + rows
        data = [['Claim ID', 'Order ID', 'Customer', 'Claimant', 'Phone', 'Recorded By', 'Recorded At', 'Notes', 'Reversed']]
        for c in results:
            cust_name = c.order.customer.user.get_full_name() if getattr(c.order, 'customer', None) and getattr(c.order.customer, 'user', None) else ''
            recorded_by = c.recorded_by.get_full_name() if c.recorded_by else ''
            recorded_at = c.recorded_at.strftime('%Y-%m-%d %H:%M') if c.recorded_at else ''
            data.append([str(c.id), str(c.order.id if c.order else ''), cust_name, c.claimant_name, c.claimant_phone, recorded_by, recorded_at, (c.notes[:80] + '...') if c.notes and len(c.notes) > 80 else (c.notes or ''), 'Yes' if c.reversed else 'No'])

        # Estimate column widths to fit A4 with margins (approx. 535pt usable width)
        col_widths = [36, 36, 90, 70, 46, 64, 64, 100, 20]
        table = Table(data, colWidths=col_widths, repeatRows=1)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#d3d3d3')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.black),
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1, -1), 8),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('BOTTOMPADDING', (0,0), (-1,0), 6),
            ('LEFTPADDING', (0,0), (-1,-1), 4),
            ('RIGHTPADDING', (0,0), (-1,-1), 4),
        ]))
        elements.append(table)

        # Draw header and footer on each page
        def draw_header(canvas, doc):
            canvas.saveState()
            # Title
            canvas.setFont('Helvetica-Bold', 14)
            canvas.drawString(36, A4[1] - 50, 'Claims Report')
            # Generated timestamp
            canvas.setFont('Helvetica', 8)
            canvas.drawString(36, A4[1] - 62, f'Generated: {timezone.now().strftime("%Y-%m-%d %H:%M")}')
            # Page number
            page_num = canvas.getPageNumber()
            canvas.drawRightString(A4[0] - 36, 30, f'Page {page_num}')
            canvas.restoreState()

        doc.build(elements, onFirstPage=draw_header, onLaterPages=draw_header)
        pdf = buffer.getvalue()
        buffer.close()

        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="claims_report.pdf"'
        return response

    except Exception as e:
        return HttpResponse(f"Error exporting claims: {str(e)}", status=500)


@login_required
@staff_member_required
@require_GET
def admin_claims_api(request):
    """JSON API for claims with filtering, sorting and pagination for AJAX use."""
    try:
        # Filters
        order_id = request.GET.get('order_id')
        claimant = request.GET.get('claimant')
        claimant_phone = request.GET.get('claimant_phone')
        recorded_by = request.GET.get('recorded_by')
        date_from = request.GET.get('date_from')
        date_to = request.GET.get('date_to')
        # Sorting: field and direction
        sort_field = request.GET.get('sort', 'recorded_at')
        sort_dir = request.GET.get('dir', 'desc')

        qs = Claim.objects.select_related('order__customer__user', 'recorded_by')

        if order_id:
            qs = qs.filter(order__id=order_id)
        if claimant:
            qs = qs.filter(claimant_name__icontains=claimant)
        if claimant_phone:
            qs = qs.filter(claimant_phone__icontains=claimant_phone)
        if recorded_by:
            qs = qs.filter(recorded_by__username__icontains=recorded_by)
        if date_from:
            try:
                from django.utils.dateparse import parse_date
                d = parse_date(date_from)
                if d:
                    qs = qs.filter(recorded_at__date__gte=d)
            except Exception:
                pass
        if date_to:
            try:
                from django.utils.dateparse import parse_date
                d = parse_date(date_to)
                if d:
                    qs = qs.filter(recorded_at__date__lte=d)
            except Exception:
                pass

        # Sorting
        allowed = {'recorded_at', 'claimant_name', 'order__id'}
        if sort_field not in allowed:
            sort_field = 'recorded_at'
        order_by = ('-' + sort_field) if sort_dir == 'desc' else sort_field
        qs = qs.order_by(order_by)

        # Pagination
        page = int(request.GET.get('page', 1))
        per_page = int(request.GET.get('per_page', 25))
        from django.core.paginator import Paginator
        paginator = Paginator(qs, per_page)
        try:
            page_obj = paginator.page(page)
        except Exception:
            page_obj = paginator.page(1)

        items = []
        for c in page_obj.object_list:
            cust = ''
            try:
                cust = c.order.customer.user.get_full_name()
            except Exception:
                cust = ''
            items.append({
                'id': c.id,
                'order_id': c.order.id if c.order else None,
                'customer': cust,
                'claimant_name': c.claimant_name,
                'claimant_phone': c.claimant_phone,
                'recorded_by': c.recorded_by.get_full_name() if c.recorded_by else None,
                'recorded_at': c.recorded_at.isoformat() if c.recorded_at else None,
                'notes': c.notes,
                'reversed': c.reversed,
            })

        return JsonResponse({
            'results': items,
            'count': paginator.count,
            'page': page_obj.number,
            'num_pages': paginator.num_pages,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous(),
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
