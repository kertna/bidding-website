from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from .forms import UserRegisterForm,SellForm
from django.contrib.auth.decorators import login_required
from blog.models import Post,Bid,Order,Wishlist
from .forms import UserUpdateForm,ProfileUpdateForm,ContactForm,AddressForm
from django.contrib.auth import login, authenticate
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from .tokens import account_activation_token
from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from django.core.paginator import Paginator
from django.db.models import Q 
from django.conf import settings
from django.template.loader import get_template
from datetime import datetime, timezone
from django.urls import reverse
import stripe
stripe.api_key = "sk_test_51H0rNqD5fba9rsNuuXZqKUJlFtWrvxVLV7PkZZKMM8nwB7AXnEHHid6pCBWZFztSVUp40634OT2R9rkDCJCA0uJY00hSmmEOsF"

def home(request):
	return render(request,'blog/home.html')
def about(request):
	return render(request,'blog/about.html')
def prohome(request):
	return render(request,'blog/home.html')
def stripecheck(request,pk):
	product = Post.objects.get(id=pk)
	context = {'product':product}
	return render(request,'blog/stripecheck.html',context)
def charge(request,pk):
	product = Post.objects.get(id=pk)
	amount=product.final_value
	if request.method == 'POST':
		print('Data:', request.POST)
		customer = stripe.Customer.create(
			email=request.POST['email'],
			name=request.POST['name'],
			source=request.POST['stripeToken']
			)
		charge = stripe.Charge.create(
			customer=customer,
			amount=amount*100,
			currency='inr',
			description="Orion payment"
			)
	product.ispaid()
	Order.objects.create(product=product,username=product.winner)
	return redirect(reverse('success'))

def successMsg(request):
	return render(request, 'blog/success.html')
	
def register(request):
	if request.method== 'POST':
		form=UserRegisterForm(request.POST)
		if form.is_valid():
			user = form.save(commit=False)
			user.is_active = False
			user.save()
			current_site = get_current_site(request)
			mail_subject = 'Activate your orion account.'
			message = render_to_string('acc_active_email.html', {
				'user': user,
				'domain': current_site.domain,
				'uid':urlsafe_base64_encode(force_bytes(user.pk)),
				'token':account_activation_token.make_token(user),})
			to_email = form.cleaned_data.get('email')
			email = EmailMessage(mail_subject, message, to=[to_email])
			email.send()
			return render(request,'blog/emailverification1.html')			
	else:
		form=UserRegisterForm()

	return render(request,'blog/register.html',{'form':form})


# our view
def contact(request):
	form_class = ContactForm

	# new logic!
	if request.method == 'POST':
		form = form_class(data=request.POST)

		if form.is_valid():
			name = request.POST.get(
				'name'
			, '')
			email = request.POST.get(
				'email'
			, '')
			message = request.POST.get('message', '')

			# Email the profile with the
			# contact information
			template = get_template('contact_template.html')
			context = {
				'name': name,
				'email': email,
				'message': message,
			}
			content = template.render(context)

			email = EmailMessage(
				"New contact form submission",
				content,
				"Orion" +'',
				['orionwebsite123@gmail.com'],
				headers = {'Reply-To': email }
			)
			email.send()
			return render(request,'blog/contact1.html')
		else:
			form_class = ContactForm()

	return render(request, 'blog/contact.html', {
		'form': form_class,
	})

def address(request,pk):
	product = Post.objects.get(id=pk)
	form_class = AddressForm

	# new logic!
	if request.method == 'POST':
		form = form_class(data=request.POST)

		if form.is_valid():
			country = request.POST.get(
				'country'
			, '')
			name = request.POST.get(
				'name'
			, '')
			street = request.POST.get('street', '')
			city = request.POST.get('city', '')
			state = request.POST.get('state', '')
			pincode = request.POST.get('pincode', '')
			phone = request.POST.get('phone', '')

			context = {
				'country':country,
				'name': name,
				'street': street,
				'city': city,
				'state':state,
				'pincode':pincode,
				'phone':phone,
				'product':product
			}
			return render(request,'blog/address_template.html',context)
		else:
			form_class = ContactForm()

	return render(request, 'blog/checkout.html', {
		'form': form_class,
	})
