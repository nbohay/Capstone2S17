#!C:\python27\python.exe
import csv
import urllib
from itertools import islice
from datetime import datetime
import cgi
import cgitb
import plotly
from plotly.graph_objs import Scatter, Layout

#this is the header for the html code
def htmlTop():
    print("""Content-type:text/html\n\n
            <!DOCTYPE html>
            <html>
                <head>
                    <meta charset="utf-8" />
                    <title>Stock Market</title>
                </head>
                
                <body>""")
#tail for the html code that outputs into input.html
def htmlTail():
    print("""</body> </html>""")

#after submission of the form, getting the information put into the form to use 
form=cgi.FieldStorage()
stockname=form.getvalue('fullname')
stocktag=stockname.split("\t")[0]
stockname=stockname.split("\t")[1]
#stocktag=form.getvalue('stockticker') #old way of getting stock ticker
toDate=datetime.strptime(form.getvalue('todate'),'%m/%d/%Y').strftime('%Y-%m-%d')
fromDate=datetime.strptime(form.getvalue('fromdate'),'%m/%d/%Y').strftime('%Y-%m-%d')

#uses the data from the stock tag submission in the form and finds the stock closings and dates
def make_url(stocktag):
    base_url="https://ichart.finance.yahoo.com/table.csv?s="
    return base_url+stocktag

#name of csv file of the information found by make_url and saves name as stocktag
def make_filename(stocktag):
    output_path="C:/xampp/htdocs/Capstone/Stocks_info/"
    return output_path + stocktag + ".csv"

#runs the url and creates the csv file, if it is not found then it will create one, overwrites previous with new information
def pull_stock_info(stocktag):
    try:
        filename=urllib.URLopener()
        filename.retrieve(make_url(stocktag), make_filename(stocktag))
    except urllib.ContentTooShortError as e:   
        outfile = open(make_filename(stocktag), "w")
        outfile.write(e.content)
        outfile.close()

#opens csv file and finds the row tht the dates are in and counts the difference between them
def find_dates_data(toDate,fromDate):
    with open(make_filename(stocktag), "r") as f:
        reader = csv.reader(f)
        maxcol=0
        mincol=0
        L=list()
        for col, row in enumerate(reader):
            if toDate in row[0]:
                maxcol=col
                L.append(maxcol)
            if fromDate in row[0]:
                mincol=col
                L.append(mincol)
            diff=mincol-maxcol+1; ##added one bec i want to include that date    
        if maxcol ==0 or mincol==0:
            print "\nNOT IN FILE"    
    return mincol,maxcol,diff        

#finds the dates and the adjusted closings to find statistics of the last three years of the stock
def get_last_three():  
    years='2014-01-02'
    thisyear='2017-01-03'
    a= find_dates_data(thisyear,years)     
    list2d=[];       ##list of dates
    with open(make_filename(stocktag), "r") as f:
        reader = csv.reader(f)
        for col, row in enumerate(reader): #goes through reader and finds the maxcol and loops the difference amount of times and puts it into the list2d
            for i in range(a[2]):        
                if col==a[1]:
                    list2d.append([row[0],row[6]]);   ##add the dates and the adjust close
                    row=reader.next();      ##go to next line in reader
    listdates=[]
    listprice=[]
    for i, row in enumerate(list2d): 
        listdates.insert(0,datetime.strptime(list2d[i][0],'%Y-%m-%d').strftime('%m-%d-%Y'))
        listprice.insert(0,float(list2d[i][1]))
    return listprice

#calculates the average price of the stock in the certain timeframe
def mean(numbers):
    sum=0
    for elem in numbers:
        sum+=float(elem)
    b=float(sum/(len(numbers)*1.0))
    return b

#calculates the percentage of roc of a stock per day
def growth(numbers):
    a=float(numbers[0])
    b=float(numbers[-1])
    c=((b-a)/a)*100
    return c
    
