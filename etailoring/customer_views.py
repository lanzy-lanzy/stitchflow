from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.db.models import Count
from .models import Customer, Order

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def get_customer_orders(request, customer_id=None):
    """
    API endpoint to get orders for a specific customer or all customers.
    If customer_id is provided, returns orders for that customer.
    If no customer_id is provided, returns order counts for all customers.
    """
    try:
        if customer_id:
            # Get orders for a specific customer
            customer = Customer.objects.get(id=customer_id)
            orders = Order.objects.filter(customer=customer)
            
            return Response({
                'customer_id': customer_id,
                'order_count': orders.count(),
                'orders': [
                    {
                        'id': order.id,
                        'total_amount': str(order.total_amount),
                        'status': order.status,
                        'payment_status': order.payment_status,
                        'created_at': order.created_at
                    }
                    for order in orders
                ]
            }, status=status.HTTP_200_OK)
        else:
            # Get order counts for all customers
            customers_with_orders = Customer.objects.annotate(
                order_count=Count('order')
            ).values('id', 'order_count')
            
            # Convert to a dictionary for easier lookup
            customer_order_counts = {
                item['id']: item['order_count'] 
                for item in customers_with_orders
            }
            
            return Response({
                'customer_order_counts': customer_order_counts
            }, status=status.HTTP_200_OK)
            
    except Customer.DoesNotExist:
        return Response({'detail': 'Customer not found.'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'detail': f'An error occurred: {str(e)}'}, 
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)