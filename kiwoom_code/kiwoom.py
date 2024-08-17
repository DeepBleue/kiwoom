import os
from PyQt5.QtCore import *
from PyQt5.QtTest import * 
from PyQt5.QtWidgets import *
from PyQt5.QAxContainer import *
from config.kiwoomType import *
from config.errorCode import errors
import numpy as np
from kiwoom_code.account import AccountFunctions
from kiwoom_code.tr.trdata_handler import trdata_slot
from kiwoom_code.real.real_handler import real_data_slot
from kiwoom_code.chejan.chejan_handler import chejan_slot
from kiwoom_code.tr.tr_order import TRFunctions
from kiwoom_code.real.real_order import RealFunctions

class Kiwoom(QAxWidget):
    def __init__(self):
        super().__init__()


        ######## 인스턴스화 모듈 
        self.account = AccountFunctions(self)
        self.tr_order = TRFunctions(self)
        self.real_order = RealFunctions(self)


        ########## 이벤트 루프 모음 
        
        self.login_event_loop = None
        self.detail_acc_info_event_loop = None
        self.account_eval_event_loop = None
        self.michaegul_event_loop = None
        self.day_chart_event_loop =None
        
        
        ########## 변수 모음 
        
        self.realType = RealType()
        self.account_num = None
        self.account_stock_dict = {}
        self.michaegul_dict = {}
        self.day_data_all = []
        self.portfolio_stock_dict = {}
        self.jango_dict = {}
        
        ########### 스크린번호 모음
        
        self.market_time_screen = '1000'  # 장시간 구분 
        self.screen_my_info = '2000'      # 계좌조회
        self.day_chart_screen = '4000'    # 일봉조회 
        self.screen_real_stock = '5000'   # 종목별로할당할 스크린 번호
        self.screen_meme_stock = '6000'   # 종목별 매매할 스크린 번호
        
        
        ########### 함수 실행
        
        print('Kiwoom class')
        self.account.get_ocx_instance()             # 실행
        self.event_slot()                   # 이벤트 슬롯 
        self.account.signal_login_CommConnect()     # 로그인하기 
        self.account.get_account_info()             # 계좌번호가져오기
        self.account.detail_acc_info()              # 예수금 가져오기 
        self.account.account_eval()                 # 계좌평가잔고내역
        self.account.michaegul()                    # 미체결조회
        

        ########### 실시간 

        self.real_event_slot()              # 실시간 데이터 슬롯 
        
        self.tr_order.day_chart('005930')            # 일봉조회
        self.calculate_ma()                 # 보유종목 MA 구하기 
        self.screen_number_set()            # 스크린번호세팅
        self.real_order.get_market_time()              # 장시간운영구분
        self.real_order.register_stock_on_real_time()  # 실시간 코드등록 , 주식체결 
        
        # for sCode in self.account_stock_dict.keys():
        #     self.send_order(order = '신규매도', sCode=sCode, quantity=self.account_stock_dict[sCode]['매매가능수량'])
    
    
    ################# 함수 모음

    def calculate_ma(self): 
        print(self.account_stock_dict)
        for code , value in self.account_stock_dict.items() : 

            self.tr_order.day_chart(code) 


################### 슬롯 설정 ################

    def event_slot(self):
        self.OnEventConnect.connect(self.account.login_slot)
        self.OnReceiveTrData.connect(self.handle_trdata_slot)
        self.OnReceiveMsg.connect(self.account.msg_slot)

    def real_event_slot(self):
        self.OnReceiveRealData.connect(self.handle_realdata_slot)   # 실시간 종목 정보
        self.OnReceiveChejanData.connect(self.handle_chejan_slot)    # 주문전송 후 주문접수, 체결통보, 잔고통보를 수신

    def handle_realdata_slot(self,sCode,sRealType,sRealData):
        real_data_slot(self,sCode,sRealType,sRealData)

    def handle_trdata_slot(self, sScrNo, sRQName, sTrCode, sRecordName, sPrevNext):
        trdata_slot(self, sScrNo, sRQName, sTrCode, sRecordName, sPrevNext)

    def handle_chejan_slot(self,sGubun,nItemCnt,sFIdList):
        chejan_slot(self,sGubun,nItemCnt,sFIdList)