def activate(request, uidb64, token):
	try:
		uid = force_text(urlsafe_base64_decode(uidb64))
		user = User.objects.get(pk=uid)
	except(TypeError, ValueError, OverflowError, User.DoesNotExist):
		user = None
	if user is not None and account_activation_token.check_token(user, token):
		user.is_active = True
		user.save()
		login(request, user)
		# return redirect('home')
		return render(request,'blog/emailverification2.html')
	else:
		return HttpResponse('Activation link is invalid!')	

def my_wishlist(request):
	posts = Wishlist.objects.filter(username=request.user)
	for a in posts:
		a.product.resolve()
	paginator = Paginator(posts,6)
	page = request.GET.get('page')
	posts = paginator.get_page(page)
	context={
		'items' : posts
	}
	return render(request,'blog/my_wishlist.html',context)

def add_to_wishlist(request,pid):
	product = Post.objects.get(pk=pid)
	Wishlist.objects.create(product=product,username=request.user)
	posts = Wishlist.objects.filter(username=request.user)
	for a in posts:
		a.product.resolve()
	paginator = Paginator(posts,6)
	page = request.GET.get('page')
	posts = paginator.get_page(page)
	context={
		'items' : posts
	}
	return render(request,'blog/my_wishlist.html',context)

def delete_from_wishlist(request,pid):
	product = Wishlist.objects.get(pk=pid)
	product.delete()
	posts = Wishlist.objects.filter(username=request.user)
	for a in posts:
		a.product.resolve()
	paginator = Paginator(posts,6)
	page = request.GET.get('page')
	posts = paginator.get_page(page)
	context={
		'items' : posts
	}
	return render(request,'blog/my_wishlist.html',context)

@login_required
def getmyitems(request):
	posts = Post.objects.filter(author=request.user).order_by('-date_added')
	for a in posts:
		a.resolve()
	paginator = Paginator(posts,6)
	page = request.GET.get('page')
	posts = paginator.get_page(page)
	context={
		'items' : posts
	}
	return render(request,'blog/myitems.html',context)
@login_required
def getmyorders(request):
	posts = Order.objects.filter(username=request.user)
	for a in posts:
		a.product.resolve()
	paginator = Paginator(posts,6)
	page = request.GET.get('page')
	posts = paginator.get_page(page)
	context={
		'items' : posts
	}
	return render(request,'blog/myorders.html',context)

@login_required
def my_bids(request):
	# Get all bids by user, sorted by date
	my_bids_list = Bid.objects.filter(bidder=request.user).order_by('-date')
	for a in my_bids_list:
		a.auction.resolve()
	paginator = Paginator(my_bids_list,6)
	page = request.GET.get('page')
	my_bids_list = paginator.get_page(page)
	context = {
		'my_bids_list': my_bids_list,
	}
	return render(request,'blog/my_bids.html',context)

@login_required 
def auctions(request):
	posts = Post.objects.all().order_by('-date_added')
	for a in posts:
		a.resolve()
	latest_auction_list = posts.filter(is_exp=True).order_by('-date_added')
	paginator = Paginator(latest_auction_list,6)
	page = request.GET.get('page')
	latest_auction_list = paginator.get_page(page)
	context={
		'items' : latest_auction_list
	}
	return render(request,'blog/auctions.html',context)
@login_required 	
def shop(request):
	auction_list = Post.objects.all()
	for a in auction_list:
		a.resolve()
	latest_auction_list = auction_list.filter(is_active=True).order_by('-date_added')
	paginator = Paginator(latest_auction_list,6)
	page = request.GET.get('page')
	latest_auction_list = paginator.get_page(page)
	context={
		'items' : latest_auction_list
	}
	return render(request,'blog/shop.html',context)	

def pricerange1(request):
	auction_list = Post.objects.filter(is_active=True).filter(minprice__range=(0,10000))
	for a in auction_list:
		a.resolve()
	paginator = Paginator(auction_list,6)
	page = request.GET.get('page')
	auction_list = paginator.get_page(page)
	context={
		'items' : auction_list
	}
	return render(request,'blog/shop.html',context)	

