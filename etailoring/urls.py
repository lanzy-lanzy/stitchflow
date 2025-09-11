from django.urls import path
from . import views
from . import inventory_views
from . import customer_views
from . import admin_report_views

app_name = 'etailoring'

urlpatterns = [
    # Homepage
    path('', views.homepage, name='homepage'),
    
    # Page URLs
    path('login/', views.login_view, name='login'),
    path('register/', views.register_page_view, name='register'),
    path('create-customer/', views.create_customer_view, name='create_customer'),
    path('create-order/', views.create_order_view, name='create_order'),
    path('inventory-management/', views.inventory_management_view, name='inventory_management'),
    path('customer-management/', views.customer_management_view, name='customer_management'),
    path('command-management/', views.command_management_view, name='command_management'),
    path('manage-customers/', views.manage_customers_view, name='manage_customers'),
    path('manage-fabrics/', views.manage_fabrics_view, name='manage_fabrics'),
    path('manage-accessories/', views.manage_accessories_view, name='manage_accessories'),
    path('manage-tailors/', views.manage_tailors_view, name='manage_tailors'),
    path('manage-orders/', views.manage_orders_view, name='manage_orders'),
    path('manage-tasks/', views.manage_tasks_view, name='manage_tasks'),
    path('manage-commissions/', views.manage_commissions_view, name='manage_commissions'),
    path('order-summary/', views.order_summary_view, name='order_summary'),
    path('logout/', views.logout_page_view, name='logout'),
    path('assign-order/<int:order_id>/', views.assign_order_view, name='assign_order'),
    
    # Dashboard URLs
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('tailor-dashboard/', views.tailor_dashboard, name='tailor_dashboard'),
    path('customer-dashboard/', views.customer_dashboard, name='customer_dashboard'),
    
    # Authentication URLs
    path('api/login/', views.CustomAuthToken.as_view(), name='api_login'),
    path('api/logout/', views.logout_view, name='api_logout'),
    path('api/register/', views.register_view, name='api_register'),
    
    # Admin URLs
    path('api/admin/customers/', views.CustomerListCreateView.as_view(), name='admin_customer_list'),
    path('api/admin/customers/<int:pk>/', views.CustomerDetailView.as_view(), name='admin_customer_detail'),
    path('api/admin/customers/orders/', customer_views.get_customer_orders, name='admin_customer_orders'),
    path('api/admin/customers/<int:customer_id>/orders/', customer_views.get_customer_orders, name='admin_customer_orders_detail'),
    
    path('api/admin/tailors/', views.TailorListCreateView.as_view(), name='admin_tailor_list'),
    path('api/admin/tailors/<int:pk>/', views.TailorDetailView.as_view(), name='admin_tailor_detail'),
    
    path('api/admin/fabrics/', views.FabricListCreateView.as_view(), name='admin_fabric_list'),
    path('api/admin/fabrics/<int:pk>/', views.FabricDetailView.as_view(), name='admin_fabric_detail'),
    
    path('api/admin/accessories/', views.AccessoryListCreateView.as_view(), name='admin_accessory_list'),
    path('api/admin/accessories/<int:pk>/', views.AccessoryDetailView.as_view(), name='admin_accessory_detail'),
    
    path('api/admin/orders/', views.OrderListCreateView.as_view(), name='admin_order_list'),
    path('api/admin/orders/<int:pk>/', views.OrderDetailView.as_view(), name='admin_order_detail'),
    
    path('api/admin/tasks/', views.TaskListCreateView.as_view(), name='admin_task_list'),
    path('api/admin/tasks/<int:pk>/', views.TaskDetailView.as_view(), name='admin_task_detail'),
    
    path('api/admin/commissions/', views.CommissionListView.as_view(), name='admin_commission_list'),
    path('api/admin/commissions/<int:commission_id>/pay/', views.pay_commission, name='admin_pay_commission'),
    path('api/admin/orders/<int:order_id>/process-payment/', views.process_customer_payment, name='admin_process_payment'),
    path('api/admin/tasks/<int:task_id>/approve/', views.approve_task, name='admin_approve_task'),
    path('api/admin/tasks/<int:task_id>/pay-commission/', views.pay_commission_for_task, name='admin_pay_commission_for_task'),

    # Payment management
    path('manage-payments/', views.manage_payments, name='manage_payments'),
    path('api/admin/payment-summary/', views.payment_summary, name='admin_payment_summary'),
    path('api/admin/assign-order/', views.assign_order_to_tailor, name='admin_assign_order'),
    path('api/admin/fabrics/<int:fabric_id>/restock/', inventory_views.restock_fabric, name='admin_restock_fabric'),
    path('api/admin/accessories/<int:accessory_id>/restock/', inventory_views.restock_accessory, name='admin_restock_accessory'),
    path('api/admin/inventory/low-stock/', inventory_views.get_low_stock_items, name='admin_low_stock'),
    path('api/admin/inventory/summary/', inventory_views.get_inventory_summary, name='admin_inventory_summary'),
    path('api/admin/inventory/bulk-restock/', inventory_views.bulk_restock, name='admin_bulk_restock'),
    path('api/admin/inventory/deduct/', inventory_views.deduct_inventory, name='admin_deduct_inventory'),
    path('api/admin/inventory/deduct/<int:order_id>/', inventory_views.deduct_inventory, name='admin_deduct_inventory_for_order'),
    
    # Tailor URLs
    path('api/tailor/tasks/', views.TailorTaskListView.as_view(), name='tailor_task_list'),
    path('api/tailor/tasks/<int:pk>/', views.TailorTaskDetailView.as_view(), name='tailor_task_detail'),
    path('api/tailor/tasks/<int:task_id>/start/', views.start_task, name='tailor_start_task'),
    path('api/tailor/tasks/<int:task_id>/complete/', views.complete_task, name='tailor_complete_task'),
    path('api/tailor/commissions/', views.TailorCommissionListView.as_view(), name='tailor_commission_list'),
    
    # Customer URLs
    path('api/customer/orders/', views.CustomerOrderListView.as_view(), name='customer_order_list'),
    path('api/customer/orders/<int:pk>/', views.CustomerOrderDetailView.as_view(), name='customer_order_detail'),

    # Report URLs
    path('reports/', views.tailor_report_page, name='tailor_report_page'),
    path('generate-report/', views.generate_tailor_report, name='generate_tailor_report'),
    path('generate-report/<int:tailor_id>/', views.generate_tailor_report, name='generate_tailor_report_for_tailor'),
    path('api/generate-report/', views.tailor_report_api, name='tailor_report_api'),
    path('api/generate-report/<int:tailor_id>/', views.tailor_report_api, name='tailor_report_api_for_tailor'),

    # Admin Report URLs
    path('admin-reports/', admin_report_views.admin_reports_page, name='admin_reports_page'),
    path('admin-reports/generate/<str:report_type>/', admin_report_views.generate_admin_report, name='generate_admin_report'),

    # Admin Stats API URLs
    path('api/admin/stats/revenue/', admin_report_views.admin_stats_revenue, name='admin_stats_revenue'),
    path('api/admin/stats/orders/', admin_report_views.admin_stats_orders, name='admin_stats_orders'),
    path('api/admin/stats/commissions/', admin_report_views.admin_stats_commissions, name='admin_stats_commissions'),
    path('api/admin/stats/tailors/', admin_report_views.admin_stats_tailors, name='admin_stats_tailors'),

    # Admin Charts API URLs
    path('api/admin/charts/revenue/', admin_report_views.admin_charts_revenue, name='admin_charts_revenue'),
    path('api/admin/charts/orders/', admin_report_views.admin_charts_orders, name='admin_charts_orders'),

    # Admin Activity API URL
    path('api/admin/activity/', admin_report_views.admin_recent_activity, name='admin_recent_activity'),
]