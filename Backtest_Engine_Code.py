import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import requests
import math
import yfinance as yf

#Import S&P500 Historial Data from Yahoo Finance API-----------------
snp500_full = yf.Ticker("^GSPC")
snp500_full = snp500_full.history(period="20y",interval="1d")
snp500_full.index = snp500_full.index.tz_localize(None).normalize()
snp500 = snp500_full['Close'] #limit to relevant data
snp500=snp500.reset_index(name='Close Price') #Change into data frame to enable numerical indexing

#Calculate 5 and 20 day average-------------------------------------
snp500['50 day average'] = "N/A" #Initialising columns so that the number of rows match the data frame
snp500['200 day average'] = "N/A"

for i in range (49,len(snp500)): #Manual for loop for moving average technique
    average= sum(snp500['Close Price'][i-49:i+1])/50
    snp500.loc[i, '50 day average']=average

snp500['200 day average'] = snp500['Close Price'].rolling(window=200).mean() #Built in rolling function in pandas

#Detect Crossover of averages--------------------------------------
snp500['State'] = "Hold" #Set default to be hold

for i in range(199,len(snp500)):
    #Golden Cross
    if (snp500.loc[i, '50 day average']>snp500.loc[i, '200 day average'] and snp500.loc[i-1, '50 day average']<=snp500.loc[i-1, '200 day average']):
        snp500.loc[i, 'State']="Golden Cross"
    #Death Cross
    elif (snp500.loc[i, '50 day average']<snp500.loc[i, '200 day average'] and snp500.loc[i-1, '50 day average']>=snp500.loc[i-1, '200 day average']):
        snp500.loc[i, 'State']="Death Cross"
        
#Defining strategies---------------------------------------------
def SMA_strategy(initial_value): #Simple moving average crossover strategy
    
    shares=math.floor((initial_value/snp500.loc[0, 'Close Price'])-5) #-5 to enable 5 shares to be bought initially
    liquid_funds=initial_value-shares*snp500.loc[0, 'Close Price'] #buy shares on day 0
    k=0 #Transaction counter
    port_value=pd.Series([np.nan]*len(snp500))
    SMA_returns=pd.Series([np.nan]*len(snp500))
    
    for i in range (0,199):  #for 0-198 calculate return and port value
        port_value[i]=liquid_funds+shares*snp500.loc[i, 'Close Price']
        if i != 0:
            SMA_returns[i]=(port_value[i]-port_value[i-1])/port_value[i-1]
            
    for i in range(199,len(snp500)):
        #Golden Cross
        if (snp500.loc[i, '50 day average']>snp500.loc[i, '200 day average'] and snp500.loc[i-1, '50 day average']<=snp500.loc[i-1, '200 day average'] and liquid_funds>=5*snp500.loc[i, 'Close Price']):
            liquid_funds=liquid_funds-5*snp500.loc[i, 'Close Price'] #buy 5 shares
            shares=shares+5
            port_value[i]=liquid_funds+shares*snp500.loc[i, 'Close Price']
            k+=1
            SMA_returns[i]=(port_value[i]-port_value[i-1])/port_value[i-1]
            #print("Transaction %i (BUY) %s - Close Price $%.2f, Portfolio Value $%.2f, Liquid Funds:%.2f" %(k,snp500.loc[i, 'Date'].strftime('%Y-%m-%d'),snp500.loc[i, 'Close Price'],port_value[i],liquid_funds))
            
        #Death Cross
        elif (snp500.loc[i,'50 day average']<snp500.loc[i, '200 day average'] and snp500.loc[i-1, '50 day average']>=snp500.loc[i-1,'200 day average']):
            liquid_funds=liquid_funds+5*snp500.loc[i, 'Close Price'] #Sell 5 shares
            shares=shares-5
            port_value[i]=liquid_funds+shares*snp500.loc[i, 'Close Price']
            k+=1
            SMA_returns[i]=(port_value[i]-port_value[i-1])/port_value[i-1]
            #print("Transaction %i (SELL) %s - Close Price $%.2f, Portfolio Value $%.2f" %(k,snp500.loc[i, 'Date'].strftime('%Y-%m-%d'),snp500.loc[i, 'Close Price'],port_value[i]))
        
        #No trade days - neutral
        else:
            port_value[i]=liquid_funds+shares*snp500.loc[i, 'Close Price']
            SMA_returns[i]=(port_value[i]-port_value[i-1])/port_value[i-1]
    
    final_port_value=liquid_funds+shares*snp500.loc[len(snp500)-1, 'Close Price']
    SMA_return=((final_port_value/initial_value)**(1/20)-1)*100
    
    #Use returns to calculate Sharpe Ratio
    average_return=SMA_returns.mean()
    risk_free_rate=0.015/252 #daily return of treasury bills
    std_dev = SMA_returns.std()
    daily_sharpe_ratio=(average_return-risk_free_rate)/std_dev
    sharpe_ratio=daily_sharpe_ratio*252**0.5
    
    #Calculate max. drawdown
    ceiling=port_value.cummax()
    drawdown = (ceiling - port_value)*100/ ceiling
    max_drawdown = drawdown.max()
    
    
    return SMA_return, sharpe_ratio, max_drawdown

