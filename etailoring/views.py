from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db.models import Sum, Count
from django.http import HttpResponse
from datetime import datetime, timedelta
from .models import (
    UserExtension, Customer, Tailor, Fabric, 
    Accessory, Order, Task, Commission, Testimonial
)
from .serializers import (
    UserExtensionSerializer, CustomerSerializer, TailorSerializer, 
    FabricSerializer, AccessorySerializer, OrderSerializer, 
    TaskSerializer, CommissionSerializer
)
from .business_logic import OrderManager, CommissionManager
from .report_generator import TailorReportGenerator
from .sms_service import SemaphoreSMS
import logging

logger = logging.getLogger(__name__)


# Homepage view
def homepage(request):
    # If user is already authenticated, redirect to appropriate dashboard
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('etailoring:admin_dashboard')
        elif hasattr(request.user, 'userextension'):
            if request.user.userextension.role == 'TAILOR':
                return redirect('etailoring:tailor_dashboard')
            elif request.user.userextension.role == 'CUSTOMER':
                return redirect('etailoring:customer_dashboard')
    
    # Get real statistics for the homepage
    try:
        # Get counts for statistics
        customers_count = Customer.objects.count()
        tailors_count = Tailor.objects.count()
        completed_orders_count = Order.objects.filter(status='COMPLETED').count()
        
        # Calculate total commissions paid
        total_commissions = Commission.objects.filter(status='PAID').aggregate(Sum('amount'))
        commission_amount = total_commissions['amount__sum'] if total_commissions['amount__sum'] else 0
        
        # Convert to K format if larger than 1000
        if commission_amount >= 1000:
            commission_amount = commission_amount / 1000
        
        # Get active testimonials from the database
        testimonials = Testimonial.objects.filter(is_active=True)
        
        context = {
            'customers_count': customers_count,
            'tailors_count': tailors_count,
            'completed_orders_count': completed_orders_count,
            'commission_amount': commission_amount,
            'testimonials': testimonials,
        }
    except Exception as e:
        # Fallback to default values if database query fails
        print(f"Error fetching homepage statistics: {e}")
        context = {
            'customers_count': 0,
            'tailors_count': 0,
            'completed_orders_count': 0,
            'commission_amount': 0,
            'testimonials': [],
        }
    
    # Render the homepage with the context data
    return render(request, 'homepage.html', context)

# Page Views
def login_view(request):
    next_url = request.GET.get('next', '')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        next_url = request.POST.get('next', '')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)

            if next_url:
                return redirect(next_url)

            # Redirect based on role
            if user.is_staff:
                return redirect('etailoring:admin_dashboard')
            elif hasattr(user, 'userextension'):
                if user.userextension.role == 'TAILOR':
                    return redirect('etailoring:tailor_dashboard')
                elif user.userextension.role == 'CUSTOMER':
                    return redirect('etailoring:customer_dashboard')

            return redirect('etailoring:homepage')
        
    return render(request, 'login.html', {'next_url': next_url})


@login_required
def register_page_view(request):
    # Only staff/admin users can access the registration page
    if not request.user.is_staff:
        return redirect('etailoring:homepage')
    return render(request, 'register.html')


@login_required
def create_customer_view(request):
    # Only staff/admin users can create customers
    if not request.user.is_staff:
        return redirect('etailoring:homepage')
    return render(request, 'create_customer.html')


@login_required
def create_order_view(request):
    # Only staff/admin users can create orders
    if not request.user.is_staff:
        return redirect('etailoring:homepage')
    return render(request, 'create_order.html')


@login_required
def inventory_management_view(request):
    # Only staff/admin users can manage inventory
    if not request.user.is_staff:
        return redirect('etailoring:homepage')
    return render(request, 'inventory_management.html')


@login_required
def command_management_view(request):
    # Only staff/admin users can manage commands
    if not request.user.is_staff:
        return redirect('etailoring:homepage')
    return render(request, 'command_management.html')


@login_required
def customer_management_view(request):
    # Only staff/admin users can manage customers
    if not request.user.is_staff:
        return redirect('etailoring:homepage')
    return render(request, 'customer_management.html')


@login_required
def manage_customers_view(request):
    # Only staff/admin users can manage customers
    if not request.user.is_staff:
        return redirect('etailoring:homepage')
    return render(request, 'manage_customers.html')