def pricerange2(request):
	auction_list = Post.objects.filter(is_active=True).filter(minprice__range=(10001,100001))
	for a in auction_list:
		a.resolve()
	paginator = Paginator(auction_list,6)
	page = request.GET.get('page')
	auction_list = paginator.get_page(page)
	context={
		'items' : auction_list
	}
	return render(request,'blog/shop.html',context)	

def pricerange3(request):
	auction_list = Post.objects.filter(is_active=True).filter(minprice__range=(100001,1000001))
	for a in auction_list:
		a.resolve()
	paginator = Paginator(auction_list,6)
	page = request.GET.get('page')
	auction_list = paginator.get_page(page)
	context={
		'items' : auction_list
	}
	return render(request,'blog/shop.html',context)	

def pricerange4(request):
	auction_list = Post.objects.filter(is_exp=True).filter(minprice__range=(0,10000))
	for a in auction_list:
		a.resolve()
	paginator = Paginator(auction_list,6)
	page = request.GET.get('page')
	auction_list = paginator.get_page(page)
	context={
		'items' : auction_list
	}
	return render(request,'blog/auctions.html',context)	

def pricerange5(request):
	auction_list = Post.objects.filter(is_exp=True).filter(minprice__range=(10001,100001))
	for a in auction_list:
		a.resolve()
	paginator = Paginator(auction_list,6)
	page = request.GET.get('page')
	auction_list = paginator.get_page(page)
	context={
		'items' : auction_list
	}
	return render(request,'blog/auctions.html',context)	

def pricerange6(request):
	auction_list = Post.objects.filter(is_exp=True).filter(minprice__range=(100001,1000001))
	for a in auction_list:
		a.resolve()
	paginator = Paginator(auction_list,6)
	page = request.GET.get('page')
	auction_list = paginator.get_page(page)
	context={
		'items' : auction_list
	}
	return render(request,'blog/auctions.html',context)	

def pricerange7(request):
	auction_list = Post.objects.filter(is_active=False).filter(is_exp=False).filter(minprice__range=(0,10000))
	for a in auction_list:
		a.resolve()
	paginator = Paginator(auction_list,6)
	page = request.GET.get('page')
	auction_list = paginator.get_page(page)
	context={
		'items' : auction_list
	}
	return render(request,'blog/upcoming_auctions.html',context)	

def pricerange8(request):
	auction_list = Post.objects.filter(is_active=False).filter(is_exp=False).filter(minprice__range=(10001,100001))
	for a in auction_list:
		a.resolve()
	paginator = Paginator(auction_list,6)
	page = request.GET.get('page')
	auction_list = paginator.get_page(page)
	context={
		'items' : auction_list
	}
	return render(request,'blog/upcoming_auctions.html',context)	

def pricerange9(request):
	auction_list = Post.objects.filter(is_active=False).filter(is_exp=False).filter(minprice__range=(100001,1000001))
	for a in auction_list:
		a.resolve()
	paginator = Paginator(auction_list,6)
	page = request.GET.get('page')
	auction_list = paginator.get_page(page)
	context={
		'items' : auction_list
	}
	return render(request,'blog/upcoming_auctions.html',context)	

@login_required
def upauctions(request):
	auction_list = Post.objects.all()
	for a in auction_list:
		a.resolve()
	latest_auction_list = auction_list.filter(is_active=False).filter(is_exp=False).order_by('-date_added')
	paginator = Paginator(latest_auction_list,6)
	page = request.GET.get('page')
	latest_auction_list = paginator.get_page(page)
	context={
		'items' : latest_auction_list
	}
	return render(request,'blog/upcoming_auctions.html',context)

def search_upcoming(request):
	query=request.GET.get('q3')
	if query:
		posts = Post.objects.all().filter(is_active=False).filter(is_exp=False)
		results=posts.filter(Q(title__icontains=query)|Q(category__icontains=query)).order_by('-date_added')
	else:
		results=Post.objects.all().filter(is_active=False).filter(is_exp=False).order_by('-date_added')
	if not results:
		return render(request,'blog/nosearch_upcoming.html')
	for a in results:
		a.resolve()
	paginator = Paginator(results,6)
	page = request.GET.get('page')
	results = paginator.get_page(page)
	context={
		'items' : results
	}
	return render(request,'blog/upcoming_auctions.html',context)
