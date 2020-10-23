######################################################№########
#           PublicApi-клиент TraderNet для Python 3           #
#######################################################№#######
import time, hmac, hashlib, requests, json

class PublicApiClient:
    # Имена приватных переменных класса должны начинаться на два подчеркивания: __
    V1 = 1
    V2 = 2  
    
    __apiUrl = str()
    __apiKey = str()
    __apiSecret = str()
    __version = int()

    # Инициализация экземпляра класса
    def __init__(self, apiKey = None, apiSecret = None, version = V1):
        self.__apiUrl  = 'https://tradernet.ru/api'
        self.__version = version
        self.__apiKey    = apiKey
        self.__apiSecret = apiSecret


    # preSign используется для подписи с ключом
    def preSign(self, d):
        s=''
        for i in sorted(d):
            if type(d[i]) == dict:
                s += i+'='+self.preSign(d[i])+'&'
            else:
                s += i+'='+str(d[i])+'&'
        
        return s[:-1]

    # httpencode - аналог функции http_build_query для URL-запроса
    def httpencode(self, d,mode=1):
        s=''
        for i in sorted(d):
            if type(d[i]) == dict:
              s += self.httpencode(d[i],i)+'&'
            else:
                if mode == 1: s += i+'='+str(d[i])+'&'
                else        : s += mode + '[' + i + ']=' + str(d[i])+'&'
        
        return s[:-1]


    def sendRequest (self, method, aParams = None, format = 'JSON'):
        aReq = dict()
        aReq['cmd'] = method
        if aParams:
            aReq['params'] = aParams
        if (self.__version != self.V1) and (self.__apiKey):
            aReq['apiKey'] = self.__apiKey
        aReq['nonce'] = int(time.time()*10000)

        preSig = self.preSign(aReq)
        Presig_Enc = self.httpencode(aReq)

        # Создание подписи и выполнение запроса в зависимости от V1 или V2
        if (self.__version == self.V1):
            aReq['sig'] = hmac.new(key=self.__apiSecret.encode()).hexdigest()
            res = requests.post(self.__apiUrl, data={'q':json.dumps(aReq)})
        else:
            apiheaders = {
                'X-NtApi-Sig': hmac.new(key=self.__apiSecret.encode(), msg=preSig.encode('utf-8'), digestmod=hashlib.sha256).hexdigest(),
                'Content-Type': 'application/x-www-form-urlencoded'
                 # Нужно в явном виде указать Content-Type, иначе не будет работать;
                 # по какой-то причине requests.post не может сам это сделать
            }
            self.__apiUrl += '/v2/cmd/'+method
            res = requests.post(self.__apiUrl, params=Presig_Enc, headers=apiheaders, data=Presig_Enc)

        return(res)