@login_required
def manage_fabrics_view(request):
    # Only staff/admin users can manage fabrics
    if not request.user.is_staff:
        return redirect('etailoring:homepage')
    return render(request, 'manage_fabrics.html')


@login_required
def manage_accessories_view(request):
    # Only staff/admin users can manage accessories
    if not request.user.is_staff:
        return redirect('etailoring:homepage')
    return render(request, 'manage_accessories.html')


@login_required
def manage_tailors_view(request):
    # Only staff/admin users can manage tailors
    if not request.user.is_staff:
        return redirect('etailoring:homepage')
    return render(request, 'manage_tailors.html')


@login_required
def manage_orders_view(request):
    # Only staff/admin users can manage orders
    if not request.user.is_staff:
        return redirect('etailoring:homepage')
    return render(request, 'manage_orders.html')


@login_required
def manage_tasks_view(request):
    # Only staff/admin users can manage tasks
    if not request.user.is_staff:
        return redirect('etailoring:homepage')
    return render(request, 'manage_tasks.html')


@login_required
def manage_commissions_view(request):
    # Only staff/admin users can manage commissions
    if not request.user.is_staff:
        return redirect('etailoring:homepage')
    return render(request, 'manage_commissions.html')


@login_required
def manage_workflow_view(request):
    """
    Consolidated admin workflow view that provides quick actions for
    orders, tasks, and commissions in a single page to simplify admin work.
    """
    if not request.user.is_staff:
        return redirect('etailoring:homepage')
    # Minimal context — the page will load data via admin APIs
    return render(request, 'manage_workflow.html')


@login_required
def manage_payments(request):
    """
    Admin view to manage customer payments.
    """
    # Only staff/admin users can manage payments
    if not request.user.is_staff:
        return redirect('etailoring:homepage')
    return render(request, 'manage_payments.html')


@login_required
def order_summary_view(request):
    # Only staff/admin users can view order summary
    if not request.user.is_staff:
        return redirect('etailoring:homepage')
    return render(request, 'order_summary.html')


def logout_page_view(request):
    logout(request)
    return redirect('etailoring:homepage')


# Dashboard Views
@login_required
def admin_dashboard(request):
    # Only allow staff users to access admin dashboard
    if not request.user.is_staff:
        return redirect('etailoring:homepage')
        
    try:
        # Get counts for dashboard statistics
        customers_count = Customer.objects.count()
        tailors_count = Tailor.objects.count()
        orders_count = Order.objects.count()
        tasks_count = Task.objects.count()
    except Exception as e:
        # Log the error and provide default values
        print(f"Error fetching dashboard counts: {e}")
        customers_count = 0
        tailors_count = 0
        orders_count = 0
        tasks_count = 0
    
    return render(request, 'admin_dashboard.html', {
        'customers_count': customers_count,
        'tailors_count': tailors_count,
        'orders_count': orders_count,
        'tasks_count': tasks_count,
    })


@login_required
def tailor_dashboard(request):
    try:
        tailor = Tailor.objects.get(user=request.user)
        tasks = Task.objects.filter(tailor=tailor)
        commissions = Commission.objects.filter(tailor=tailor)
        return render(request, 'tailor_dashboard.html', {
            'tailor': tailor,
            'tasks': tasks,
            'commissions': commissions,
        })
    except Tailor.DoesNotExist:
        return redirect('etailoring:homepage')


@login_required
def customer_dashboard(request):
    # According to requirements, customers should not have dashboard access
    # Redirect all users away from this page
    return redirect('etailoring:homepage')


# Authentication Views
class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        
        # Perform Django session login
        login(request, user)
        
        # Determine role
        role = None
        if user.is_staff:
            role = 'ADMIN'
        elif hasattr(user, 'userextension'):
            role = user.userextension.role
            
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'role': role
        })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    try:
        request.user.auth_token.delete()
        return Response({'detail': 'Successfully logged out.'}, 
                        status=status.HTTP_200_OK)
    except:
        return Response({'detail': 'Error logging out.'}, 
                        status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def register_view(request):
    import logging
    logger = logging.getLogger('etailoring')
    
    try:
        logger.info(f"Register request data: {request.data}")
        serializer = CustomerSerializer(data=request.data)
        if serializer.is_valid():
            customer = serializer.save()
            logger.info(f"Customer created: {customer.id}")
            
            # Create user extension
            UserExtension.objects.create(
                user=customer.user,
                role='CUSTOMER',
                phone_number=customer.phone_number
            )
            
            logger.info(f"UserExtension created for customer: {customer.id}")
            # No automatic login - customers don't use the login system
            
            response_data = serializer.data
            logger.info(f"Returning response data: {response_data}")
            return Response(response_data, status=status.HTTP_201_CREATED)
        else:
            logger.error(f"Serializer errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.exception(f"Error in register_view: {str(e)}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Admin Views
class CustomerListCreateView(generics.ListCreateAPIView):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]


class CustomerDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]