def search_auctions(request):
	query=request.GET.get('q1')
	if query:
		posts = Post.objects.all().filter(is_exp=True)
		results=posts.filter(Q(title__icontains=query)|Q(category__icontains=query)).order_by('-date_added')
	else:
		results=Post.objects.all().filter(is_exp=True).order_by('-date_added')
	if not results:
		return render(request,'blog/nosearch_auctions.html')
	for a in results:
		a.resolve()
	paginator = Paginator(results,6)
	page = request.GET.get('page')
	results = paginator.get_page(page)
	context={
		'items' : results
	}
	return render(request,'blog/auctions.html',context)
def search_shop(request):
	query=request.GET.get('q2')
	if query:
		posts = Post.objects.all().filter(is_active=True)
		results=posts.filter(Q(title__icontains=query)|Q(category__icontains=query)).order_by('-date_added')
	else:
		results=Post.objects.all().filter(is_active=True).order_by('-date_added')
	if not results:
		return render(request,'blog/nosearch_shop.html')
	for a in results:
		a.resolve()
	paginator = Paginator(results,6)
	page = request.GET.get('page')
	results = paginator.get_page(page)
	context={
		'items' : results
	}
	return render(request,'blog/shop.html',context)

@login_required
def shop_item(request,pid):
	products = Post.objects.get(pk=pid)
	products.resolve()
	posts = Bid.objects.filter(bidder=request.user).filter(auction=products).first()
	already_bid = False
	if request.user.is_authenticated:
		if products.author == request.user:
			own_auction = True
			return render(request, 'blog/shop1.html', {'products': products, 'own_auction': own_auction,'bid': posts,})

		user_bid = Bid.objects.filter(bidder=request.user).filter(auction=products).first()
		if user_bid:
			already_bid = True
			bid_amount = user_bid.amount
			return render(request, 'blog/shop1.html', {'products': products, 'already_bid': already_bid, 'bid_amount': bid_amount,'bid': posts,})
	return render(request,'blog/shop1.html',{'products' : products, 'already_bid': already_bid,'bid': posts,})
@login_required
def profile(request):
	if request.method== 'POST':
		u_form=UserUpdateForm(request.POST,instance=request.user)
		p_form=ProfileUpdateForm(request.POST,request.FILES,instance=request.user.profile)
		if u_form.is_valid() and p_form.is_valid():
			u_form.save()
			p_form.save()
			messages.success(request,f'Your account is updated ')
			return redirect('profile')
	else:
		u_form=UserUpdateForm(instance=request.user)
		p_form=ProfileUpdateForm(instance=request.user.profile)
	context={
		'u_form' :u_form,
		'p_form' :p_form
		
	}
	return render(request,'blog/profile.html',context)

@login_required
def get_name(request):
	if request.method == 'POST':	
		form = SellForm(request.POST,request.FILES,author=request.user)	
		if form.is_valid():
			print("in get_name")
			form.save()
			return redirect('blog-home')
	else :
		form=SellForm(author=request.user)
	
	return render(request, 'blog/sell.html', {'form': form})
 
# Bid on some auction
@login_required
def bid(request, auction_id):
	auction = Post.objects.get(pk=auction_id)
	auction.resolve()
	bid = Bid.objects.filter(bidder=request.user).filter(auction=auction).first()

	if not auction.is_active:
		return render(request, 'blog/shop1.html', {
			'auction': auction,
		})

	try:
		bid_amount = request.POST['amount']
		# Prevent user from entering an empty or invalid bid
		if not bid_amount or int(bid_amount) < auction.minprice:
			raise(KeyError)
		if not bid:
			# Create new Bid object if it does not exist
			bid = Bid()
			bid.auction = auction
			bid.bidder = request.user
		bid.amount = bid_amount
		bid.date = datetime.now(timezone.utc)
	except (KeyError):
		# Redisplay the auction details.
		return render(request, 'blog/shop1.html', {
			'auction': auction,
		})
	else:
		bid.save()
		my_bids_list = Bid.objects.filter(bidder=request.user).order_by('-date')
		for a in my_bids_list:
			a.auction.resolve()
		paginator = Paginator(my_bids_list,6)
		page = request.GET.get('page')
		my_bids_list = paginator.get_page(page)
		context = {
			'my_bids_list': my_bids_list,
		}
		return render(request,'blog/my_bids.html',context)