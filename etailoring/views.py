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
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db.models import Sum
from .models import (
    UserExtension, Customer, Tailor, Fabric, 
    Accessory, Order, Task, Commission, Testimonial
)
from .serializers import (
    UserExtensionSerializer, CustomerSerializer, TailorSerializer, 
    FabricSerializer, AccessorySerializer, OrderSerializer, 
    TaskSerializer, CommissionSerializer
)
from .business_logic import OrderManager


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
    serializer = CustomerSerializer(data=request.data)
    if serializer.is_valid():
        customer = serializer.save()
        
        # Create user extension
        UserExtension.objects.create(
            user=customer.user,
            role='CUSTOMER',
            phone_number=customer.phone_number
        )
        
        # No automatic login - customers don't use the login system
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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


class AccessoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Accessory.objects.all()
    serializer_class = AccessorySerializer
    permission_classes = [IsAuthenticated, IsAdminUser]


class OrderListCreateView(generics.ListCreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]


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
    """
    try:
        order = Order.objects.get(id=order_id)
        order.payment_status = 'PAID'
        order.paid_at = timezone.now()
        order.save()
        
        return Response({
            'detail': 'Payment processed successfully.',
            'order_id': order.id,
            'payment_status': order.payment_status
        }, status=status.HTTP_200_OK)
    except Order.DoesNotExist:
        return Response({'detail': 'Order not found.'}, 
                        status=status.HTTP_404_NOT_FOUND)
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
            # If no commission exists, create one
            commission = Commission.objects.create(
                tailor=task.tailor,
                amount=(task.tailor.commission_rate / 100) * task.order.total_amount,
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
        commission = OrderManager.complete_task(task)
        
        return Response({
            'detail': 'Task completed successfully.',
            'task_id': task.id,
            'task_status': task.status,
            'commission_id': commission.id,
            'commission_amount': str(commission.amount)
        }, status=status.HTTP_200_OK)
        
    except Task.DoesNotExist:
        return Response({'detail': 'Task not found.'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
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
        return Commission.objects.filter(tailor__user=self.request.user)


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