class TailorListCreateView(generics.ListCreateAPIView):
    queryset = Tailor.objects.all()
    serializer_class = TailorSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]


class TailorDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Tailor.objects.all()
    serializer_class = TailorSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]


class FabricListCreateView(generics.ListCreateAPIView):
    queryset = Fabric.objects.all()
    serializer_class = FabricSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]


class FabricDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Fabric.objects.all()
    serializer_class = FabricSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]


class AccessoryListCreateView(generics.ListCreateAPIView):
    queryset = Accessory.objects.all()
    serializer_class = AccessorySerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get_queryset(self):
        qs = super().get_queryset()
        garment = self.request.query_params.get('garment') or self.request.query_params.get('garment_type')
        if garment:
            # Return accessories that either explicitly list the garment code
            # or have no applicable_garments (treated as universal)
            from django.db.models import Q
            # Use annotate to check if the M2M has no related objects
            qs = qs.annotate(garment_count=Count('applicable_garments')).filter(
                Q(applicable_garments__code__iexact=garment) | Q(garment_count=0)
            ).distinct()
        return qs


class AccessoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Accessory.objects.all()
    serializer_class = AccessorySerializer
    permission_classes = [IsAuthenticated, IsAdminUser]


class GarmentTypeListView(generics.ListAPIView):
    """Return available garment types for admin UI."""
    queryset = None
    serializer_class = None
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get_queryset(self):
        from .models import GarmentType
        return GarmentType.objects.all()

    def get_serializer_class(self):
        from .serializers import GarmentTypeSerializer
        return GarmentTypeSerializer


class OrderListCreateView(generics.ListCreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def perform_create(self, serializer):
        """Override to add server-side logging and better error visibility."""
        try:
            order = serializer.save()
            # Log important order creation details
            logger.info(f"Order created: id={order.id}, total={order.total_amount}, down_payment={order.down_payment_amount}, created_by={getattr(self.request.user, 'username', None)}")
        except Exception as e:
            # Log exception with traceback
            logger.exception(f"Error creating order by user={getattr(self.request.user, 'username', None)}: {e}")
            # Re-raise so DRF can return a proper error response
            raise


class OrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]


class TaskListCreateView(generics.ListCreateAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]


class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]