###############################################
 


    def screen_number_set(self):
        
        screen_overwrite = []
        
        # 계좌평가잔고내역에 있는 종목들                 : 보유종목 
        for code in self.account_stock_dict.keys():
            if code not in screen_overwrite : 
                screen_overwrite.append(code)
    
        # 미체결에 있는 종목들                           : 매매처리가 안된종목 ( 매도, 매수 포함)
        for order_no in self.michaegul_dict.keys():
            code = self.michaegul_dict[order_no]['종목코드']
            if code not in screen_overwrite : 
                screen_overwrite.append(code)

                
        # 포트폴리오에 있는 종목들                        : 관심종목 
        for code in self.portfolio_stock_dict.keys():
            if code not in screen_overwrite : 
                screen_overwrite.append(code)
        
        # 스크린번호 할당  
        '''
        스크린 번호는 200개 생성 가능 
        스크린 하나에는 100개의 요청을 할 수 있음
        '''
        
        
        cnt = 0 
        for code in screen_overwrite : 
            temp_screen = int(self.screen_real_stock)
            meme_screen = int(self.screen_meme_stock)
            
            if (cnt % 50) == 0 : # 스크린 하나당 50개의 종목 할당
                temp_screen += 1   
                meme_screen += 1

                self.screen_real_stock = str(temp_screen)
                self.screen_meme_stock = str(meme_screen)
            

            if code in self.portfolio_stock_dict.keys():
                self.portfolio_stock_dict[code].update({'스크린번호':str(self.screen_real_stock)})
                self.portfolio_stock_dict[code].update({'주문용스크린번호':str(self.screen_meme_stock)})
                
            elif code not in self.portfolio_stock_dict.keys(): 
                self.portfolio_stock_dict.update({code : {'스크린번호':str(self.screen_real_stock),'주문용스크린번호':str(self.screen_meme_stock)}})
   
            
            cnt += 1
            
            
    
    def send_order(self,order,sCode,quantity,order_number=''):
        '''
          BSTR sRQName, // 사용자 구분명
          BSTR sScreenNo, // 화면번호
          BSTR sAccNo,  // 계좌번호 10자리
          LONG nOrderType,  // 주문유형 1:신규매수, 2:신규매도 3:매수취소, 4:매도취소, 5:매수정정, 6:매도정정, 7:프로그램매매 매수, 8:프로그램매매 매도
          BSTR sCode, // 종목코드 (6자리)
          LONG nQty,  // 주문수량
          LONG nPrice, // 주문가격
          BSTR sHogaGb,   // 거래구분(혹은 호가구분)은 아래 참고
          BSTR sOrgOrderNo  // 원주문번호. 신규주문에는 공백 입력, 정정/취소시 입력합니다.
        '''
        
        state = None 
        
        if order == '신규매수' or order == '신규매도':
            state = 0 
        else : 
            state = 1
        
 
        gubun = {'신규매수': 1,
                 '신규매도': 2,
                 '매수취소': 3,
                 '매도취소': 4,
                 '매수정정': 5,
                 '매도정정': 6}
        
        gubun_num = gubun[order]
        
        
        order_success = self.dynamicCall("SendOrder(QString,QString,QString,int,QString,int,int,QString,QString)",
                                 [order,
                                 self.portfolio_stock_dict[sCode]['주문용스크린번호'],
                                 self.account_num,
                                 gubun_num,
                                 sCode,
                                 quantity,
                                 state,
                                 self.realType.SENDTYPE['거래구분']['시장가'],
                                 order_number])
        
        return order_success
            