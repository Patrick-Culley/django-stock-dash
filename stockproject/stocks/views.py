import requests, time, json, asyncio, aiohttp
from django.shortcuts import render, redirect
from .models import Stock 
from django.http import HttpResponseRedirect
from django.db import connection
from .forms import RegisterUserForm, LoginUserForm
from django.contrib.auth import logout, login, authenticate
from django.contrib import messages
from asgiref.sync import sync_to_async
from datetime import date
from django.http import JsonResponse
from django.contrib.messages import get_messages

curr_date = str(date.today())
user = None

# WELCOME PAGE
def siteentry(request): 
    return render(request, 'stocks/siteentry.html')

# HOME PAGE UPON SUCCESSFULL LOGIN
def index(request):
    user = request.session['user']
    greetingtime = None
    localtime = time.localtime()

    if localtime[3] < 12: 
        greetingtime = "Good Morning"
    elif localtime[3] > 12 and localtime[3] < 18:
        greetingtime = "Good Afternoon"
    else: 
        greetingtime = "Good Evening"

    # API CALLS 
    response = requests.get('https://www.alphavantage.co/query?function=NEWS_SENTIMENT&topics=technology&apikey=RIDUWMSKIS4518PV').json()
    composites = requests.get('https://api.twelvedata.com/price?symbol=NVDA,TSLA,AAPL,MSFT,CRWD,GOOG,PLTR&apikey=c486aa4073cd405daae26abe7f2aef04').json()
    high_volume = requests.get('https://financialmodelingprep.com/api/v3/stock_market/actives?apikey=a47ede9cfb01fb619982832def1ce5cc').json()
    key_stats = requests.get('https://financialmodelingprep.com/api/v3/profile/AAPL?apikey=a47ede9cfb01fb619982832def1ce5cc').json()

    context = {
        'news': response,
        'composites': composites,
        "hi_volume": high_volume,
        "key_stats": key_stats,
        "user": user,
        "greetingtime": greetingtime
    }
    return render(request, 'stocks/base.html', context)

# REGISTER NEW USERS 
def register(request): 
    if request.method == 'POST': 
        form = RegisterUserForm(request.POST) 
        if form.is_valid():
            form.save()
            fname = form.cleaned_data['first_name']
            lname = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            username = form.cleaned_data['username']

            request.session['user'] = username
            # with connection.cursor() as cursor: 
            #     cursor.execute("INSERT INTO users (first_name, last_name, email, password, username) VALUES (%s,%s,%s,%s,%s)", 
            #                    [fname, lname, email, password, username])

            return HttpResponseRedirect("/home/")
    else: 
        form=RegisterUserForm
        request.session['user'] = "testuser"
        print(request.session['user'])
            
    return render(request, 'stocks/register.html', {'form': form})

# USER LOGIN PAGE
def login(request): 
    request.session['user'] = None 
    if request.method == 'POST': 
        form = LoginUserForm(request.POST)
        if form.is_valid(): 
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            
            # AUTHENTICATE VIA MySQL 
            with connection.cursor() as cursor: 
                cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", [username, password])
                if (len(cursor.fetchall()) == 0): 
                    print("USER NAME DOES NOT EXIST!")
                    messages.info(request, "Invalid Credentials.")
                    
                    return redirect('/login')  
                else: 
                    print("SUCCESSFULLY LOGGED IN")
                    request.session['user'] = username
                    user = request.session['user']
                    return redirect('/home')
    else: 
        form = LoginUserForm
    return render(request, 'stocks/login.html', {'form': form})

# SEARCH BY TICKER SYMBOL 

def search(request):
    ticker = request.GET.get("search")
    newsfeed = requests.get('https://financialmodelingprep.com/api/v3/stock_news?tickers=' + ticker.upper() + '&page=0&apikey=a47ede9cfb01fb619982832def1ce5cc').json()
    time.sleep(.1)

    # Confirm if ticker or company name input
    try:
        response = requests.get('https://www.alphavantage.co/query?function=OVERVIEW&symbol=' + ticker.upper() + '&apikey=RIDUWMSKIS4518PV').json()
        quote = requests.get('https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=' + ticker.upper() + '&apikey=RIDUWMSKIS4518PV').json() 
        
        metrics = {
            "name": response["Name"].upper(),
            "icon": findIcon(ticker.upper()),
            "curr_price": quote["Global Quote"]["05. price"],
            "dollar_change": quote["Global Quote"]["09. change"] + " ",
            "percent_change": "(" + quote["Global Quote"]["10. change percent"] + ") ",
            "signed_int": 0 if quote["Global Quote"]["09. change"][0] == "-" else 1, 
            "date": quote["Global Quote"]["07. latest trading day"], 
            "exchange": "     |     " + response["Exchange"],
            "news": newsfeed,
            "symbol": ticker.upper(), 
            "summary": response["Description"],
            "m_cap": conversions(response["MarketCapitalization"]), 
            "peRatio": response["PERatio"],
            "eps": response["EPS"],
            "52weekhigh": response["52WeekHigh"],
            "52weeklow": response["52WeekLow"],
            "targetprice": response["AnalystTargetPrice"],
            "margin": response["ProfitMargin"],
            "beta": response["Beta"], 
            "div_yield": response["DividendYield"],
            # "DivDate": response["ExDividendDate"]
        }   
        return render(request, 'stocks/search.html', {'form': metrics}) 
    except: 
        messages.info(request, "Invalid Ticker Symbol. Please try again.")
        return redirect('/home')