class CommissionListView(generics.ListAPIView):
    queryset = Commission.objects.all()
    serializer_class = CommissionSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def process_customer_payment(request, order_id):
    """
    API endpoint to process customer payment for an order.
    Supports different payment types: DOWN_PAYMENT, FULL_PAYMENT, REMAINING_PAYMENT
    """
    try:
        order = Order.objects.get(id=order_id)
        payment_type = request.data.get('payment_type', 'FULL_PAYMENT')

        if payment_type == 'DOWN_PAYMENT':
            # Process down payment only
            order.down_payment_status = 'PAID'
            order.down_payment_paid_at = timezone.now()
            order.payment_status = 'DOWN_PAYMENT_PAID'

        elif payment_type == 'REMAINING_PAYMENT':
            # Process remaining balance (only if down payment was already paid)
            if order.payment_status != 'DOWN_PAYMENT_PAID':
                return Response({
                    'detail': 'Down payment must be processed first.'
                }, status=status.HTTP_400_BAD_REQUEST)

            order.payment_status = 'PAID'
            order.paid_at = timezone.now()
            order.remaining_balance = 0  # Set remaining balance to zero when fully paid

        elif payment_type == 'FULL_PAYMENT':
            # Process full payment at once
            order.payment_status = 'PAID'
            order.paid_at = timezone.now()
            order.down_payment_status = 'PAID'
            order.down_payment_paid_at = timezone.now()
            order.remaining_balance = 0  # Set remaining balance to zero when fully paid

        else:
            return Response({
                'detail': 'Invalid payment type. Use DOWN_PAYMENT, FULL_PAYMENT, or REMAINING_PAYMENT.'
            }, status=status.HTTP_400_BAD_REQUEST)

        order.save()

        return Response({
            'detail': 'Payment processed successfully.',
            'order_id': order.id,
            'payment_status': order.payment_status,
            'payment_type': payment_type
        }, status=status.HTTP_200_OK)

    except Order.DoesNotExist:
        return Response({'detail': 'Order not found.'},
                        status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'detail': f'An error occurred: {str(e)}'},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def payment_summary(request):
    """
    API endpoint to get payment summary statistics.
    """
    try:
        from django.db.models import Count, Sum

        # Get payment statistics
        pending_orders = Order.objects.filter(payment_status='PENDING')
        down_payment_orders = Order.objects.filter(payment_status='DOWN_PAYMENT_PAID')
        paid_orders = Order.objects.filter(payment_status='PAID')

        # For the admin summary we want the 'pending' card to reflect the pending down-payment amounts
        # (i.e., the amounts customers still owe as down payments), so aggregate down_payment_amount
        # for orders whose payment_status is PENDING. Keep full payment totals as before.
        summary = {
            'pending_count': pending_orders.count(),
            'pending_amount': pending_orders.aggregate(total=Sum('down_payment_amount'))['total'] or 0,
            'pending_total_amount': pending_orders.aggregate(total=Sum('total_amount'))['total'] or 0,
            'down_payment_count': down_payment_orders.count(),
            'down_payment_amount': down_payment_orders.aggregate(total=Sum('down_payment_amount'))['total'] or 0,
            'full_payment_count': paid_orders.count(),
            'full_payment_amount': paid_orders.aggregate(total=Sum('total_amount'))['total'] or 0,
            'total_revenue': paid_orders.aggregate(total=Sum('total_amount'))['total'] or 0
        }

        return Response(summary, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'detail': f'An error occurred: {str(e)}'},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def approve_task(request, task_id):
    """
    API endpoint for admin to approve a completed task and create commission.
    Sends SMS notification to customer that their garment is ready for pickup.
    """
    try:
        task = Task.objects.get(id=task_id)

        # Check if task is completed
        if task.status != 'COMPLETED':
            return Response({'detail': 'Task must be completed before it can be approved.'},
                            status=status.HTTP_400_BAD_REQUEST)

        # Use business logic to approve task and create commission
        commission = OrderManager.approve_task(task)

        # Send SMS notification to customer that garment is ready for pickup
        try:
            customer = task.order.customer
            customer_name = customer.user.get_full_name() or customer.user.username
            customer_phone = customer.phone_number
            order_id = task.order.id
            
            sms_success, sms_message = SemaphoreSMS.notify_customer_ready_for_pickup(
                customer_name=customer_name,
                customer_phone=customer_phone,
                order_id=order_id
            )
            
            if sms_success:
                logger.info(f'SMS notification sent to customer {customer_name} for Order #{order_id}')
            else:
                logger.warning(f'Failed to send SMS to customer {customer_name}: {sms_message}')
                
        except Exception as e:
            logger.error(f'Error sending SMS notification for task {task_id}: {str(e)}')
            # Don't fail the task approval if SMS fails, just log the error

        return Response({
            'detail': 'Task approved successfully. Commission created. Customer notified via SMS.',
            'task_id': task.id,
            'task_status': task.status,
            'commission_id': commission.id,
            'commission_amount': str(commission.amount)
        }, status=status.HTTP_200_OK)

    except Task.DoesNotExist:
        return Response({'detail': 'Task not found.'},
                        status=status.HTTP_404_NOT_FOUND)
    except ValueError as e:
        return Response({'detail': str(e)},
                        status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'detail': f'An error occurred: {str(e)}'},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def pay_commission_for_task(request, task_id):
    """
    API endpoint to pay commission for a completed task.
    """
    try:
        task = Task.objects.get(id=task_id)
        
        # Check if task is completed
        if task.status != 'COMPLETED':
            return Response({'detail': 'Task must be completed before commission can be paid.'}, 
                            status=status.HTTP_400_BAD_REQUEST)
        
        # Get or create commission for this task
        try:
            commission = Commission.objects.get(order=task.order)
        except Commission.DoesNotExist:
            # If no commission exists, create one using CommissionManager so we
            # respect fixed tariffs defined on the Tailor model.
            amount = CommissionManager.calculate_commission(task)
            commission = Commission.objects.create(
                tailor=task.tailor,
                amount=amount,
                order=task.order
            )
        
        # Pay the commission
        commission.status = 'PAID'
        commission.paid_at = timezone.now()
        commission.save()
        
        return Response({
            'detail': 'Commission paid successfully.',
            'commission_id': commission.id,
            'commission_status': commission.status
        }, status=status.HTTP_200_OK)
    except Task.DoesNotExist:
        return Response({'detail': 'Task not found.'}, 
                        status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'detail': f'An error occurred: {str(e)}'}, 
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def pay_commission(request, commission_id):
    try:
        commission = Commission.objects.get(id=commission_id)
        commission.status = 'PAID'
        commission.paid_at = timezone.now()
        commission.save()
        return Response({'detail': 'Commission paid successfully.'}, 
                        status=status.HTTP_200_OK)
    except Commission.DoesNotExist:
        return Response({'detail': 'Commission not found.'}, 
                        status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def assign_order_to_tailor(request):
    """
    API endpoint to assign an order to a tailor.
    Expects JSON with 'order_id' and 'tailor_id'.
    """
    try:
        order_id = request.data.get('order_id')
        tailor_id = request.data.get('tailor_id')
        
        if not order_id or not tailor_id:
            return Response(
                {'detail': 'Both order_id and tailor_id are required.'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        order = Order.objects.get(id=order_id)
        tailor = Tailor.objects.get(id=tailor_id)
        
        # Use the business logic to assign the order
        task = OrderManager.assign_order_to_tailor(order, tailor)
        
        return Response({
            'detail': 'Order assigned to tailor successfully.',
            'task_id': task.id,
            'order_status': order.status
        }, status=status.HTTP_200_OK)
        
    except Order.DoesNotExist:
        return Response({'detail': 'Order not found.'}, status=status.HTTP_404_NOT_FOUND)
    except Tailor.DoesNotExist:
        return Response({'detail': 'Tailor not found.'}, status=status.HTTP_404_NOT_FOUND)
    except ValidationError as e:
        return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'detail': f'An error occurred: {str(e)}'}, 
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_task(request, task_id):
    """
    API endpoint to start a task.
    Only the assigned tailor can start the task.
    """
    try:
        task = Task.objects.get(id=task_id)
        
        # Check if the user is the assigned tailor
        if task.tailor.user != request.user:
            return Response({'detail': 'You are not authorized to start this task.'}, 
                            status=status.HTTP_403_FORBIDDEN)
        
        # Check if task is already in progress or completed
        if task.status == 'IN_PROGRESS':
            return Response({'detail': 'Task is already in progress.'}, 
                            status=status.HTTP_400_BAD_REQUEST)
        elif task.status == 'COMPLETED':
            return Response({'detail': 'Task is already completed.'}, 
                            status=status.HTTP_400_BAD_REQUEST)
        
        # Use the business logic to start the task
        started_task = OrderManager.start_task(task)
        
        return Response({
            'detail': 'Task started successfully.',
            'task_id': started_task.id,
            'task_status': started_task.status
        }, status=status.HTTP_200_OK)
        
    except Task.DoesNotExist:
        return Response({'detail': 'Task not found.'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        # Enhanced error logging
        import traceback
        print(f"Error in start_task for task_id {task_id}: {str(e)}")
        print(traceback.format_exc())
        return Response({'detail': f'An error occurred: {str(e)}'}, 
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def complete_task(request, task_id):
    """
    API endpoint to complete a task.
    Only the assigned tailor can complete the task.
    """
    try:
        task = Task.objects.get(id=task_id)
        
        # Check if the user is the assigned tailor
        if task.tailor.user != request.user:
            return Response({'detail': 'You are not authorized to complete this task.'}, 
                            status=status.HTTP_403_FORBIDDEN)
        
        # Check if task is already completed
        if task.status == 'COMPLETED':
            return Response({'detail': 'Task is already completed.'}, 
                            status=status.HTTP_400_BAD_REQUEST)
        # Check if task is not yet in progress
        elif task.status == 'ASSIGNED':
            return Response({'detail': 'Task must be started before it can be completed.'}, 
                            status=status.HTTP_400_BAD_REQUEST)
        
        # Use the business logic to complete the task
        completed_task = OrderManager.complete_task(task)

        return Response({
            'detail': 'Task completed successfully. Waiting for admin approval to generate commission.',
            'task_id': completed_task.id,
            'task_status': completed_task.status,
            'message': 'Commission will be created when admin approves this task.'
        }, status=status.HTTP_200_OK)
        
    except Task.DoesNotExist:
        return Response({'detail': 'Task not found.'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        # Enhanced error logging
        import traceback
        print(f"Error in complete_task for task_id {task_id}: {str(e)}")
        print(traceback.format_exc())
        return Response({'detail': f'An error occurred: {str(e)}'}, 
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def restock_fabric(request, fabric_id):
    """
    API endpoint to restock a fabric item.
    """
    try:
        fabric = Fabric.objects.get(id=fabric_id)
        quantity = request.data.get('quantity', 0)
        
        if quantity <= 0:
            return Response({'detail': 'Quantity must be greater than zero.'}, 
                            status=status.HTTP_400_BAD_REQUEST)
        
        # Update the fabric quantity
        fabric.quantity = float(fabric.quantity) + float(quantity)
        fabric.save()
        
        return Response({
            'detail': f'Successfully restocked {quantity} units of {fabric.name}.',
            'fabric_id': fabric.id,
            'new_quantity': fabric.quantity,
            'unit_type': fabric.unit_type
        }, status=status.HTTP_200_OK)
        
    except Fabric.DoesNotExist:
        return Response({'detail': 'Fabric not found.'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'detail': f'An error occurred: {str(e)}'}, 
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def restock_accessory(request, accessory_id):
    """
    API endpoint to restock an accessory item.
    """
    try:
        accessory = Accessory.objects.get(id=accessory_id)
        quantity = request.data.get('quantity', 0)
        
        if quantity <= 0:
            return Response({'detail': 'Quantity must be greater than zero.'}, 
                            status=status.HTTP_400_BAD_REQUEST)
        
        # Update the accessory quantity
        accessory.quantity = int(accessory.quantity) + int(quantity)
        accessory.save()
        
        return Response({
            'detail': f'Successfully restocked {quantity} units of {accessory.name}.',
            'accessory_id': accessory.id,
            'new_quantity': accessory.quantity,
            'unit': 'units'
        }, status=status.HTTP_200_OK)
        
    except Accessory.DoesNotExist:
        return Response({'detail': 'Accessory not found.'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'detail': f'An error occurred: {str(e)}'}, 
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def mark_order_claimed(request, order_id):
    """
    API endpoint for admin to mark an order as claimed (customer picked up garment).
    Records `claimed_at` and `claimed_by` but does not change payment/commission state.
    """
    try:
        order = Order.objects.get(id=order_id)

        if order.claimed_at:
            return Response({'detail': 'Order already marked claimed.'}, status=status.HTTP_400_BAD_REQUEST)

        order.claimed_at = timezone.now()
        order.claimed_by = request.user

        # Create an audit Claim entry so we keep a history of who claimed and any notes.
        try:
            from .models import Claim
            claimant_name = request.data.get('claimant_name') or (order.customer.user.get_full_name() if order.customer and order.customer.user else '')
            claimant_phone = request.data.get('claimant_phone') or (order.customer.phone_number if hasattr(order, 'customer') else '')
            Claim.objects.create(
                order=order,
                claimant_name=claimant_name,
                claimant_phone=claimant_phone,
                recorded_by=request.user,
                notes=request.data.get('notes', '')
            )
        except Exception:
            # If claim creation fails for any reason, continue — we still want the
            # primary order fields to be recorded. Log in production.
            logger.exception('Failed to create Claim audit record for order %s', getattr(order, 'id', 'unknown'))

        # When admin marks claimed, treat this as completion of the order lifecycle.
        # Only update status if it's not already a terminal state.
        if order.status not in ('COMPLETED', 'APPROVED', 'CANCELLED'):
            order.status = 'COMPLETED'
            order.save(update_fields=['claimed_at', 'claimed_by', 'status', 'updated_at'])
        else:
            order.save(update_fields=['claimed_at', 'claimed_by', 'updated_at'])

        return Response({'detail': 'Order marked as claimed.', 'order_id': order.id}, status=status.HTTP_200_OK)
    except Order.DoesNotExist:
        return Response({'detail': 'Order not found.'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.exception('Error marking order claimed: %s', e)
        return Response({'detail': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Tailor Views
class TailorTaskListView(generics.ListAPIView):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Task.objects.filter(tailor__user=self.request.user)


class TailorTaskDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Task.objects.filter(tailor__user=self.request.user)


class TailorCommissionListView(generics.ListAPIView):
    serializer_class = CommissionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Only show commissions for approved tasks
        return Commission.objects.filter(
            tailor__user=self.request.user,
            order__task__status='APPROVED'
        )


# Customer Views
class CustomerOrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Order.objects.filter(customer__user=self.request.user)


class CustomerOrderDetailView(generics.RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Order.objects.filter(customer__user=self.request.user)


@login_required
def assign_order_view(request, order_id):
    # Only staff/admin users can assign orders
    if not request.user.is_staff:
        return redirect('etailoring:homepage')
    
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return redirect('etailoring:manage_orders')
    
    if request.method == 'POST':
        tailor_id = request.POST.get('tailor')
        try:
            tailor = Tailor.objects.get(id=tailor_id)
            # Assign order to tailor using business logic
            task = OrderManager.assign_order_to_tailor(order, tailor)
            # Redirect to manage tasks page
            return redirect('etailoring:manage_tasks')
        except Tailor.DoesNotExist:
            # Handle error - tailor not found
            pass
        except ValidationError as e:
            # Handle inventory validation error
            error_message = str(e)
    
    # GET request - show assignment form
    tailors = Tailor.objects.all()
    return render(request, 'assign_order.html', {
        'order': order,
        'tailors': tailors
    })


# Report Generation Views
@login_required
def tailor_report_page(request):
    """Show the tailor report generation page"""
    try:
        # Determine which tailor's report page to show
        if request.user.is_staff:
            # Admin sees tailor selection page
            tailors = Tailor.objects.all()
            return render(request, 'select_tailor_report.html', {'tailors': tailors})
        else:
            # Tailor sees their own report generation page
            try:
                tailor = Tailor.objects.get(user=request.user)

                # Get some basic stats for the page
                total_tasks = Task.objects.filter(tailor=tailor).count()
                completed_tasks = Task.objects.filter(tailor=tailor, status__in=['COMPLETED', 'APPROVED']).count()
                in_progress_tasks = Task.objects.filter(tailor=tailor, status='IN_PROGRESS').count()

                # Get commission statistics safely
                try:
                    total_commissions = Commission.objects.filter(tailor=tailor).aggregate(
                        total=Sum('amount')
                    )['total'] or 0

                    paid_commissions = Commission.objects.filter(tailor=tailor, status='PAID').aggregate(
                        total=Sum('amount')
                    )['total'] or 0

                    pending_commissions = total_commissions - paid_commissions
                except Exception:
                    total_commissions = 0
                    paid_commissions = 0
                    pending_commissions = 0

                # Calculate completion rate
                completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0

                context = {
                    'tailor': tailor,
                    'total_tasks': total_tasks,
                    'completed_tasks': completed_tasks,
                    'in_progress_tasks': in_progress_tasks,
                    'total_commissions': total_commissions,
                    'paid_commissions': paid_commissions,
                    'pending_commissions': pending_commissions,
                    'completion_rate': completion_rate,
                    'now': timezone.now(),
                }

                return render(request, 'tailor_report_page.html', context)

            except Tailor.DoesNotExist:
                return HttpResponse("Access denied. You are not registered as a tailor.", status=403)

    except Exception as e:
        return HttpResponse(f"Error loading report page: {str(e)}", status=500)


@login_required
def generate_tailor_report(request, tailor_id=None):
    """Generate tailor performance report PDF"""
    try:
        # Determine which tailor's report to generate
        if request.user.is_staff:
            # Admin can generate report for any tailor
            if tailor_id:
                tailor = get_object_or_404(Tailor, id=tailor_id)
            else:
                return HttpResponse("Tailor ID required for admin users", status=400)
        else:
            # Tailor can only generate their own report
            try:
                tailor = Tailor.objects.get(user=request.user)
            except Tailor.DoesNotExist:
                return HttpResponse("Access denied. You are not registered as a tailor.", status=403)

        # Get date range parameters
        date_from_str = request.GET.get('date_from')
        date_to_str = request.GET.get('date_to')
        period = request.GET.get('period', 'last_month')

        # Parse date range
        if date_from_str and date_to_str:
            date_from = datetime.strptime(date_from_str, '%Y-%m-%d').date()
            date_to = datetime.strptime(date_to_str, '%Y-%m-%d').date()
        else:
            # Use predefined periods
            today = timezone.now().date()
            if period == 'last_week':
                date_from = today - timedelta(days=7)
                date_to = today
            elif period == 'last_month':
                date_from = today - timedelta(days=30)
                date_to = today
            elif period == 'last_quarter':
                date_from = today - timedelta(days=90)
                date_to = today
            elif period == 'ytd':
                date_from = today.replace(month=1, day=1)
                date_to = today
            elif period == 'all_time':
                date_from = tailor.user.date_joined.date()
                date_to = today
            else:
                date_from = today - timedelta(days=30)
                date_to = today

        # Convert to datetime with timezone
        date_from = timezone.make_aware(datetime.combine(date_from, datetime.min.time()))
        date_to = timezone.make_aware(datetime.combine(date_to, datetime.max.time()))

        # Generate report
        report_generator = TailorReportGenerator(
            tailor=tailor,
            date_from=date_from,
            date_to=date_to,
            generated_by=request.user
        )

        pdf_data = report_generator.generate_report()
        filename = report_generator.get_filename()

        # Return PDF response
        response = HttpResponse(pdf_data, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        response['Content-Length'] = len(pdf_data)

        return response

    except Exception as e:
        return HttpResponse(f"Error generating report: {str(e)}", status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def tailor_report_api(request, tailor_id=None):
    """API endpoint for generating tailor reports"""
    try:
        # Determine which tailor's report to generate
        if request.user.is_staff:
            if tailor_id:
                tailor = get_object_or_404(Tailor, id=tailor_id)
            else:
                return Response({'error': 'Tailor ID required for admin users'}, status=400)
        else:
            try:
                tailor = Tailor.objects.get(user=request.user)
            except Tailor.DoesNotExist:
                return Response({'error': 'Access denied. You are not registered as a tailor.'}, status=403)

        # Get parameters
        period = request.GET.get('period', 'last_month')
        date_from_str = request.GET.get('date_from')
        date_to_str = request.GET.get('date_to')

        # Parse date range (same logic as above)
        if date_from_str and date_to_str:
            try:
                date_from = datetime.strptime(date_from_str, '%Y-%m-%d').date()
                date_to = datetime.strptime(date_to_str, '%Y-%m-%d').date()
            except ValueError:
                return Response({'error': 'Invalid date format. Use YYYY-MM-DD'}, status=400)
        else:
            today = timezone.now().date()
            if period == 'last_week':
                date_from = today - timedelta(days=7)
                date_to = today
            elif period == 'last_month':
                date_from = today - timedelta(days=30)
                date_to = today
            elif period == 'last_quarter':
                date_from = today - timedelta(days=90)
                date_to = today
            elif period == 'ytd':
                date_from = today.replace(month=1, day=1)
                date_to = today
            elif period == 'all_time':
                date_from = tailor.user.date_joined.date()
                date_to = today
            else:
                date_from = today - timedelta(days=30)
                date_to = today

        # Convert to datetime with timezone
        date_from = timezone.make_aware(datetime.combine(date_from, datetime.min.time()))
        date_to = timezone.make_aware(datetime.combine(date_to, datetime.max.time()))

        # Generate report
        report_generator = TailorReportGenerator(
            tailor=tailor,
            date_from=date_from,
            date_to=date_to,
            generated_by=request.user
        )

        pdf_data = report_generator.generate_report()
        filename = report_generator.get_filename()

        # Return PDF as base64 for API consumption
        import base64
        pdf_base64 = base64.b64encode(pdf_data).decode('utf-8')

        return Response({
            'success': True,
            'filename': filename,
            'pdf_data': pdf_base64,
            'content_type': 'application/pdf'
        })

    except Exception as e:
        return Response({'error': f'Error generating report: {str(e)}'}, status=500)
