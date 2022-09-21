import requests  
from django.shortcuts import render, redirect
from .models import Stock
from django.http import HttpResponse

# Create your views here.

from django.http import HttpResponse


def index(request):
    response = requests.get('https://www.alphavantage.co/query?function=NEWS_SENTIMENT&topics=technology&apikey=RIDUWMSKIS4518PV').json()
    composites = requests.get('https://api.twelvedata.com/price?symbol=NVDA,TSLA,AAPL,MSFT,CRWD,GOOG,PLTR&apikey=c486aa4073cd405daae26abe7f2aef04').json()
    high_volume = requests.get('https://financialmodelingprep.com/api/v3/stock_market/actives?apikey=a47ede9cfb01fb619982832def1ce5cc').json()
    key_stats = requests.get('https://financialmodelingprep.com/api/v3/profile/AAPL?apikey=a47ede9cfb01fb619982832def1ce5cc').json()

    context = {
        'news': response,
        'composites': composites,
        "hi_volume": high_volume,
        "key_stats": key_stats
    }
    return render(request, 'stocks/base.html', context)

def search(request):
    ticker = request.GET.get("search")
    response = requests.get('https://www.alphavantage.co/query?function=OVERVIEW&symbol=' + ticker.upper() + '&apikey=RIDUWMSKIS4518PV').json()
    news = requests.get('https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers=' + ticker.upper() + '&topics=technology&apikey=RIDUWMSKIS4518PV').json()
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
        "news": news["feed"],
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
    if Stock.objects.filter(ticker=str(stock)): 
        for val in Stock.objects.all():
            stats = requests.get('https://financialmodelingprep.com/api/v3/profile/MSFT?limit=10&apikey=a47ede9cfb01fb619982832def1ce5cc').json()
            response = requests.get('https://financialmodelingprep.com/api/v3/profile/' + str(val) + '?apikey=a47ede9cfb01fb619982832def1ce5cc').json() 
            for el in response: 
                if el["mktCap"]: 
                    el["mktCap"] = conversions(str(el["mktCap"]))
                metrics.append(el)
        return render(request, 'stocks/results.html', {'form': metrics, 'exists': "true", 'msg': "Equity already exists in watchlist. Enter another query"})
    else: 
        Stock.objects.create(ticker=stock)
        for ticker in Stock.objects.all(): 
            response = requests.get('https://financialmodelingprep.com/api/v3/profile/' + str(ticker) + '?apikey=a47ede9cfb01fb619982832def1ce5cc').json() 
            for el in response: 
                if el["mktCap"]: 
                    el["mktCap"] = conversions(str(el["mktCap"]))
                metrics.append(el)

        return render(request, 'stocks/results.html', {'form': metrics, 'exists': "false", 'msg': "Successfully added equity to watchlist"})

def watchlist(request): 
    metrics = []
    for val in Stock.objects.all():
        response = requests.get('https://financialmodelingprep.com/api/v3/profile/' + str(val) + '?apikey=a47ede9cfb01fb619982832def1ce5cc').json() 
        for el in response:
            if el["mktCap"]: 
                el["mktCap"] = conversions(str(el["mktCap"]))
            metrics.append(el)
    return render(request, 'stocks/watchlist.html', {'form': metrics})

def delete(request):
    stock = request.POST.get('delete')
    Stock.objects.get(ticker=stock).delete()
    return redirect("/home/watchlist")

def stock(request):     
    return render(request, 'stocks/search.html', {'form': "Ontolocial study"})
