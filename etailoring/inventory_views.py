from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from .models import Fabric, Accessory
from .business_logic import InventoryManager


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def restock_fabric(request, fabric_id):
    """
    Restock a fabric item with the given quantity
    """
    try:
        fabric = Fabric.objects.get(id=fabric_id)
        quantity = float(request.data.get('quantity', 0))
        
        if quantity <= 0:
            return Response(
                {'detail': 'Quantity must be greater than 0'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        fabric.quantity += quantity
        fabric.save()
        
        return Response({
            'id': fabric.id,
            'name': fabric.name,
            'quantity': fabric.quantity,
            'message': f'Successfully restocked {fabric.name} with {quantity} {fabric.unit_type}'
        })
    except Fabric.DoesNotExist:
        return Response(
            {'detail': 'Fabric not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'detail': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def restock_accessory(request, accessory_id):
    """
    Restock an accessory item with the given quantity
    """
    try:
        accessory = Accessory.objects.get(id=accessory_id)
        quantity = int(request.data.get('quantity', 0))
        
        if quantity <= 0:
            return Response(
                {'detail': 'Quantity must be greater than 0'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        accessory.quantity += quantity
        accessory.save()
        
        return Response({
            'id': accessory.id,
            'name': accessory.name,
            'quantity': accessory.quantity,
            'message': f'Successfully restocked {accessory.name} with {quantity} units'
        })
    except Accessory.DoesNotExist:
        return Response(
            {'detail': 'Accessory not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'detail': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def get_low_stock_items(request):
    """
    Get a list of items with low stock
    """
    try:
        low_stock_fabrics = Fabric.objects.filter(
            quantity__lte=Fabric.objects.values_list('low_stock_threshold', flat=True)
        )
        
        low_stock_accessories = Accessory.objects.filter(
            quantity__lte=Accessory.objects.values_list('low_stock_threshold', flat=True)
        )
        
        fabric_data = [{
            'id': fabric.id,
            'name': fabric.name,
            'type': 'fabric',
            'quantity': fabric.quantity,
            'threshold': fabric.low_stock_threshold,
            'unit_type': fabric.unit_type
        } for fabric in low_stock_fabrics]
        
        accessory_data = [{
            'id': accessory.id,
            'name': accessory.name,
            'type': 'accessory',
            'quantity': accessory.quantity,
            'threshold': accessory.low_stock_threshold
        } for accessory in low_stock_accessories]
        
        return Response({
            'low_stock_items': fabric_data + accessory_data,
            'count': len(fabric_data) + len(accessory_data)
        })
    except Exception as e:
        return Response(
            {'detail': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def get_inventory_summary(request):
    """
    Get a summary of the inventory
    """
    try:
        fabrics_count = Fabric.objects.count()
        accessories_count = Accessory.objects.count()
        
        low_stock_fabrics_count = Fabric.objects.filter(
            quantity__lte=Fabric.objects.values_list('low_stock_threshold', flat=True)
        ).count()
        
        low_stock_accessories_count = Accessory.objects.filter(
            quantity__lte=Accessory.objects.values_list('low_stock_threshold', flat=True)
        ).count()
        
        return Response({
            'fabrics_count': fabrics_count,
            'accessories_count': accessories_count,
            'low_stock_count': low_stock_fabrics_count + low_stock_accessories_count,
            'total_items': fabrics_count + accessories_count
        })
    except Exception as e:
        return Response(
            {'detail': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def bulk_restock(request):
    """
    Restock multiple items at once
    """
    try:
        items = request.data.get('items', [])
        results = []
        
        for item in items:
            item_type = item.get('type')
            item_id = item.get('id')
            quantity = float(item.get('quantity', 0))
            
            if quantity <= 0:
                results.append({
                    'id': item_id,
                    'type': item_type,
                    'success': False,
                    'message': 'Quantity must be greater than 0'
                })
                continue
            
            if item_type == 'fabric':
                try:
                    fabric = Fabric.objects.get(id=item_id)
                    fabric.quantity += quantity
                    fabric.save()
                    results.append({
                        'id': fabric.id,
                        'name': fabric.name,
                        'type': 'fabric',
                        'success': True,
                        'quantity': fabric.quantity,
                        'message': f'Successfully restocked {fabric.name} with {quantity} {fabric.unit_type}'
                    })
                except Fabric.DoesNotExist:
                    results.append({
                        'id': item_id,
                        'type': 'fabric',
                        'success': False,
                        'message': 'Fabric not found'
                    })
            
            elif item_type == 'accessory':
                try:
                    accessory = Accessory.objects.get(id=item_id)
                    accessory.quantity += quantity
                    accessory.save()
                    results.append({
                        'id': accessory.id,
                        'name': accessory.name,
                        'type': 'accessory',
                        'success': True,
                        'quantity': accessory.quantity,
                        'message': f'Successfully restocked {accessory.name} with {quantity} units'
                    })
                except Accessory.DoesNotExist:
                    results.append({
                        'id': item_id,
                        'type': 'accessory',
                        'success': False,
                        'message': 'Accessory not found'
                    })
            else:
                results.append({
                    'id': item_id,
                    'type': item_type,
                    'success': False,
                    'message': 'Invalid item type'
                })
        
        return Response({
            'results': results,
            'success_count': len([r for r in results if r.get('success')])
        })
    except Exception as e:
        return Response(
            {'detail': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def deduct_inventory(request, order_id=None):
    """
    Manually deduct inventory or deduct for a specific order
    """
    from .models import Order
    
    try:
        if order_id:
            # Deduct inventory for a specific order
            try:
                order = Order.objects.get(id=order_id)
                result, message = InventoryManager.check_inventory(order)
                
                if not result:
                    return Response(
                        {'detail': message},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                InventoryManager.deduct_inventory(order)
                
                return Response({
                    'message': f'Successfully deducted inventory for order #{order.id}'
                })
            except Order.DoesNotExist:
                return Response(
                    {'detail': 'Order not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
        else:
            # Manual deduction
            items = request.data.get('items', [])
            results = []
            
            for item in items:
                item_type = item.get('type')
                item_id = item.get('id')
                quantity = float(item.get('quantity', 0))
                
                if quantity <= 0:
                    results.append({
                        'id': item_id,
                        'type': item_type,
                        'success': False,
                        'message': 'Quantity must be greater than 0'
                    })
                    continue
                
                if item_type == 'fabric':
                    try:
                        fabric = Fabric.objects.get(id=item_id)
                        if fabric.quantity < quantity:
                            results.append({
                                'id': fabric.id,
                                'name': fabric.name,
                                'type': 'fabric',
                                'success': False,
                                'message': f'Insufficient stock for {fabric.name}'
                            })
                            continue
                        
                        fabric.quantity -= quantity
                        fabric.save()
                        results.append({
                            'id': fabric.id,
                            'name': fabric.name,
                            'type': 'fabric',
                            'success': True,
                            'quantity': fabric.quantity,
                            'message': f'Successfully deducted {quantity} {fabric.unit_type} from {fabric.name}'
                        })
                    except Fabric.DoesNotExist:
                        results.append({
                            'id': item_id,
                            'type': 'fabric',
                            'success': False,
                            'message': 'Fabric not found'
                        })
                
                elif item_type == 'accessory':
                    try:
                        accessory = Accessory.objects.get(id=item_id)
                        if accessory.quantity < quantity:
                            results.append({
                                'id': accessory.id,
                                'name': accessory.name,
                                'type': 'accessory',
                                'success': False,
                                'message': f'Insufficient stock for {accessory.name}'
                            })
                            continue
                        
                        accessory.quantity -= quantity
                        accessory.save()
                        results.append({
                            'id': accessory.id,
                            'name': accessory.name,
                            'type': 'accessory',
                            'success': True,
                            'quantity': accessory.quantity,
                            'message': f'Successfully deducted {quantity} units from {accessory.name}'
                        })
                    except Accessory.DoesNotExist:
                        results.append({
                            'id': item_id,
                            'type': 'accessory',
                            'success': False,
                            'message': 'Accessory not found'
                        })
                else:
                    results.append({
                        'id': item_id,
                        'type': item_type,
                        'success': False,
                        'message': 'Invalid item type'
                    })
            
            return Response({
                'results': results,
                'success_count': len([r for r in results if r.get('success')])
            })
    except Exception as e:
        return Response(
            {'detail': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def deduction_report(request, order_id):
    """
    Return a detailed deduction report for a specific order without mutating inventory.
    """
    from .models import Order
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return Response({'detail': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

    try:
        report = InventoryManager.get_deduction_report(order)
        return Response({'report': report})
    except Exception as e:
        return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)