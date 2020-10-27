import PublicApiClient as NtApi
import json,requests
import time, hmac, hashlib, requests,json
from datetime import datetime, date, timedelta
import numpy as np

class telegram:
    text="hello"
    chat_id="твой ид в телеграмм"
    tokenTelegramBot="токен телеграмм бота"
    status=False
    def sentTelegramm(self):
        if self.status:
            telegramUrl="https://api.telegram.org/bot"+self.tokenTelegramBot
            url = telegramUrl + "/sendMessage?chat_id="+self.chat_id+"&text="+str(self.text)
            requests.post(url = url)

class tradernet:
    pub_ = 'public key tradernet'
    sec_ = 'secret key tradernet'
    ticker="RU_VTBR.KZ"
    # Команда выполнения запроса. Инструмент, по которому выставляется приказ
    instr_name = ticker
    # Команда выполнения запроса. Действие: 1 – Покупка (Buy); 2 – Покупка при совершении сделок с маржой (Buy on Margin); 3 – Продажа (Sell); 4 – Продажа при совершении сделок с маржой (Sell Short)
    action_id = 1
    # Команда выполнения запроса. Тип приказа: 1 – Рыночный Приказ (Market); 2 – Приказ по заданной цене (Limit); 3 – Рыночный Стоп-приказ (Stop); 4 – Стоп-приказ по заданной цене (Stop Limit)
    order_type_id = 2
    # количество
    qty = 1000
    # цена по лимиту
    limit_price = 0.190
    # цена стопа
    stop_price = 0
    # Команда выполнения запроса. Экспирация приказа: 1 – Приказ «до конца текущей торговой сессии» (Day); 2 – Приказ «день/ночь или ночь/день» (Day + Ext); 3 – Приказ «до отмены» (GTC, до отмены с участием в ночных сессиях)
    expiration_id = 3
    # Команда выполнения запроса. Пользовательский id приказа. Необязательный параметр
    userOrderId = 0
    order_id_del=0
    command='statusMarket'
    textForTelegram=''
    def OrderPut(self):
        res = NtApi.PublicApiClient(self.pub_, self.sec_, NtApi.PublicApiClient().V2)
        res.sendRequest('getAuthInfo', {})
        cmd_   ='putTradeOrder'
        param_ = {
            "instr_name"    : self.instr_name,
            "action_id"     : self.action_id,
            "order_type_id" : self.order_type_id,
            "qty"           : self.qty,
            "limit_price"   : self.limit_price,
            "stop_price"    : self.stop_price,
            "expiration_id" : self.expiration_id,
            "userOrderId"   : self.userOrderId
        }
        res = res.sendRequest(cmd_, param_).content.decode("utf-8")
        getOrder=json.loads(res)
        return getOrder['order_id']
    def getPositionJsonf (self):
        cmd_ ='getPositionJson'
        res = NtApi.PublicApiClient(self.pub_,self.sec_, NtApi.PublicApiClient().V2)
        res = res.sendRequest(cmd_).content.decode("utf-8")

        getPositionJson=json.loads(res)
        print(getPositionJson)
        for val in getPositionJson['result']['ps']['pos']:
            print(val['i'])
            print(val['s'])
            print(val['q'])
            print(15*"=")
    def OrderDel(self):
        res = NtApi.PublicApiClient(self.pub_, self.sec_, NtApi.PublicApiClient().V2)
        res.sendRequest('getAuthInfo', {})
        cmd_   ='delTradeOrder'
        param_ = {
            "order_id" : self.order_id_del,
        }
        res =res.sendRequest(cmd_, param_).content.decode("utf-8")
        getOrder=json.loads(res)
        return getOrder
    def OrdgetNotifyOrderJson(self):
        res = NtApi.PublicApiClient(self.pub_, self.sec_, NtApi.PublicApiClient().V2)
        res.sendRequest('getAuthInfo', {})
        cmd_ = 'getNotifyOrderJson' 
        res =res.sendRequest(cmd_).content.decode("utf-8")
        getOrder=json.loads(res)
        
        return getOrder
    def infoTicker(self):
        res=requests.get("https://tradernet.ru/securities/export?tickers="+self.ticker+"&params=bap+bbp+marketStatus")
        getStak=json.loads(res.content)
        return getStak[0][self.command]
    def allCancelOrder(self):
        res = self.OrdgetNotifyOrderJson()
        proverka=-1
        for order in res['result']['orders']['order']:
            if order['stat'] !=31 and order['stat']!=2 and order['stat']!=21 and order['stat']!=30:
                self.order_id_del=order['id']
                delres=self.OrderDel()
                if delres['result']==-1:
                    proverka=1
                    self.textForTelegram+=("Order = "+str(self.order_id_del)+" удален \n")
                
                else:
                    self.textForTelegram+=str(delres)+"\n"
            
        if proverka==-1:
            self.textForTelegram+="Открытых ордеров для отмены не найдено \n"

        elif proverka==1:
            self.textForTelegram+="Открытые ордера отменены \n"
    
    def statusMarket(self):
        res=requests.get("https://tradernet.ru/securities/export?tickers="+self.ticker+"&params=bap+bbp+marketStatus")
        getStak=json.loads(res.content)
        return (getStak[0]['marketStatus']=='OPEN')
    def avgStakanPrice(self):
        res=requests.get("https://tradernet.ru/securities/export?tickers="+self.ticker+"&params=bap+bbp+marketStatus")
        getStak=json.loads(res.content)
        buyPrice=getStak[0]['bbp']
        sellPrice=getStak[0]['bap']
        avgPrice=(buyPrice+sellPrice)/2
        routePrice=avgPrice%0.001
        routePrice=round(routePrice,4)
        glavPrice=avgPrice//0.001
        glavPrice=glavPrice/1000
        if routePrice>0.0004:
            glavPrice=glavPrice+0.001
        return glavPrice

