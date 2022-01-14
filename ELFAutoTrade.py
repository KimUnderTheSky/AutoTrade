import time
import pyupbit
import datetime

access = "your-access"
secret = "your-secret"
flag = True #1번만 매수 저장되라고 저장안되냐고



def get_target_price(ticker, k):
    """변동성 돌파 전략으로 매수 목표가 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=2)
    target_price = df.iloc[0]['close'] + (df.iloc[0]['high'] - df.iloc[0]['low']) * k
    return target_price

def get_start_time(ticker):
    """시작 시간 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=1)
    start_time = df.index[0]
    return start_time

def get_ma5(ticker):
    """5일 이동 평균선 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=5) #file가져오기
    ma5 = df['close'].rolling(5).mean().iloc[-1] #5일씩 나눠서 평균내라 = 이평선구하는 것.
    return ma5

def get_balance(ticker):
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
        start_time = get_start_time("KRW-ELF") #09:00
        end_time = start_time + datetime.timedelta(days=1) #09:00 +1일
        #9시부터 다음날 8시 59분 50초까지 실행
        if start_time < now < end_time - datetime.timedelta(seconds=10): 
            target_price = get_target_price("KRW-ELF", 0.5)
            ma5 = get_ma5("KRW-ELF")
            current_price = get_current_price("KRW-ELF")
            if target_price < current_price and ma5 < current_price: #현재가가 target price이상이고 5일 이평선 이상일때
                krw = get_balance("KRW")
                while True:
                    if(flag): #flag가 True이면 매수
                        if krw > 5000: #krw가 내 잔고 내 전재산
                            df_public = pyupbit.get_ohlcv("KRW-ELF", interval="day", count=2)
                            ago_range = df_public.iloc[0]['high'] - df_public.iloc[0]['low'] #전일변동성
                            ago_range1 = ago_range/current_price #(0.2/ago_range1)/2이 퍼센테이지로 나와야함
                            total = ((0.05/ago_range1)/5)*(krw*0.9995)  # 변동성 조절로 내재산2% 코인자산 20% 변동 픽스
                             #구매
                            if total > 5000: # 총투자 금액이 5000이상이어야 buy
                                upbit.buy_market_order("KRW-ELF", total)
                                flag = False #한번 사면 False값 넣음                            
        else:
            ELF = get_balance("ELF")
            if ELF > 5000/get_current_price("KRW-ELF"):
                upbit.sell_market_order("KRW-ELF", ELF*0.9995)
            flag = True
        time.sleep(1)
    except Exception as e:
        print(e)
        time.sleep(1)