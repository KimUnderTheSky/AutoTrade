import time
import pyupbit
import datetime

access = "your-access"
secret = "your-secret"


def get_target_price(ticker, k): #이부분을 바꿔야 새로운 전략이 됨
    """변동성 돌파 전략으로 매수 목표가 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=2)
    target_price = df.iloc[0]['close'] + (df.iloc[0]['high'] - df.iloc[0]['low']) * k 
    #코인은 다음날 시가와 붙어있어서 iloc이 다음 날 시가와 같다.
    return target_price

def get_start_time(ticker):
    """시작 시간 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=1)
    start_time = df.index[0]
    return start_time

def get_balance(ticker): #ticker 어떤 코인인지
    """잔고 조회"""
    balances = upbit.get_balances()
    for b in balances:
        if b['currency'] == ticker:
            if b['balance'] is not None:
                return float(b['balance'])
            else:
                return 0
    return 0

def get_current_price(ticker):
    """현재가 조회"""
    return pyupbit.get_orderbook(ticker=ticker)["orderbook_units"][0]["ask_price"]

# 로그인
upbit = pyupbit.Upbit(access, secret)
print("autotrade start")

# 자동매매 시작
while True:
    try:
        now = datetime.datetime.now()
        start_time = get_start_time("KRW-BTC") #시작시간 get_start_time함수로 OHLCV조회할때 일봉으로 조회하면 그날의 시작시간이 나옴 9시로
        end_time = start_time + datetime.timedelta(days=1) #끝나는시간 #1일을 더해준값

        if start_time < now < end_time - datetime.timedelta(seconds=10): #10초를 빼줘서 8시 59분 50초까지 돌아가게해줌
            target_price = get_target_price("KRW-BTC", 0.5)
            current_price = get_current_price("KRW-BTC")
            if target_price < current_price: #목표가보다 현재가가 높다면
                krw = get_balance("KRW") # 내잔고 확인
                if krw > 5000: #잔고에 5000원 이상일때 
                    upbit.buy_market_order("KRW-BTC", krw*0.9995) #비트코인 매수, 수수료 0.05고려
        else: # 8시 59분 50초부터 9시까지 사이에는
            btc = get_balance("BTC") #전량매도
            if btc > 0.00008: #5000원 이상이면? (BTC가격으로 환산한듯)
                upbit.sell_market_order("KRW-BTC", btc*0.9995) # 수수료 고려해서 
        time.sleep(1)
    except Exception as e:#오류 발생시 잡아주는 코드
        print(e)
        time.sleep(1)