def SNF_strategy(initial_value): #set and forget strategy

    shares=math.floor(initial_value/snp500.loc[0, 'Close Price']) 
    liquid_funds=initial_value-shares*snp500.loc[0, 'Close Price'] #buy shares on day 0
    SNF_returns=pd.Series([np.nan]*len(snp500))
    
    for i in range(1,len(snp500)):
        SNF_returns[i]=(snp500.loc[i, 'Close Price']-snp500.loc[i-1, 'Close Price'])/snp500.loc[i-1, 'Close Price']
            
    final_port_value=liquid_funds+shares*snp500.loc[len(snp500)-1, 'Close Price']
    SNF_return=((final_port_value/initial_value)**(1/20)-1)*100
    
    #average_return=(snp500.loc[len(snp500)-1,'Close Price']/snp500.loc[0,'Close Price'])**(1/len(snp500))
    average_return=SNF_returns.mean()
    risk_free_rate=0.015/252 #daily return of treasury bills (assume 1.5% annually)
    std_dev = SNF_returns.std()
    sharpe_ratio_daily=(average_return-risk_free_rate)/std_dev #daily sharpe ratio
    sharpe_ratio=sharpe_ratio_daily*252**0.5 #annualise sharpe ratio 
    
    #Calculation of max. drawdown----------------------------------------------------
    drawdown=pd.Series([np.nan]*len(snp500)) #initialise 
    ceiling=snp500.loc[0, 'Close Price'] #initial ceiling

    for i in range (0,len(snp500)):  
        if snp500.loc[i, 'Close Price']>ceiling:
            ceiling=snp500.loc[i, 'Close Price'] #replace ceiling with new highest value
        
        drawdown[i]=(ceiling-snp500.loc[i, 'Close Price'])*100/ceiling

    max_drawdown=drawdown.max()
    
    return SNF_return, sharpe_ratio, max_drawdown

#Backtesting Strategy using data----------------------------------------------------------
initial_value=100000

SMA_return, SMA_sharpe_ratio, SMA_max_drawdown=SMA_strategy(initial_value)
print("Simple Moving Average Strategy- Final Return: %.1f%%, Sharpe Ratio: %.3f, Max Drawdown: %.2f%%" %(SMA_return, SMA_sharpe_ratio,SMA_max_drawdown))

SNF_return, SNF_sharpe_ratio,SNF_max_drawdown =SNF_strategy(initial_value)
print("Set and Forget (Buy and Hold) Strategy- Final Return: %.1f%%, Sharpe Ratio: %.3f, Max Drawdown: %.2f%%" %(SNF_return, SNF_sharpe_ratio,SNF_max_drawdown))



#Data Visualisation through graph plotting-------------------------------------
#Change date to datetime format to allow x axis to be date
snp500.set_index('Date', inplace=True) #inplace=True simply replaces the data frame instead of making a copy (more efficient)

plt.plot(snp500['Close Price'],label='Close Price')
plt.plot(snp500['50 day average'][49:],label='50 day average')
plt.plot(snp500['200 day average'][199:],label='200 day average')
plt.ylabel('Stock Price $USD')
plt.xlabel('Date')
plt.title('S&P500 Historial Close Price Data')
plt.legend()
plt.grid()
plt.show()



#Building the strategy
#print(snp500)
