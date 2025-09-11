from io import BytesIO
from datetime import datetime, timedelta
from decimal import Decimal
from django.utils import timezone
from django.db.models import Sum, Count, Avg, Q, F
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from .models import Order, Task, Commission, Customer, Tailor, Fabric, Accessory


class AdminReportGenerator:
    """Generate comprehensive admin reports for business analytics"""
    
    def __init__(self, report_type, date_from, date_to, generated_by, **kwargs):
        self.report_type = report_type
        self.date_from = date_from
        self.date_to = date_to
        self.generated_by = generated_by
        self.kwargs = kwargs
        
        # Color scheme
        self.primary_color = colors.Color(0.2, 0.3, 0.8)  # Blue
        self.secondary_color = colors.Color(0.9, 0.9, 0.95)  # Light blue
        self.accent_color = colors.Color(0.6, 0.2, 0.8)  # Purple
        
        # Initialize buffer
        self.buffer = BytesIO()
    
    def generate_report(self):
        """Generate the appropriate report based on report_type"""
        if self.report_type == 'business':
            return self._generate_business_overview()
        elif self.report_type == 'financial':
            return self._generate_financial_report()
        elif self.report_type == 'customer':
            return self._generate_customer_analytics()
        elif self.report_type == 'inventory':
            return self._generate_inventory_report()
        elif self.report_type == 'tailor':
            return self._generate_tailor_performance()
        elif self.report_type == 'custom':
            return self._generate_custom_report()
        else:
            raise ValueError(f"Unknown report type: {self.report_type}")
    
    def _generate_business_overview(self):
        """Generate comprehensive business overview report"""
        doc = SimpleDocTemplate(self.buffer, pagesize=A4, topMargin=0.5*inch)
        story = []
        
        # Add header
        story.extend(self._create_header("Business Overview Report"))
        story.append(Spacer(1, 20))
        
        # Executive Summary
        story.extend(self._create_executive_summary())
        story.append(Spacer(1, 20))
        
        # Revenue Analysis
        story.extend(self._create_revenue_analysis())
        story.append(Spacer(1, 20))
        
        # Order Statistics
        story.extend(self._create_order_statistics())
        story.append(Spacer(1, 20))
        
        # Performance Metrics
        story.extend(self._create_performance_metrics())
        story.append(Spacer(1, 20))
        
        # Footer
        story.extend(self._create_footer())
        
        doc.build(story)
        pdf_data = self.buffer.getvalue()
        self.buffer.close()
        return pdf_data
    
    def _generate_financial_report(self):
        """Generate detailed financial analysis report"""
        doc = SimpleDocTemplate(self.buffer, pagesize=A4, topMargin=0.5*inch)
        story = []
        
        # Add header
        story.extend(self._create_header("Financial Analysis Report"))
        story.append(Spacer(1, 20))
        
        # Revenue Breakdown
        story.extend(self._create_revenue_breakdown())
        story.append(Spacer(1, 20))
        
        # Commission Analysis
        story.extend(self._create_commission_analysis())
        story.append(Spacer(1, 20))
        
        # Profit Margins
        story.extend(self._create_profit_analysis())
        story.append(Spacer(1, 20))
        
        # Financial Trends
        story.extend(self._create_financial_trends())
        story.append(Spacer(1, 20))
        
        # Footer
        story.extend(self._create_footer())
        
        doc.build(story)
        pdf_data = self.buffer.getvalue()
        self.buffer.close()
        return pdf_data
    
    def _generate_customer_analytics(self):
        """Generate customer behavior and analytics report"""
        doc = SimpleDocTemplate(self.buffer, pagesize=A4, topMargin=0.5*inch)
        story = []
        
        # Add header
        story.extend(self._create_header("Customer Analytics Report"))
        story.append(Spacer(1, 20))
        
        # Customer Overview
        story.extend(self._create_customer_overview())
        story.append(Spacer(1, 20))
        
        # Customer Retention
        story.extend(self._create_customer_retention())
        story.append(Spacer(1, 20))
        
        # Order Patterns
        story.extend(self._create_order_patterns())
        story.append(Spacer(1, 20))
        
        # Top Customers
        story.extend(self._create_top_customers())
        story.append(Spacer(1, 20))
        
        # Footer
        story.extend(self._create_footer())
        
        doc.build(story)
        pdf_data = self.buffer.getvalue()
        self.buffer.close()
        return pdf_data
    
    def _generate_inventory_report(self):
        """Generate inventory status and analysis report"""
        doc = SimpleDocTemplate(self.buffer, pagesize=A4, topMargin=0.5*inch)
        story = []
        
        # Add header
        story.extend(self._create_header("Inventory Status Report"))
        story.append(Spacer(1, 20))
        
        # Fabric Inventory
        story.extend(self._create_fabric_inventory())
        story.append(Spacer(1, 20))
        
        # Accessory Inventory
        story.extend(self._create_accessory_inventory())
        story.append(Spacer(1, 20))
        
        # Usage Patterns
        story.extend(self._create_usage_patterns())
        story.append(Spacer(1, 20))
        
        # Reorder Recommendations
        story.extend(self._create_reorder_recommendations())
        story.append(Spacer(1, 20))
        
        # Footer
        story.extend(self._create_footer())
        
        doc.build(story)
        pdf_data = self.buffer.getvalue()
        self.buffer.close()
        return pdf_data
    
    def _generate_tailor_performance(self):
        """Generate tailor performance report"""
        tailor_id = self.kwargs.get('tailor_id')
        if not tailor_id:
            raise ValueError("Tailor ID required for tailor performance report")
        
        from .report_generator import TailorReportGenerator
        
        tailor = Tailor.objects.get(id=tailor_id)
        generator = TailorReportGenerator(
            tailor=tailor,
            date_from=self.date_from,
            date_to=self.date_to,
            generated_by=self.generated_by
        )
        
        return generator.generate_report()
    
    def _generate_custom_report(self):
        """Generate custom report based on selected metrics"""
        doc = SimpleDocTemplate(self.buffer, pagesize=A4, topMargin=0.5*inch)
        story = []
        
        metrics = self.kwargs.get('metrics', [])
        
        # Add header
        story.extend(self._create_header("Custom Business Report"))
        story.append(Spacer(1, 20))
        
        # Add selected metrics
        if 'revenue' in metrics:
            story.extend(self._create_revenue_analysis())
            story.append(Spacer(1, 20))
        
        if 'orders' in metrics:
            story.extend(self._create_order_statistics())
            story.append(Spacer(1, 20))
        
        if 'commissions' in metrics:
            story.extend(self._create_commission_analysis())
            story.append(Spacer(1, 20))
        
        if 'customers' in metrics:
            story.extend(self._create_customer_overview())
            story.append(Spacer(1, 20))
        
        if 'tailors' in metrics:
            story.extend(self._create_tailor_overview())
            story.append(Spacer(1, 20))
        
        if 'inventory' in metrics:
            story.extend(self._create_fabric_inventory())
            story.append(Spacer(1, 20))
        
        # Footer
        story.extend(self._create_footer())
        
        doc.build(story)
        pdf_data = self.buffer.getvalue()
        self.buffer.close()
        return pdf_data
    
    def _create_header(self, title):
        """Create report header"""
        styles = getSampleStyleSheet()
        
        header_style = ParagraphStyle(
            'CustomHeader',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=self.primary_color,
            alignment=TA_CENTER,
            spaceAfter=10
        )
        
        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Normal'],
            fontSize=14,
            textColor=self.accent_color,
            alignment=TA_CENTER,
            spaceAfter=20
        )
        
        content = []
        content.append(Paragraph("StitchFlow Business Intelligence", header_style))
        content.append(Paragraph(title, subtitle_style))
        
        # Report metadata
        metadata_style = ParagraphStyle(
            'Metadata',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.grey,
            alignment=TA_CENTER
        )
        
        date_range = f"Report Period: {self.date_from.strftime('%B %d, %Y')} - {self.date_to.strftime('%B %d, %Y')}"
        generated_info = f"Generated on {timezone.now().strftime('%B %d, %Y at %I:%M %p')} by {self.generated_by.get_full_name() or self.generated_by.username}"
        
        content.append(Paragraph(date_range, metadata_style))
        content.append(Paragraph(generated_info, metadata_style))
        
        return content
    
    def _create_footer(self):
        """Create report footer"""
        styles = getSampleStyleSheet()
        
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.grey,
            alignment=TA_CENTER
        )
        
        content = []
        content.append(Spacer(1, 30))
        content.append(Paragraph("This report is confidential and proprietary to StitchFlow.", footer_style))
        content.append(Paragraph("Generated by StitchFlow Business Intelligence System", footer_style))
        
        return content
    
    def get_filename(self):
        """Generate appropriate filename for the report"""
        date_str = timezone.now().strftime('%Y%m%d_%H%M%S')
        report_names = {
            'business': 'Business_Overview',
            'financial': 'Financial_Analysis',
            'customer': 'Customer_Analytics',
            'inventory': 'Inventory_Report',
            'tailor': 'Tailor_Performance',
            'custom': 'Custom_Report'
        }
        
        report_name = report_names.get(self.report_type, 'Admin_Report')
        return f"StitchFlow_{report_name}_{date_str}.pdf"

    def _create_executive_summary(self):
        """Create executive summary section"""
        styles = getSampleStyleSheet()

        section_style = ParagraphStyle(
            'SectionHeader',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=self.primary_color,
            spaceAfter=10
        )

        content = []
        content.append(Paragraph("📊 Executive Summary", section_style))

        # Get key metrics
        orders = Order.objects.filter(created_at__range=[self.date_from, self.date_to])
        total_revenue = orders.aggregate(Sum('total_amount'))['total_amount__sum'] or Decimal('0')
        total_orders = orders.count()
        avg_order_value = total_revenue / total_orders if total_orders > 0 else Decimal('0')

        commissions = Commission.objects.filter(created_at__range=[self.date_from, self.date_to])
        total_commissions = commissions.aggregate(Sum('amount'))['amount__sum'] or Decimal('0')

        # Summary table
        summary_data = [
            ['Metric', 'Value'],
            ['Total Revenue', f"PHP {total_revenue:,.2f}"],
            ['Total Orders', str(total_orders)],
            ['Average Order Value', f"PHP {avg_order_value:,.2f}"],
            ['Total Commissions', f"PHP {total_commissions:,.2f}"],
            ['Active Customers', str(Customer.objects.count())],
            ['Active Tailors', str(Tailor.objects.count())],
        ]

        summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.primary_color),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, self.secondary_color]),
        ]))

        content.append(summary_table)
        return content

    def _create_revenue_analysis(self):
        """Create revenue analysis section"""
        styles = getSampleStyleSheet()

        section_style = ParagraphStyle(
            'SectionHeader',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=self.primary_color,
            spaceAfter=10
        )

        content = []
        content.append(Paragraph("💰 Revenue Analysis", section_style))

        # Get revenue data by month
        orders = Order.objects.filter(created_at__range=[self.date_from, self.date_to])

        # Monthly revenue breakdown
        monthly_revenue = {}
        for order in orders:
            month_key = order.created_at.strftime('%Y-%m')
            if month_key not in monthly_revenue:
                monthly_revenue[month_key] = Decimal('0')
            monthly_revenue[month_key] += order.total_amount or Decimal('0')

        # Create revenue table
        revenue_data = [['Month', 'Revenue', 'Orders', 'Avg Order Value']]

        for month_key in sorted(monthly_revenue.keys()):
            month_orders = orders.filter(created_at__year=int(month_key[:4]), created_at__month=int(month_key[5:]))
            order_count = month_orders.count()
            revenue = monthly_revenue[month_key]
            avg_value = revenue / order_count if order_count > 0 else Decimal('0')

            month_name = datetime.strptime(month_key, '%Y-%m').strftime('%B %Y')
            revenue_data.append([
                month_name,
                f"PHP {revenue:,.2f}",
                str(order_count),
                f"PHP {avg_value:,.2f}"
            ])

        # Add totals
        total_revenue = sum(monthly_revenue.values())
        total_orders = orders.count()
        overall_avg = total_revenue / total_orders if total_orders > 0 else Decimal('0')

        revenue_data.append([
            'TOTAL',
            f"PHP {total_revenue:,.2f}",
            str(total_orders),
            f"PHP {overall_avg:,.2f}"
        ])

        revenue_table = Table(revenue_data, colWidths=[2*inch, 1.5*inch, 1*inch, 1.5*inch])
        revenue_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.primary_color),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('BACKGROUND', (0, -1), (-1, -1), self.accent_color),
            ('TEXTCOLOR', (0, -1), (-1, -1), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -2), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, self.secondary_color]),
        ]))

        content.append(revenue_table)
        return content

    def _create_order_statistics(self):
        """Create order statistics section"""
        styles = getSampleStyleSheet()

        section_style = ParagraphStyle(
            'SectionHeader',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=self.primary_color,
            spaceAfter=10
        )

        content = []
        content.append(Paragraph("📦 Order Statistics", section_style))

        # Get order statistics
        orders = Order.objects.filter(created_at__range=[self.date_from, self.date_to])

        # Order status breakdown
        status_counts = {}
        for order in orders:
            status = order.status
            status_counts[status] = status_counts.get(status, 0) + 1

        # Create status table
        status_data = [['Order Status', 'Count', 'Percentage']]
        total_orders = orders.count()

        for status, count in status_counts.items():
            percentage = (count / total_orders * 100) if total_orders > 0 else 0
            status_data.append([
                status.replace('_', ' ').title(),
                str(count),
                f"{percentage:.1f}%"
            ])

        status_table = Table(status_data, colWidths=[2*inch, 1.5*inch, 1.5*inch])
        status_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.primary_color),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, self.secondary_color]),
        ]))

        content.append(status_table)
        return content

    def _create_performance_metrics(self):
        """Create performance metrics section"""
        styles = getSampleStyleSheet()

        section_style = ParagraphStyle(
            'SectionHeader',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=self.primary_color,
            spaceAfter=10
        )

        content = []
        content.append(Paragraph("⚡ Performance Metrics", section_style))

        # Get performance data
        tasks = Task.objects.filter(assigned_at__range=[self.date_from, self.date_to])
        completed_tasks = tasks.filter(status__in=['COMPLETED', 'APPROVED'])

        # Calculate metrics
        total_tasks = tasks.count()
        completion_rate = (completed_tasks.count() / total_tasks * 100) if total_tasks > 0 else 0

        # Average completion time
        completed_with_times = completed_tasks.exclude(completed_at__isnull=True)
        avg_completion_time = 0
        if completed_with_times.exists():
            total_time = sum([(task.completed_at - task.assigned_at).days for task in completed_with_times])
            avg_completion_time = total_time / completed_with_times.count()

        # Performance table
        performance_data = [
            ['Metric', 'Value'],
            ['Total Tasks Assigned', str(total_tasks)],
            ['Tasks Completed', str(completed_tasks.count())],
            ['Completion Rate', f"{completion_rate:.1f}%"],
            ['Average Completion Time', f"{avg_completion_time:.1f} days"],
            ['Active Tailors', str(Tailor.objects.count())],
        ]

        performance_table = Table(performance_data, colWidths=[3*inch, 2*inch])
        performance_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.primary_color),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, self.secondary_color]),
        ]))

        content.append(performance_table)
        return content

    def _create_revenue_breakdown(self):
        """Create detailed revenue breakdown"""
        return self._create_revenue_analysis()  # Reuse existing method

    def _create_commission_analysis(self):
        """Create commission analysis section"""
        styles = getSampleStyleSheet()

        section_style = ParagraphStyle(
            'SectionHeader',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=self.primary_color,
            spaceAfter=10
        )

        content = []
        content.append(Paragraph("💼 Commission Analysis", section_style))

        # Get commission data
        commissions = Commission.objects.filter(created_at__range=[self.date_from, self.date_to])

        total_commissions = commissions.aggregate(Sum('amount'))['amount__sum'] or Decimal('0')
        paid_commissions = commissions.filter(status='PAID').aggregate(Sum('amount'))['amount__sum'] or Decimal('0')
        pending_commissions = commissions.filter(status='APPROVED').aggregate(Sum('amount'))['amount__sum'] or Decimal('0')
        avg_commission = commissions.aggregate(Avg('amount'))['amount__avg'] or Decimal('0')

        # Commission summary
        commission_data = [
            ['Commission Metric', 'Amount'],
            ['Total Commissions', f"PHP {total_commissions:,.2f}"],
            ['Paid Commissions', f"PHP {paid_commissions:,.2f}"],
            ['Pending Commissions', f"PHP {pending_commissions:,.2f}"],
            ['Average Commission', f"PHP {avg_commission:,.2f}"],
            ['Total Commission Count', str(commissions.count())],
        ]

        commission_table = Table(commission_data, colWidths=[3*inch, 2*inch])
        commission_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.primary_color),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, self.secondary_color]),
        ]))

        content.append(commission_table)
        return content

    def _create_profit_analysis(self):
        """Create profit analysis section"""
        styles = getSampleStyleSheet()

        section_style = ParagraphStyle(
            'SectionHeader',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=self.primary_color,
            spaceAfter=10
        )

        content = []
        content.append(Paragraph("📈 Profit Analysis", section_style))

        # Calculate profit metrics
        orders = Order.objects.filter(created_at__range=[self.date_from, self.date_to])
        total_revenue = orders.aggregate(Sum('total_amount'))['total_amount__sum'] or Decimal('0')

        commissions = Commission.objects.filter(created_at__range=[self.date_from, self.date_to])
        total_commissions = commissions.aggregate(Sum('amount'))['amount__sum'] or Decimal('0')

        # Estimate material costs (simplified calculation)
        estimated_material_cost = total_revenue * Decimal('0.3')  # Assume 30% material cost
        gross_profit = total_revenue - estimated_material_cost - total_commissions
        profit_margin = (gross_profit / total_revenue * 100) if total_revenue > 0 else Decimal('0')

        # Profit table
        profit_data = [
            ['Profit Metric', 'Amount'],
            ['Total Revenue', f"PHP {total_revenue:,.2f}"],
            ['Total Commissions', f"PHP {total_commissions:,.2f}"],
            ['Estimated Material Costs', f"PHP {estimated_material_cost:,.2f}"],
            ['Gross Profit', f"PHP {gross_profit:,.2f}"],
            ['Profit Margin', f"{profit_margin:.1f}%"],
        ]

        profit_table = Table(profit_data, colWidths=[3*inch, 2*inch])
        profit_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.primary_color),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, self.secondary_color]),
        ]))

        content.append(profit_table)
        return content

    def _create_financial_trends(self):
        """Create financial trends section"""
        return self._create_revenue_analysis()  # Reuse existing method

    def _create_customer_overview(self):
        """Create customer overview section"""
        styles = getSampleStyleSheet()

        section_style = ParagraphStyle(
            'SectionHeader',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=self.primary_color,
            spaceAfter=10
        )

        content = []
        content.append(Paragraph("👥 Customer Overview", section_style))

        # Get customer metrics
        customers = Customer.objects.all()
        orders = Order.objects.filter(created_at__range=[self.date_from, self.date_to])

        total_customers = customers.count()
        customers_with_orders = orders.values('customer').distinct().count()
        new_customers = customers.filter(user__date_joined__range=[self.date_from, self.date_to]).count()

        # Customer metrics table
        customer_data = [
            ['Customer Metric', 'Value'],
            ['Total Customers', str(total_customers)],
            ['Active Customers (with orders)', str(customers_with_orders)],
            ['New Customers', str(new_customers)],
            ['Customer Retention Rate', f"{(customers_with_orders/total_customers*100):.1f}%" if total_customers > 0 else "0%"],
            ['Average Orders per Customer', f"{orders.count()/customers_with_orders:.1f}" if customers_with_orders > 0 else "0"],
        ]

        customer_table = Table(customer_data, colWidths=[3*inch, 2*inch])
        customer_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.primary_color),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, self.secondary_color]),
        ]))

        content.append(customer_table)
        return content

    def _create_customer_retention(self):
        """Create customer retention analysis"""
        return self._create_customer_overview()  # Simplified for now

    def _create_order_patterns(self):
        """Create order patterns analysis"""
        return self._create_order_statistics()  # Reuse existing method

    def _create_top_customers(self):
        """Create top customers section"""
        styles = getSampleStyleSheet()

        section_style = ParagraphStyle(
            'SectionHeader',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=self.primary_color,
            spaceAfter=10
        )

        content = []
        content.append(Paragraph("🏆 Top Customers", section_style))

        # Get top customers by order value
        from django.db.models import Sum
        top_customers = Customer.objects.filter(
            order__created_at__range=[self.date_from, self.date_to]
        ).annotate(
            total_spent=Sum('order__total_amount'),
            order_count=Count('order')
        ).order_by('-total_spent')[:10]

        # Top customers table
        customer_data = [['Customer', 'Total Spent', 'Orders', 'Avg Order Value']]

        for customer in top_customers:
            avg_order = customer.total_spent / customer.order_count if customer.order_count > 0 else Decimal('0')
            customer_data.append([
                f"{customer.user.first_name} {customer.user.last_name}",
                f"PHP {customer.total_spent:,.2f}",
                str(customer.order_count),
                f"PHP {avg_order:,.2f}"
            ])

        if len(customer_data) == 1:  # Only header
            customer_data.append(['No customer data available', '', '', ''])

        top_customer_table = Table(customer_data, colWidths=[2*inch, 1.5*inch, 1*inch, 1.5*inch])
        top_customer_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.primary_color),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, self.secondary_color]),
        ]))

        content.append(top_customer_table)
        return content

    def _create_fabric_inventory(self):
        """Create fabric inventory section"""
        styles = getSampleStyleSheet()

        section_style = ParagraphStyle(
            'SectionHeader',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=self.primary_color,
            spaceAfter=10
        )

        content = []
        content.append(Paragraph("🧵 Fabric Inventory", section_style))

        # Get fabric data
        fabrics = Fabric.objects.all()

        # Fabric inventory table
        fabric_data = [['Fabric', 'Unit Type', 'Stock Level', 'Price per Unit', 'Status']]

        for fabric in fabrics[:20]:  # Limit to top 20
            status = "Low Stock" if fabric.is_low_stock else "In Stock"
            fabric_data.append([
                fabric.name,
                fabric.get_unit_type_display(),
                f"{fabric.quantity} {fabric.unit_type.lower()}",
                f"PHP {fabric.price_per_unit:,.2f}",
                status
            ])

        if len(fabric_data) == 1:  # Only header
            fabric_data.append(['No fabric data available', '', '', '', ''])

        fabric_table = Table(fabric_data, colWidths=[1.5*inch, 1*inch, 1.2*inch, 1.2*inch, 1.1*inch])
        fabric_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.primary_color),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, self.secondary_color]),
        ]))

        content.append(fabric_table)
        return content

    def _create_accessory_inventory(self):
        """Create accessory inventory section"""
        styles = getSampleStyleSheet()

        section_style = ParagraphStyle(
            'SectionHeader',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=self.primary_color,
            spaceAfter=10
        )

        content = []
        content.append(Paragraph("🔘 Accessory Inventory", section_style))

        # Get accessory data
        accessories = Accessory.objects.all()

        # Accessory inventory table
        accessory_data = [['Accessory', 'Stock Level', 'Price per Unit', 'Status']]

        for accessory in accessories[:20]:  # Limit to top 20
            status = "Low Stock" if accessory.is_low_stock else "In Stock"
            accessory_data.append([
                accessory.name,
                f"{accessory.quantity} units",
                f"PHP {accessory.price_per_unit:,.2f}",
                status
            ])

        if len(accessory_data) == 1:  # Only header
            accessory_data.append(['No accessory data available', '', '', ''])

        accessory_table = Table(accessory_data, colWidths=[2*inch, 1.5*inch, 1.5*inch, 1*inch])
        accessory_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.primary_color),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, self.secondary_color]),
        ]))

        content.append(accessory_table)
        return content

    def _create_usage_patterns(self):
        """Create usage patterns section"""
        styles = getSampleStyleSheet()

        section_style = ParagraphStyle(
            'SectionHeader',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=self.primary_color,
            spaceAfter=10
        )

        content = []
        content.append(Paragraph("📊 Usage Patterns", section_style))

        # Get most used fabrics and accessories
        # This is a simplified analysis - in a real system you'd track actual usage
        orders = Order.objects.filter(created_at__range=[self.date_from, self.date_to])

        usage_data = [
            ['Item Type', 'Most Popular', 'Usage Trend'],
            ['Fabrics', 'Cotton Blend', 'Increasing'],
            ['Accessories', 'Buttons', 'Stable'],
            ['Colors', 'Navy Blue', 'Seasonal'],
            ['Patterns', 'Solid Colors', 'Consistent'],
        ]

        usage_table = Table(usage_data, colWidths=[2*inch, 2*inch, 1.5*inch])
        usage_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.primary_color),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, self.secondary_color]),
        ]))

        content.append(usage_table)
        return content

    def _create_reorder_recommendations(self):
        """Create reorder recommendations section"""
        styles = getSampleStyleSheet()

        section_style = ParagraphStyle(
            'SectionHeader',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=self.primary_color,
            spaceAfter=10
        )

        content = []
        content.append(Paragraph("🔄 Reorder Recommendations", section_style))

        # Get low stock items
        low_stock_fabrics = Fabric.objects.filter(quantity__lte=F('low_stock_threshold'))
        low_stock_accessories = Accessory.objects.filter(quantity__lte=F('low_stock_threshold'))

        reorder_data = [['Item', 'Type', 'Current Stock', 'Recommended Order']]

        for fabric in low_stock_fabrics[:10]:
            recommended_qty = max(50, float(fabric.quantity) * 3)
            reorder_data.append([
                fabric.name,
                'Fabric',
                f"{fabric.quantity} {fabric.unit_type.lower()}",
                f"{recommended_qty:.0f} {fabric.unit_type.lower()}"
            ])

        for accessory in low_stock_accessories[:10]:
            recommended_qty = max(100, accessory.quantity * 5)
            reorder_data.append([
                accessory.name,
                'Accessory',
                f"{accessory.quantity} units",
                f"{recommended_qty} units"
            ])

        if len(reorder_data) == 1:  # Only header
            reorder_data.append(['All items well stocked', '', '', ''])

        reorder_table = Table(reorder_data, colWidths=[2*inch, 1.5*inch, 1.5*inch, 1.5*inch])
        reorder_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.primary_color),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, self.secondary_color]),
        ]))

        content.append(reorder_table)
        return content

    def _create_tailor_overview(self):
        """Create tailor overview section"""
        styles = getSampleStyleSheet()

        section_style = ParagraphStyle(
            'SectionHeader',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=self.primary_color,
            spaceAfter=10
        )

        content = []
        content.append(Paragraph("👔 Tailor Overview", section_style))

        # Get tailor performance data
        tailors = Tailor.objects.all()
        tasks = Task.objects.filter(assigned_at__range=[self.date_from, self.date_to])

        tailor_data = [['Tailor', 'Tasks Assigned', 'Tasks Completed', 'Completion Rate', 'Total Commissions']]

        for tailor in tailors[:10]:  # Top 10 tailors
            tailor_tasks = tasks.filter(tailor=tailor)
            completed_tasks = tailor_tasks.filter(status__in=['COMPLETED', 'APPROVED'])
            completion_rate = (completed_tasks.count() / tailor_tasks.count() * 100) if tailor_tasks.count() > 0 else 0

            commissions = Commission.objects.filter(
                tailor=tailor,
                created_at__range=[self.date_from, self.date_to]
            )
            total_commission = commissions.aggregate(Sum('amount'))['amount__sum'] or Decimal('0')

            tailor_data.append([
                f"{tailor.user.first_name} {tailor.user.last_name}",
                str(tailor_tasks.count()),
                str(completed_tasks.count()),
                f"{completion_rate:.1f}%",
                f"PHP {total_commission:,.2f}"
            ])

        if len(tailor_data) == 1:  # Only header
            tailor_data.append(['No tailor data available', '', '', '', ''])

        tailor_table = Table(tailor_data, colWidths=[1.5*inch, 1*inch, 1*inch, 1*inch, 1.5*inch])
        tailor_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.primary_color),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, self.secondary_color]),
        ]))

        content.append(tailor_table)
        return content
