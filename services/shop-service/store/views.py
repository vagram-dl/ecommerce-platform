from django.shortcuts import render, get_object_or_404, redirect
from .models import Product
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required

@login_required
def orders(request):
    return render(request, "store/orders.html")

@login_required
def profile(request):
    return render(request,"store/profile.html")

def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("login")
    else:
        form = UserCreationForm()
    return render(request, "store/register.html",{"form":form})


def product_list(request):
    query = request.GET.get('q')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    category_name = request.GET.get('category')

    products = Product.objects.all()

    if query:
        products = products.filter(name__icontains=query)

    if min_price:
        products = products.filter(price__gte=min_price)

    if max_price:
        products = products.filter(price__lte=max_price)

    if category_name:
        products = products.filter(category__name=category_name)
    return render(request, 'store/product_list.html', {'products': products})

def product_detail(request,pk):
    product = get_object_or_404(Product,pk=pk)
    return render(request, 'store/product_detail.html', {'product':product})

def add_to_cart(request,product_id):
    product = get_object_or_404(Product,id=product_id)

    cart = request.session.get('cart',{})

    if str(product_id) in cart:
        cart[str(product_id)] += 1
    else:
        cart[str(product_id)] = 1

    request.session['cart'] = cart
    request.session.modified = True

    return redirect('cart_view')

def remove_from_cart(request,product_id):
    cart = request.session.get('cart',{})
    if str(product_id) in cart:
        del cart[str(product_id)]
    request.session['cart'] = cart
    request.session.modified = True

    return redirect('cart_view')


def cart_view(request):
    cart = request.session.get('cart', {})

    products_in_cart = []
    total = 0

    for product_id, quantity in cart.items():
        try:
            product = Product.objects.get(id=product_id)
            subtotal = product.price * quantity
            products_in_cart.append({
                'product': product,
                'quantity': quantity,
                'subtotal': subtotal
            })
            total += subtotal
        except Product.DoesNotExist:
            continue

    context = {
        'products': products_in_cart,
        'total': total,
    }

    return render(request, 'store/cart.html', context)



# Create your views here.
