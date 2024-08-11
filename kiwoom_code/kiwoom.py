import os
from PyQt5.QtCore import *
from PyQt5.QtTest import * 
from PyQt5.QtWidgets import *
from PyQt5.QAxContainer import *
from config.kiwoomType import *
from config.errorCode import errors
import numpy as np
from kiwoom_code.account import AccountFunctions
from kiwoom_code.trdata_handler import trdata_slot


class Kiwoom(QAxWidget):
    def __init__(self):
        super().__init__()


        ######## 인스턴스화 모듈 
        self.account = AccountFunctions(self)


        
        
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
        self.account.event_slot()                   # 이벤트 슬롯 
        self.connect_event_slots()                  # TR event slot 
        self.account.signal_login_CommConnect()     # 로그인하기 
        self.account.get_account_info()             # 계좌번호가져오기
        self.account.detail_acc_info()              # 예수금 가져오기 
        self.account.account_eval()                 # 계좌평가잔고내역
        

        ########### 실시간 

        self.real_event_slot()              # 실시간 데이터 슬롯 
        self.michaegul()                    # 미체결조회
        self.day_chart('005930')            # 일봉조회
        self.calculate_ma()                 # 보유종목 MA 구하기 
        # self.calculator_fn()                # 종목분석용
        # self.read_code()                    # 저장된 종목들 불러오기 
        self.screen_number_set()            # 스크린번호세팅
        self.get_market_time()              # 장시간운영구분
        self.register_stock_on_real_time()  # 실시간 코드등록 , 주식체결 
        
        # for sCode in self.account_stock_dict.keys():
        #     self.send_order(order = '신규매도', sCode=sCode, quantity=self.account_stock_dict[sCode]['매매가능수량'])
    
    
    ################# 함수 모음

    def calculate_ma(self): 
        print(self.account_stock_dict)
        for code , value in self.account_stock_dict.items() : 

            self.day_chart(code) 

    def connect_event_slots(self):
        self.OnReceiveTrData.connect(self.handle_trdata_slot)


    def handle_trdata_slot(self, sScrNo, sRQName, sTrCode, sRecordName, sPrevNext):
        trdata_slot(self, sScrNo, sRQName, sTrCode, sRecordName, sPrevNext)

    
    def register_stock_on_real_time(self):
        for code in self.portfolio_stock_dict.keys():
            secreen_number = self.portfolio_stock_dict[code]['스크린번호']
            fids = self.realType.REALTYPE['주식체결']['체결시간']
            self.dynamicCall("SetRealReg(QString,QString,QString,QString)",secreen_number,code,fids,'1')
            print(f'실시간 등록 코드: {code}, 스크린번호 : {secreen_number}, fid번호 : {fids}')
    
    
    def get_market_time(self):
        self.dynamicCall("SetRealReg(QString,QString,QString,QString)",self.market_time_screen,'',self.realType.REALTYPE['장시작시간']['장운영구분'],'0')



    def real_event_slot(self):
        self.OnReceiveRealData.connect(self.real_data_slot)   # 실시간 종목 정보
        self.OnReceiveChejanData.connect(self.chejan_slot)    # 주문전송 후 주문접수, 체결통보, 잔고통보를 수신

            
    
    def michaegul(self):
        self.dynamicCall(f"SetInputValue(String,String)","계좌번호",self.account_num)
        self.dynamicCall(f"SetInputValue(String,String)",'전체종목구분','0')
        self.dynamicCall(f"SetInputValue(String,String)",'매매구분','0')
        # self.dynamicCall(f"SetInputValue(String,String)",'종목코드','')
        self.dynamicCall(f"SetInputValue(String,String)",'체결구분','0')
        
        self.dynamicCall(f"CommRqData(String,String,int,String)",'미체결요청','OPT10075', '0', self.screen_my_info)
        
        self.michaegul_event_loop = QEventLoop()
        self.michaegul_event_loop.exec_()
        
    def day_chart(self,code,date=None,sPrevNext='0'):
        
        QTest.qWait(3600)
        
        self.dynamicCall(f"SetInputValue(String,String)","종목코드",code)
        if date != None : 
            self.dynamicCall(f"SetInputValue(String,String)","기준일자",date)
        self.dynamicCall(f"SetInputValue(String,String)","수정주가구분","1")
        
        self.dynamicCall(f"CommRqData(String,String,int,String)","주식일봉차트초회요청","OPT10081",sPrevNext,self.day_chart_screen)
        
        if sPrevNext=='0':
            self.day_chart_event_loop = QEventLoop()
            self.day_chart_event_loop.exec_()
            
    def get_code_list_by_market(self,market_code):  # 마켓에 있는 종목코드 반환 
        '''
          0 : 코스피
          10 : 코스닥
          3 : ELW
          8 : ETF
          50 : KONEX
          4 :  뮤추얼펀드
          5 : 신주인수권
          6 : 리츠
          9 : 하이얼펀드
          30 : K-OTC
        '''
        
        code_list = self.dynamicCall("GetCodeListByMarket(QString)",market_code)
        code_list = code_list.split(';')[:-1]
        
        return code_list
    
    
    def calculator_fn(self):  
        '''
        종목분석 함수 
        '''
        code_list = self.get_code_list_by_market('10')
        
        print(f'코스닥 종목 개수 : {len(code_list)}')
        print('종목분석중 ...')
        for idx , code in enumerate(code_list):
            
            self.dynamicCall('DisconnectRealData(QString)',self.day_chart_screen)
            
            
            print(f"KOSDAQ {idx+1}/{len(code_list)} - {code} 분석중 ...")
            self.day_chart(code=code)
        
        print('done')


    def read_code(self):
        
        if os.path.exists("files/condition_stock.txt") : 
            f = open("files/condition_stock.txt","r",encoding = 'utf8') 
            
            lines = f.readlines()
            for line in lines : 
                if line != '' : 
                    ls = line.split('\t')
                    
                    stock_code = ls[0]
                    stock_name = ls[1]
                    stock_price = int(ls[2].split('\n')[0])
                    stock_code = abs(stock_price)
                    
                    self.portfolio_stock_dict.update({stock_code:{'종목명':stock_name,'현재가':stock_price}})
            f.close()
            print(self.portfolio_stock_dict)

    def screen_number_set(self):
        
        screen_overwrite = []
        
        # 계좌평가잔고내역에 있는 종목들 
        for code in self.account_stock_dict.keys():
            if code not in screen_overwrite : 
                screen_overwrite.append(code)
    
        # 미체결에 있는 종목들 
        for order_no in self.michaegul_dict.keys():
            code = self.michaegul_dict[order_no]['종목코드']
            if code not in screen_overwrite : 
                screen_overwrite.append(code)

                
        # 포트폴리오에 있는 종목들 
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
            


    
    def real_data_slot(self,sCode,sRealType,sRealData):
        '''
            BSTR sCode,        // 종목코드
            BSTR sRealType,    // 실시간타입
            BSTR sRealData    // 실시간 데이터 전문 (사용불가)
        '''
        # print(sCode)
        if sRealType == '장시작시간':
            fid = self.realType.REALTYPE[sRealType]['장운영구분']
            value = self.dynamicCall("GetCommRealData(QString,int)",sCode,fid)
       
            if value == '0':
                print('장 시작 전')
                
            elif value == '3':
                print('장 시작')
                
            elif value == '2': 
                print('장 종료, 동시호가로 넘어갑니다.')
                
            elif value == '4':
                print('3시30분 장 종료')
    
    
        elif sRealType == '주식체결':

            time_fid = self.realType.REALTYPE[sRealType]['체결시간']  
            current_price_fid = self.realType.REALTYPE[sRealType]['현재가']
            com_prev_day_fid = self.realType.REALTYPE[sRealType]['전일대비']
            fluctuation_fid = self.realType.REALTYPE[sRealType]['등락율']
            best_selling_price_fid = self.realType.REALTYPE[sRealType]['(최우선)매도호가']   # 호가창에서 매도쪽 첫부분 
            best_buying_price_fid = self.realType.REALTYPE[sRealType]['(최우선)매수호가']    # 호가창에서 매수쪽 첫부분 
            volume_fid = self.realType.REALTYPE[sRealType]['거래량']                        # 틱봉의 거래량 (확실치않음)
            cum_volume_fid = self.realType.REALTYPE[sRealType]['누적거래량']  
            high_fid = self.realType.REALTYPE[sRealType]['고가']  
            open_fid = self.realType.REALTYPE[sRealType]['시가']  
            low_fid = self.realType.REALTYPE[sRealType]['저가']  
            
            
            time_tick = self.dynamicCall("GetCommRealData(QString,int)",sCode,time_fid)                             # HHMMSS
            current_price = self.dynamicCall("GetCommRealData(QString,int)",sCode,current_price_fid)                # +(-) 2500
            com_prev_day = self.dynamicCall("GetCommRealData(QString,int)",sCode,com_prev_day_fid)                  # +(-) 50
            fluctuation = self.dynamicCall("GetCommRealData(QString,int)",sCode,fluctuation_fid)                    # +(-) 12.98
            best_selling_price = self.dynamicCall("GetCommRealData(QString,int)",sCode,best_selling_price_fid)      # +(-) 2500
            best_buying_price = self.dynamicCall("GetCommRealData(QString,int)",sCode,best_buying_price_fid)        # +(-) 2500
            volume = self.dynamicCall("GetCommRealData(QString,int)",sCode,volume_fid)                              # +(-) 120000
            cum_volume = self.dynamicCall("GetCommRealData(QString,int)",sCode,cum_volume_fid)                      # +(-) 39933000
            high = self.dynamicCall("GetCommRealData(QString,int)",sCode,high_fid)                                  # +(-) 2500
            open = self.dynamicCall("GetCommRealData(QString,int)",sCode,open_fid)                                  # +(-) 2500
            low = self.dynamicCall("GetCommRealData(QString,int)",sCode,low_fid)                                    # +(-) 2500
            
            time_tick = time_tick                                   # 체결시간
            current_price = abs(int(current_price))                 # 현재가
            com_prev_day = abs(int(com_prev_day))                   # 전일대비
            fluctuation = float(fluctuation)                        # 등락율
            best_selling_price = abs(int(best_selling_price))       # 최우선매도호가
            best_buying_price = abs(int(best_buying_price))         # 최우선매수호가
            volume = abs(int(volume))                               # 거래량
            cum_volume = abs(int(cum_volume))                       # 누적거래량
            high = abs(int(high))                                   # 고가                
            open = abs(int(open))                                   # 시가
            low = abs(int(low))                                     # 저가
            
            
            if sCode not in self.portfolio_stock_dict:
                self.portfolio_stock_dict.update({sCode:{}})
                
            self.portfolio_stock_dict[sCode].update({'체결시간':time_tick})
            self.portfolio_stock_dict[sCode].update({'현재가':current_price})
            self.portfolio_stock_dict[sCode].update({'전일대비':com_prev_day})
            self.portfolio_stock_dict[sCode].update({'등락율':fluctuation})
            self.portfolio_stock_dict[sCode].update({'(최우선)매도호가':best_selling_price})
            self.portfolio_stock_dict[sCode].update({'(최우선)매수호가':best_buying_price})
            self.portfolio_stock_dict[sCode].update({'거래량':volume})
            self.portfolio_stock_dict[sCode].update({'누적거래량':cum_volume})
            self.portfolio_stock_dict[sCode].update({'고가':high})
            self.portfolio_stock_dict[sCode].update({'시가':open})
            self.portfolio_stock_dict[sCode].update({'저가':low})
            
            # print(self.portfolio_stock_dict)
            
            
            # 계좌평가잔고내역에 있고 오늘 산 잔고에는 없을 경우 매도 
            if sCode in self.account_stock_dict.keys() and sCode not in self.jango_dict.keys():
                print(f'계좌평가 잔고내역에서 신규매도를 한다. {sCode}')
                account_stock = self.account_stock_dict[sCode]
                
                # meme_rate = (current_price - account_stock['매입가']) / account_stock['매입가'] * 100
                
                
                # if account_stock['매매가능수량'] > 0 and (meme_rate > 5 or meme_rate < -5):
                    
                order_success = self.send_order(order = '신규매도', sCode=sCode, quantity=account_stock['매매가능수량'])
                
                # 주문전달 성공
                if order_success == 0 :
                    print('주문 전달 성공')
                    del self.account_stock_dict[sCode]    # 이건 너무 간단한 식임.. 고려하샘 
    
                # 주문전달 실패 
                else : 
                    print('주문 전달 실패')
            

            # 오늘 산 잔고에 종목에 있을 경우 매도
            if sCode in self.jango_dict.keys():
                
                jan_dict = self.jango_dict[sCode]
                # meme_rate = (current_price - jan_dict['매입단가']) / jan_dict['매입단가'] * 100
                
                # if jan_dict['주문가능수량'] > 0 and (meme_rate > 5 or meme_rate < -5):
                #     print(f'잔고에서 신규매도 {sCode}')
                order_success = self.send_order(order = '신규매도', sCode=sCode, quantity=jan_dict['보유수량'])
                
                # 주문전달 성공
                if order_success == 0 :
                    print('주문 전달 성공')
    
                # 주문전달 실패 
                else : 
                    print('주문 전달 실패')
            
            # 등락률이 2.0% 이상이고 오늘 산 잔고에 없을 경우 신규매수
            # elif fluctuation > 2.0 and sCode not in self.jango_dict.keys():
            #     print(f'신규매수를 한다. {sCode}')
            #     money = 1000000
            #     buy_quan = int(money / current_price)
            #     order_success = self.send_order(order = '신규매수', sCode=sCode, quantity=buy_quan)
                
            #                     # 주문전달 성공
            #     if order_success == 0 :
            #         print('주문 전달 성공')
    
            #     # 주문전달 실패 
            #     else : 
            #         print('주문 전달 실패')
            
            
            # 미체결된 종목들 처리 
            
            # michaegul_list = list(self.michaegul_dict)  # list로 감싸기 때문에 새로운 주소가 할당됨. 
            
            # for order_num in michaegul_list:
                
            #     code = self.michaegul_dict[order_num]['종목코드']
            #     order_price = self.michaegul_dict[order_num]['주문가격']
            #     michaegul_num = self.michaegul_dict[order_num]['미체결수량']
            #     order_gubun = self.michaegul_dict[order_num]['주문구분']
            
            
            #     if order_gubun == '매수' and michaegul_num > 0 and current_price > order_price : 
            #         print(f'미체결 수 : {michaegul_num}')
            #         order_success = self.send_order(order = '매수취소',sCode=code,quantity=0,order_number=order_num)  # 0 은 전량 취소
            #         if order_success == 0 :
            #             print('주문 전달 성공')
        
            #         # 주문전달 실패 
            #         else : 
            #             print('주문 전달 실패')
            
                
            #     elif michaegul_num == 0 : 
            #         del self.michaegul_dict[order_num]
                    
                    
                    
    # 주문이 들어가면 ( send order ) 여기로 데이터가 반환됨
    def  chejan_slot(self,sGubun,nItemCnt,sFIdList):
        '''
          BSTR sGubun, // 체결구분. 접수와 체결시 '0'값, 국내주식 잔고변경은 '1'값, 파생잔고변경은 '4'
          LONG nItemCnt,
          BSTR sFIdList
        '''
        # 주문체결
        if int((sGubun)) == 0:
            jumun_chaegul = self.realType.REALTYPE['주문체결']
            
            account_num = self.dynamicCall("GetChejanData(int)",jumun_chaegul['계좌번호'])
            sCode = self.dynamicCall("GetChejanData(int)",jumun_chaegul['종목코드'])[1:]
            stock_name = self.dynamicCall("GetChejanData(int)",jumun_chaegul['종목명'])
            origin_order_no = self.dynamicCall("GetChejanData(int)",jumun_chaegul['원주문번호'])
            order_num = self.dynamicCall("GetChejanData(int)",jumun_chaegul['주문번호'])
            order_status = self.dynamicCall("GetChejanData(int)",jumun_chaegul['주문상태'])
            order_quan = self.dynamicCall("GetChejanData(int)",jumun_chaegul['주문수량'])
            order_price = self.dynamicCall("GetChejanData(int)",jumun_chaegul['주문가격'])
            michaegul_quan = self.dynamicCall("GetChejanData(int)",jumun_chaegul['미체결수량'])
            order_gubun = self.dynamicCall("GetChejanData(int)",jumun_chaegul['주문구분'])
            chaegul_time = self.dynamicCall("GetChejanData(int)",jumun_chaegul['주문/체결시간'])
            chaegul_price = self.dynamicCall("GetChejanData(int)",jumun_chaegul['체결가'])
            cheagul_quan = self.dynamicCall("GetChejanData(int)",jumun_chaegul['체결량'])
            current_price = self.dynamicCall("GetChejanData(int)",jumun_chaegul['현재가'])
            best_sell_price = self.dynamicCall("GetChejanData(int)",jumun_chaegul['(최우선)매도호가'])
            best_buy_price = self.dynamicCall("GetChejanData(int)",jumun_chaegul['(최우선)매수호가'])

            
            account_num = account_num                                         # 8065597211
            sCode = sCode                                                     # 005930
            stock_name = stock_name.strip()                                   # 삼성
            origin_order_no = origin_order_no                                 # 000000 
            order_num = order_num                                             # 0115061 ( 마지막 주문번호 )
            order_status = order_status                                       # 접수, 확인, 체결
            order_quan = int(order_quan)                                      # 245
            order_price = int(order_price)                                    # 75000
            michaegul_quan =int(michaegul_quan)                               # 180
            order_gubun = order_gubun.strip().lstrip('+').lstrip('-')         # +매수, -매도
            chaegul_time = chaegul_time                                       # 151028
            chaegul_price= chaegul_price                                      # 75000
            cheagul_quan = cheagul_quan                                       # 65
            current_price = abs(int(current_price))                           # - 750000
            best_sell_price = abs(int(best_sell_price))                       # - 751000
            best_buy_price = abs(int(best_buy_price))                         # - 750000
            
            
            if chaegul_price == '' : 
                chaegul_price = 0 
            else :  
                chaegul_price = int(chaegul_price)
                
            if cheagul_quan == '':
                cheagul_quan = 0 
            else : 
                cheagul_quan = int(cheagul_quan)
            
            if order_num not in self.michaegul_dict.keys():
                # self.michaegul_dict.update({order_num:{}})
                # self.michaegul_dict[order_num].update({'종목코드':sCode})
                # self.michaegul_dict[order_num].update({'주문번호':order_num})
                # self.michaegul_dict[order_num].update({'종목명':stock_name})
                # self.michaegul_dict[order_num].update({'주문상태':order_status})
                # self.michaegul_dict[order_num].update({'주문수량':order_quan})
                # self.michaegul_dict[order_num].update({'주문가격':order_price})
                # self.michaegul_dict[order_num].update({'미체결수량':michaegul_quan})
                # self.michaegul_dict[order_num].update({'원주문번호':origin_order_no})
                # self.michaegul_dict[order_num].update({'주문구분':order_gubun})
                # self.michaegul_dict[order_num].update({'주문/체결시간':chaegul_time})
                # self.michaegul_dict[order_num].update({'체결가':chaegul_price})
                # self.michaegul_dict[order_num].update({'체결량':cheagul_quan})
                # self.michaegul_dict[order_num].update({'현재가':current_price})
                # self.michaegul_dict[order_num].update({'(최우선)매도호가':best_sell_price})
                # self.michaegul_dict[order_num].update({'(최우선)매수호가':best_buy_price})
                
                self.michaegul_dict.update({order_num:{}})
                self.michaegul_dict[order_num].update({'종목코드':sCode,
                                                       '주문번호':order_num,
                                                       '종목명':stock_name,
                                                       '주문상태':order_status,
                                                       '주문수량':order_quan,
                                                       '주문가격':order_price,
                                                       '미체결수량':michaegul_quan,
                                                       '원주문번호':origin_order_no,
                                                       '주문구분':order_gubun,
                                                       '주문/체결시간':chaegul_time,
                                                       '체결가':chaegul_price,
                                                       '체결량':cheagul_quan,
                                                       '현재가':current_price,
                                                       '(최우선)매도호가':best_sell_price,
                                                       '(최우선)매수호가':best_buy_price
                                                       })


                    
                    
                    
        # 잔고
        elif int(sGubun) == 1 : 
            jango = self.realType.REALTYPE['잔고']
            
            account_num = self.dynamicCall("GetChejanData(int)",jango['계좌번호'])
            sCode = self.dynamicCall("GetChejanData(int)",jango['종목코드'])[1:]
            stock_name = self.dynamicCall("GetChejanData(int)",jango['종목명'])
            current_price = self.dynamicCall("GetChejanData(int)",jango['현재가'])
            stock_quan = self.dynamicCall("GetChejanData(int)",jango['보유수량'])
            avail_quan = self.dynamicCall("GetChejanData(int)",jango['주문가능수량'])
            buy_price = self.dynamicCall("GetChejanData(int)",jango['매입단가'])
            total_buy_price = self.dynamicCall("GetChejanData(int)",jango['총매입가'])
            order_gubun = self.dynamicCall("GetChejanData(int)",jango['매도매수구분'])
            best_sell_price = self.dynamicCall("GetChejanData(int)",jango['(최우선)매도호가'])
            best_buy_price = self.dynamicCall("GetChejanData(int)",jango['(최우선)매수호가'])
            
            account_num = account_num
            sCode = sCode
            stock_name = stock_name.strip()
            current_price = abs(int(current_price))
            stock_quan = int(stock_quan)
            avail_quan = int(avail_quan)
            buy_price = abs(int(buy_price))
            total_buy_price = int(total_buy_price)
            meme_gubun = self.realType.REALTYPE['매도수구분'][order_gubun]
            best_sell_price = abs(int(best_sell_price))
            best_buy_price = abs(int(best_buy_price))
            
            if sCode not in self.jango_dict.keys():
                self.jango_dict.update({sCode:{}})
                self.jango_dict[sCode].update({
                    '현재가':current_price,
                    '종목코드':sCode,
                    '종목명':stock_name,
                    '보유수량':stock_quan,
                    '주문가능수량':avail_quan,
                    '매입단가':buy_price,
                    '매도매수구분':meme_gubun,
                    '(최우선)매도호가':best_sell_price,
                    '(최우선)매수호가':best_buy_price
                })
            
            if stock_quan == 0 :
                del self.jango_dict[sCode]
                self.dynamicCall("SetRealRemove(QString,QString)",self.portfolio_stock_dict[sCode]['스크린번호'],sCode)
            


 
            
    
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
            