#goes through the csv file to find the exact row of the date we discovered in find_dates_data and uses it to locate the dates themselves and the adj close and 
#puts them into sorted lists 
#Find the row then count the difference between the max row and min row 
def get_date_closing(stocktag):
    info=find_dates_data(toDate,fromDate);
    list2d=[];       ##list of dates
    with open(make_filename(stocktag), "r") as f:
        reader = csv.reader(f)
        for col, row in enumerate(reader): #goes through reader and finds the maxcol and loops the difference amount of times and puts it into the list2d
            for i in range(info[2]):        
                if col==info[1]:
                    list2d.append([row[0],row[6]]);   ##add the dates and the adjust close
                    row=reader.next();      ##go to next line in reader
    return list2d              
     
#used if needed to print all info on stocks
def print_info(stocktag):
    info=get_date_closing(stocktag);
    list2d=info
    print "Symbol &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;  Adj Close" 
    for i,row in enumerate(list2d):
        print " &nbsp; ".join(row)

#uses the information from the lists created above to plot the graphs with plotly.
def plot_user_data(stocktag):
    info=get_date_closing(stocktag);
    list2d=info
    listdates=[]
    listprice=[]
    for i, row in enumerate(list2d): 
        listdates.insert(0,datetime.strptime(list2d[i][0],'%Y-%m-%d').strftime('%m-%d-%Y'))
        listprice.insert(0,float(list2d[i][1]))
    return listdates, listprice        

#use the mean and growth functions with the get_last_three function to calculate statistics of the last three years
def stats():
    a=plot_user_data(stocktag)[1]
    a=growth(a)
    a="%.3f" % a
    mthree=get_last_three()
    yeargro=mthree
    mthree=mean(mthree)
    mthree="%.3f" % mthree  #get the first two decimal places of the float
    yeargro=growth(yeargro)
    yeargro=yeargro/3
    yeargro= "%.3f" % yeargro
    return mthree,yeargro,a

#uses the previous years data to calculate the predictions based on the past
#used 250 for the approximate amount of days the stock market is open a year.
#calculates three years in advance
def predictions():
    thisyear=get_last_three()
    jan=float(thisyear[-1])
    gro=float(stats()[1])/100
    a= (jan*gro)+jan
    b= (a*gro)+a
    c= (b*gro)+b
    a="%.3f" % a
    b="%.3f" % b
    c="%.3f" % c
    return str(a),str(b), str(c)

#was used to get date in time for a future application
#def to_unix_time(dt):
  #  epoch =  datetime.utcfromtimestamp(0)
 #   return (dt - epoch).total_seconds() * 1000

#used to create the plotting graphs in an html file in the folder where input.html is contained
def offline_plot(stocktag):
    plotinfo=plot_user_data(stocktag)
    date=plotinfo[0]
    y=plotinfo[1]
    plotly.offline.plot({"data":[Scatter(x=date, y=y)],"layout":Layout(title=stocktag, dragmode='pan')},auto_open=False, show_link=False)
    return None

#main program 
#runs the pull stock info and offline plot before running html code
#code compiles into iframe into input.html 
#prints out plot, from temp-plot html
#prints statistics run for the last three years and the next year,
#outputs a news page based on the form submission of the name of the stock
if __name__=="__main__":
    try:
        pull_stock_info(stocktag)
        offline_plot(stocktag)
        htmlTop()
        print("<style>iframe{border:none;}</style>")
        print("<div style=\"float:left; width:50%\"><iframe scrollable=\"no\" src=\"temp-plot.html\" style=\"height:500px; width:100%;\"></iframe></div>")
        print("<div style=\"float:left; width:50%\"><h1 align=\"center\">Stats for "+stockname+"</h1>")
        print("<h3>Your selection:</h3><p>Average ROC: "+stats()[2]+"%</p><h3>Past three years: </h3><p>Average ROC Per Year: "+stats()[1]+"%</p><p>Mean: "+stats()[0]+"</p></div>")
        print ("<h3>Projected:</h3><p>2018: "+predictions()[0]+"</p><p>2019: "+predictions()[1]+"</p><p>2020: "+predictions()[2]+"</p>")
        print("<iframe scrolling=\"YES\" style=\"width:99%; height:1350px \" src=\"https://www.bing.com/news/search?q="+urllib.quote(stockname)+"&FORM=HDRSC6\"></iframe>")
        htmlTail()
    except:
        cgi.print_exception()
