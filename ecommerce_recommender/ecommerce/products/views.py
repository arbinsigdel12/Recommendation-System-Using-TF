from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
import requests
import logging
from .models import Product, Category, Cart, Purchase, Review
from accounts.models import UserActivity

logger = logging.getLogger(__name__)

# Configure FastAPI endpoint
FASTAPI_URL = "http://localhost:8000/api/recommend"

def get_recommendations_from_api(user_id, product_id=None):
    """Helper function to get recommendations from FastAPI"""
    try:
        params = {'user_id': user_id}
        if product_id:
            params['product_id'] = product_id
        
        response = requests.get(
            FASTAPI_URL,
            params=params,
            timeout=3  # 3 second timeout
        )
        response.raise_for_status()  # Raises exception for 4XX/5XX status codes
        return response.json().get('recommendations', [])
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to get recommendations: {str(e)}")
        return []

@login_required
def product_list(request):
    category_id = request.GET.get('category')
    products = Product.objects.all().select_related('category')
    
    if category_id:
        products = products.filter(category_id=category_id)
    
    categories = Category.objects.all()
    paginator = Paginator(products, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    UserActivity.objects.create(
        user=request.user,
        action='view',
        product_name='All Products',
        category='All'
    )
    
    return render(request, 'products/product_list.html', {
        'page_obj': page_obj,
        'categories': categories,
        'selected_category': int(category_id) if category_id else None
    })

@login_required
def product_detail(request, product_id):
    product = get_object_or_404(Product.objects.select_related('category'), id=product_id)
    reviews = Review.objects.filter(product=product).select_related('user')
    
    UserActivity.objects.create(
        user=request.user,
        action='view',
        product_name=product.name,
        category=product.category.name
    )
    
    # Get recommendations
    recommended_ids = get_recommendations_from_api(request.user.id, product_id)
    recommendations = Product.objects.filter(id__in=recommended_ids)
    
    return render(request, 'products/product_detail.html', {
        'product': product,
        'reviews': reviews,
        'recommendations': recommendations
    })

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    cart_item, created = Cart.objects.get_or_create(
        user=request.user,
        product=product,
        defaults={'quantity': 1}
    )
    
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    
    UserActivity.objects.create(
        user=request.user,
        action='cart',
        product_name=product.name,
        category=product.category.name
    )
    
    messages.success(request, f'{product.name} added to cart')
    return redirect('product_detail', product_id=product_id)

@login_required
def remove_from_cart(request, product_id):
    cart_item = get_object_or_404(Cart, user=request.user, product_id=product_id)
    product_name = cart_item.product.name
    cart_item.delete()
    messages.success(request, f'{product_name} removed from cart')
    return redirect('cart')

@login_required
def cart_view(request):
    cart_items = Cart.objects.filter(user=request.user).select_related('product')
    total_price = sum(item.product.price * item.quantity for item in cart_items)
    
    # Get recommendations
    recommended_ids = get_recommendations_from_api(request.user.id)
    recommendations = Product.objects.filter(id__in=recommended_ids)
    
    return render(request, 'products/cart.html', {
        'cart_items': cart_items,
        'total_price': total_price,
        'recommendations': recommendations
    })

@login_required
def checkout(request):
    cart_items = Cart.objects.filter(user=request.user).select_related('product')
    
    if not cart_items.exists():
        messages.warning(request, 'Your cart is empty')
        return redirect('cart')
    
    # Create purchases
    purchases = []
    for item in cart_items:
        purchases.append(
            Purchase(
                user=request.user,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price * item.quantity
            )
        )
        UserActivity.objects.create(
            user=request.user,
            action='buy',
            product_name=item.product.name,
            category=item.product.category.name
        )
    
    # Bulk create purchases for better performance
    Purchase.objects.bulk_create(purchases)
    cart_items.delete()
    
    messages.success(request, 'Purchase successful!')
    return redirect('purchase_history')

def purchase_history(request):
    purchases = Purchase.objects.filter(user=request.user).select_related('product')

    reviewed_product_ids = set(
        Review.objects.filter(user=request.user).values_list('product_id', flat=True)
    )

    for purchase in purchases:
        purchase.already_reviewed = purchase.product.id in reviewed_product_ids

    return render(request, 'products/purchase_history.html', {
        'purchases': purchases,
    })


@login_required
def add_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment', '').strip()
        
        if not rating:
            messages.error(request, 'Please select a rating')
        else:
            Review.objects.update_or_create(
                user=request.user,
                product=product,
                defaults={
                    'rating': rating,
                    'comment': comment
                }
            )
            messages.success(request, 'Review submitted successfully')
            return redirect('purchase_history')
    
    return render(request, 'products/add_review.html', {'product': product})