def findIcon(val): 
        response = requests.get('https://financialmodelingprep.com/api/v3/profile/' + val + '?apikey=a47ede9cfb01fb619982832def1ce5cc').json()
        return response[0]["image"]


def conversions(value): 
    first = list(value)
    if len(value) >= 13: 
        first.insert(1, ".")
        return (''.join(first))[:4] + " trillion"
    elif len(value) < 13 and len(value) > 6: 
        if len(value) == 12:
            first.insert(3, ".")
            return (''.join(first))[:6] + " billion"
        elif len(value) == 11:
            first.insert(2, ".")
            return (''.join(first))[:5] + " billion"
        else: 
            first.insert(1,".")
            return (''.join(first))[:4] + " billion"
    else: 
        if len(value) == 9:
            first.insert(3, ".")
            return (''.join(first))[:6] + " million"
        elif len(value) == 8:
            first.insert(2, ".")
            return (''.join(first))[:5] + " million"
        else: 
            first.insert(1,".")
            return (''.join(first))[:4] + " million"


def addstock(request):
    stock = request.POST.get('ticker')
    metrics = []

    # If stock exists, print error message along with current stocks 
    if Stock.objects.filter(ticker=str(stock), username=request.session['user']): 
        for val in Stock.objects.all():
            stats = requests.get('https://financialmodelingprep.com/api/v3/profile/MSFT?limit=10&apikey=a47ede9cfb01fb619982832def1ce5cc').json()
            response = requests.get('https://financialmodelingprep.com/api/v3/profile/' + str(val) + '?apikey=a47ede9cfb01fb619982832def1ce5cc').json() 
            for el in response: 
                if el["mktCap"]: 
                    el["mktCap"] = conversions(str(el["mktCap"]))
                metrics.append(el)
        return render(request, 'stocks/results.html', 
                      {'form': metrics, 'exists': "true", 'msg': "Equity already exists in watchlist. Enter another query"})
    
    else: 
        with connection.cursor() as cursor:
            cursor.execute("INSERT INTO stocks (ticker, username) VALUES (%s, %s)", [stock, request.session['user']]) 
        for ticker in Stock.objects.all(): 
            response = requests.get('https://financialmodelingprep.com/api/v3/profile/' + str(ticker) + '?apikey=a47ede9cfb01fb619982832def1ce5cc').json() 
            for el in response: 
                if el["mktCap"]: 
                    el["mktCap"] = conversions(str(el["mktCap"]))
                metrics.append(el)
        return redirect('/home')

# WATCHLIST VIEW HELPER FOR QUERYING DATABASE  
@sync_to_async
def get_stocks(request):
    user = request.session['user']
    with connection.cursor() as cursor: 
        cursor.execute("SELECT ticker FROM stocks WHERE username = %s", ['bootman'])
        result = cursor.fetchall()
        return result
    
# WATCHLIST VIEW ASYNC HELPER FOR API CALLS
async def get_stock_data(session, index):
    async with session.get('https://financialmodelingprep.com/api/v3/profile/' + index[0] + '?apikey=a47ede9cfb01fb619982832def1ce5cc') as resp:
        test1 = await resp.json() 
    async with session.get('https://financialmodelingprep.com/api/v3/historical-chart/1min/' + index[0] + '?apikey=a47ede9cfb01fb619982832def1ce5cc') as con:
        test2 = await con.json()
    return test1, test2

# GET USERNAME TO DELETE WATCHLIST ROW
@sync_to_async
def get_user(request):
    user = request.session['user']
    return user 


async def watchlist(request):   
    stocks = await get_stocks(request)
    user = await get_user(request)
    metrics, quotes, price = [], [], None

    # Get intraday prices and general financials
    async with aiohttp.ClientSession() as session:
        tasks = [get_stock_data(session, stock) for stock in stocks]
        results = await asyncio.gather(*tasks)

        for test1, test2 in results:
            date =  test2[0]["date"][8:10]
            test1[0]['mktCap'] = conversions(str(test1[0]['mktCap']))
            test1[0]['volAvg'] = conversions(str(test1[0]['volAvg']))
            metrics.append(test1[0]) 
            price = [x['close'] for x in test2 if x["date"][8:10] == date]
            price.reverse()
            quotes.append(price)
    return render(request, 'stocks/watchlist.html', {'form': metrics, 'quotes': quotes, 'user': user})
 
 
def delete(request):
    user = request.POST.get('delete_user')
    stock = request.POST.get('delete_symbol')
    
    with connection.cursor() as cursor: 
        cursor.execute("DELETE FROM stocks WHERE username = %s AND ticker = %s", [str(user), str(stock)])
        result = cursor.fetchall() 
        print(result)
    return redirect("/watchlist")   


def stock(request):     
    return render(request, 'stocks/search.html', {'form': "Ontolocial study"})