class googleSheet:
    url=''
    result={0:0}
    secId=0
    listOrderBuy={0:0}
    listOrderSell={0:0}
    listPriceBuy={0:0}
    listPriceSell={0:0}
    def sendOrders(self):
        data=json.dumps(
            {'id': self.secId, 
            'command': 1,
            'orderBuy':self.listOrderBuy,
            'orderSell':self.listOrderSell,
            'priceBuy':self.listPriceBuy,
            'priceSell':self.listPriceSell})
        headers={'Content-type': 'application/json', 'Accept': 'text/plain'}
        res =requests.post(url = self.url, data=data,headers=headers)
        return res.text
    def checkStatus(self):
        data=json.dumps(
            {'id': self.secId, 
            'command': 0})
        headers={'Content-type': 'application/json', 'Accept': 'text/plain'}
        res =requests.post(url = self.url, data=data,headers=headers)
        return res.text
    def importOrders(self):
        data=json.dumps(
            {'id': self.secId, 
            'command': 2})
        headers={'Content-type': 'application/json', 'Accept': 'text/plain'}
        res =requests.post(url = self.url, data=data,headers=headers)

        return res.json()

class gridStrategy:
    trader=tradernet()
    coundOrder=0
    avgPrice=0.19
    result = {0:0}
    listOrder={0:0}
    listOrders={0:0}
    textForTelegram=''
    lastOrderIndex=-1
    listPrice={0:0}
    listOrderBuy={0:0}
    listOrderSell={0:0}
    listPriceBuy={0:0}
    listPriceSell={0:0}
    stepPrice=0.0005
    minPriceBuy=1
    minPriceSell=1
    maxPriceBuy=0
    maxPriceSell=0
    def openOrders(self):
        for index in range(self.coundOrder):
            # указываем тип ордера на данный момент это покупка
            self.trader.action_id=1
            # лимитная цена на покупку
            self.trader.limit_price=self.avgPrice-((index+1)*self.stepPrice)
            # создание ордера на покупку
            self.listOrderBuy[index]= self.trader.OrderPut()
            # self.listOrderBuy[index]=index+10
            # сохроняем цену покупки в словарь
            self.listPriceBuy[index]=self.trader.limit_price
            #=============================================================
            # указываем тип ордера на данный момент это продажа
            self.trader.action_id=3
            # лимитная цена на продажу
            self.trader.limit_price=self.avgPrice+((index+1)*self.stepPrice)
            # создание ордера на продажу
            self.listOrderSell[index]=self.trader.OrderPut()
            # self.listOrderSell[index]=index+1
            # сохроняем цену продажи в словарь
            self.listPriceSell[index]=self.trader.limit_price
    def checkOrderBuy(self):
        ind=0   
        self.minPriceBuy=1
        self.maxPriceBuy=0
        self.listOrders={0:0}
        self.listPrice={0:0}
        for index in self.listOrderBuy:
            for order_id in self.result['result']['orders']['order']:
                if ((self.listOrderBuy[index])==order_id['id']):
                    self.textForTelegram+=((" id="+str(order_id['id'])+" stat="+str(order_id['stat'])+" b/s="+str(order_id['oper'])+" p=" + str(order_id['p'])+"\n"))
                    if self.minPriceBuy>order_id['p']:
                        self.minPriceBuy=order_id['p']
                    if self.maxPriceBuy<order_id['p']:
                        self.maxPriceBuy=order_id['p']
                    if order_id['stat']==21:
                        self.trader.limit_price=order_id['p']+self.stepPrice
                        self.trader.action_id=3
                        self.listOrderSell[len(self.listOrderSell)]=self.trader.OrderPut()
                        self.listPriceSell[len(self.listPriceSell)]=self.trader.limit_price
                        self.textForTelegram+="создан ордер S id="+str(self.listOrderSell[len(self.listOrderSell)-1 ])+" p="+str(self.trader.limit_price)+"\n"
                    else:
                        self.listOrders[ind]=self.listOrderBuy[index]
                        self.listPrice[ind]=order_id['p']
                        ind+=1
                    break
        self.listOrderBuy=self.listOrders
        self.listPriceBuy=self.listPrice                    
    def checkCountOrderBuy(self):
        if len(self.listOrderBuy)<self.coundOrder:
            count = self.coundOrder-len(self.listOrderBuy)
            for index in range(count):
                self.trader.limit_price=self.minPriceBuy-self.stepPrice
                self.minPriceBuy=self.trader.limit_price
                self.trader.action_id=1
                self.listOrderBuy[len(self.listOrderBuy)]=self.trader.OrderPut()
                self.listPriceBuy[len(self.listPriceBuy)]=self.minPriceBuy
    def checkBeetwenOrderBuy(self):
        countChek=(self.maxPriceBuy-self.minPriceBuy)/self.stepPrice
        priceCheck=self.minPriceBuy
        checkstatus=0
        for index in range(int(countChek)-1):
            priceCheck+=self.stepPrice
            priceCheck=round(priceCheck,4)
            count = len(self.listPriceBuy)
            checkstatus=0
            for index in range(count):                
                if self.listPriceBuy[index]==priceCheck:
                    checkstatus=1
            if checkstatus==0:
                self.trader.limit_price=priceCheck
                self.trader.action_id=1
                self.listOrderBuy[len(self.listOrderBuy)]=self.trader.OrderPut()
                self.listPriceBuy[len(self.listPriceBuy)]=priceCheck


    def checkOrderSell(self):
        ind=0
        self.maxPriceSell=0
        self.minPriceSell=1
        self.listOrders={0:0}
        self.listPrice={0:0}
        for index in self.listOrderSell:
            for order_id in self.result['result']['orders']['order']:
                if ((self.listOrderSell[index])==order_id['id']):
                    self.textForTelegram+=((" id="+str(order_id['id'])+" stat="+str(order_id['stat'])+" b/s="+str(order_id['oper'])+" p=" + str(order_id['p'])+"\n"))
                    if self.maxPriceSell<order_id['p']:
                        self.maxPriceSell=order_id['p']
                    if self.minPriceSell>order_id['p']:
                        self.minPriceSell=order_id['p']
                    if order_id['stat']==21:
                        self.trader.limit_price=order_id['p']+self.stepPrice
                        self.trader.action_id=1
                        self.listOrderBuy[len(self.listOrderBuy)]=self.trader.OrderPut()
                        self.listPriceBuy[len(self.listPriceBuy)]=self.trader.limit_price
                        self.textForTelegram+="создан ордер S id="+str(self.listOrderBuy[len(self.listOrderBuy)-1])+" p="+str(self.trader.limit_price)+"\n"
                    else:
                        self.listOrders[ind]=self.listOrderSell[index]
                        self.listPrice[ind]=order_id['p']
                        ind+=1
                    break
        self.listOrderSell=self.listOrders
        self.listPriceSell=self.listPrice
    def checkCountOrderSell(self):
        if len(self.listOrderSell)<self.coundOrder:
            count = self.coundOrder-len(self.listOrderSell)
            for index in range(count):
                self.trader.limit_price=self.maxPriceSell+self.stepPrice
                self.maxPriceSell=self.trader.limit_price
                self.trader.action_id=3
                self.listOrderSell[len(self.listOrderSell)]=self.trader.OrderPut()
                self.listPriceSell[len(self.listPriceSell)]=self.maxPriceSell
    def checkBeetwenOrderSell(self):
        countChek=(self.maxPriceSell-self.minPriceSell)/self.stepPrice
        priceCheck=self.minPriceSell
        checkstatus=0
        for index in range(int(countChek)-1):
            priceCheck+=self.stepPrice
            priceCheck=round(priceCheck,4)
            count = len(self.listPriceSell)
            checkstatus=0
            for index in range(count):               
                if self.listPriceSell[index]==priceCheck:
                    checkstatus=1
            if checkstatus==0:
                self.trader.limit_price=priceCheck
                self.trader.action_id=3
                self.listOrderSell[len(self.listOrderSell)]=self.trader.OrderPut()
                self.listPriceSell[len(self.listPriceSell)]=priceCheck
    
    def importOrdersSave(self):
            self.listOrderBuy=self.listOrder['ordersBuy']
            self.listOrderSell=self.listOrder['orderSell']
            self.listPriceBuy=self.listOrder['priceBuy']
            self.listPriceSell=self.listOrder['priceSell']
            self.listOrder={0:0}
    
# подключение класса телеграмм
teleg=telegram()
# подключение класса стратегии сетка
grid=gridStrategy()
# подключение класса tradernet 
trader=tradernet()

# подключение класса гугл таблицы
google=googleSheet()
# ид пользователя в телеграмм кому нужно отправлять сообщения
teleg.chat_id=" ид пользователя"
# токен бота телеграмм куда будут отправляться сообщения
teleg.tokenTelegramBot="токен телеграмм бота"
# включить оповещение в телеграмм
teleg.status=True 
# публичный ключ tradernet
trader.pub_ = 'публичный ключ tradernet'
# секретный ключ tradernet
trader.sec_ = 'секретный ключ tradernet'
# подключение возможности отправки сообщения в телеграмм в классе tradernet
trader.teleg=teleg
# ссылка на веб приложения которое мы развернули при помощи редактора скриптов в google sheets
google.url="ссылка на веб приложения"
# это ид для зашиты наших команд для разпоснования свой чужой 
google.secId=1234
# указываем сколько ордеров будет открыта по каждому направлению
grid.coundOrder=20
#  указываем шаг ордеров
grid.stepPrice=0.0005
# количество в ордере
trader.qty=1000
# указываем тикер который будем покупать\продавать
trader.ticker="RU_VTBR.KZ"
# пауза
sec=60
grid.trader=trader
# grid.checkOrder()
# listOrders=google.importOrders()
while True:
    try:
        # проверка статуса tickera
        if trader.statusMarket():
        # if True:

        

            if google.checkStatus()=="0":
                # узнаем средную цену в стакане
                trader.allCancelOrder()
                teleg.text=trader.textForTelegram
                teleg.sentTelegramm()
                grid.avgPrice=trader.avgStakanPrice()
                grid.openOrders()
                google.listOrderBuy=grid.listOrderBuy
                google.listOrderSell=grid.listOrderSell
                google.listPriceBuy=grid.listPriceBuy
                google.listPriceSell=grid.listPriceSell
                google.sendOrders()
            elif google.checkStatus()=="1":
                grid.listOrder=google.importOrders()          
                grid.importOrdersSave()
                grid.result=trader.OrdgetNotifyOrderJson()
                grid.textForTelegram=""
                # проверка buy ордеров 
                grid.checkCountOrderBuy()
                grid.checkOrderBuy()
                grid.checkBeetwenOrderBuy()
                # проверка sell ордеров
                grid.checkOrderSell()
                grid.checkBeetwenOrderSell()
                grid.checkCountOrderSell()
                # текст для телеграмм и отправка
                teleg.text=grid.textForTelegram
                teleg.sentTelegramm()
                # подготовка данных для отправки в гугл таблицу
                google.listOrderBuy=grid.listOrderBuy
                google.listOrderSell=grid.listOrderSell
                google.listPriceBuy=grid.listPriceBuy
                google.listPriceSell=grid.listPriceSell
                # отправка данных в гугл таблицу
                google.sendOrders()

                time.sleep(sec)
                
        else:
        
            teleg.text="Биржа закрыта"
            teleg.sentTelegramm()
            time.sleep(sec*30)
    except:
        teleg.text="ошибка"
        teleg.sentTelegramm()
