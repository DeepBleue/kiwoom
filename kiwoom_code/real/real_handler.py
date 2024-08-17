


def real_data_slot(kiwoom,sCode,sRealType,sRealData):
    '''
        BSTR sCode,        // 종목코드
        BSTR sRealType,    // 실시간타입
        BSTR sRealData    // 실시간 데이터 전문 (사용불가)
    '''
    # print(sCode)
    if sRealType == '장시작시간':
        fid = kiwoom.realType.REALTYPE[sRealType]['장운영구분']
        value = kiwoom.dynamicCall("GetCommRealData(QString,int)",sCode,fid)
    
        if value == '0':
            print('장 시작 전')
            
        elif value == '3':
            print('장 시작')
            
        elif value == '2': 
            print('장 종료, 동시호가로 넘어갑니다.')
            
        elif value == '4':
            print('3시30분 장 종료')


    elif sRealType == '주식체결':

        time_fid = kiwoom.realType.REALTYPE[sRealType]['체결시간']  
        current_price_fid = kiwoom.realType.REALTYPE[sRealType]['현재가']
        com_prev_day_fid = kiwoom.realType.REALTYPE[sRealType]['전일대비']
        fluctuation_fid = kiwoom.realType.REALTYPE[sRealType]['등락율']
        best_selling_price_fid = kiwoom.realType.REALTYPE[sRealType]['(최우선)매도호가']   # 호가창에서 매도쪽 첫부분 
        best_buying_price_fid = kiwoom.realType.REALTYPE[sRealType]['(최우선)매수호가']    # 호가창에서 매수쪽 첫부분 
        volume_fid = kiwoom.realType.REALTYPE[sRealType]['거래량']                        # 틱봉의 거래량 (확실치않음)
        cum_volume_fid = kiwoom.realType.REALTYPE[sRealType]['누적거래량']  
        high_fid = kiwoom.realType.REALTYPE[sRealType]['고가']  
        open_fid = kiwoom.realType.REALTYPE[sRealType]['시가']  
        low_fid = kiwoom.realType.REALTYPE[sRealType]['저가']  
        
        
        time_tick = kiwoom.dynamicCall("GetCommRealData(QString,int)",sCode,time_fid)                             # HHMMSS
        current_price = kiwoom.dynamicCall("GetCommRealData(QString,int)",sCode,current_price_fid)                # +(-) 2500
        com_prev_day = kiwoom.dynamicCall("GetCommRealData(QString,int)",sCode,com_prev_day_fid)                  # +(-) 50
        fluctuation = kiwoom.dynamicCall("GetCommRealData(QString,int)",sCode,fluctuation_fid)                    # +(-) 12.98
        best_selling_price = kiwoom.dynamicCall("GetCommRealData(QString,int)",sCode,best_selling_price_fid)      # +(-) 2500
        best_buying_price = kiwoom.dynamicCall("GetCommRealData(QString,int)",sCode,best_buying_price_fid)        # +(-) 2500
        volume = kiwoom.dynamicCall("GetCommRealData(QString,int)",sCode,volume_fid)                              # +(-) 120000
        cum_volume = kiwoom.dynamicCall("GetCommRealData(QString,int)",sCode,cum_volume_fid)                      # +(-) 39933000
        high = kiwoom.dynamicCall("GetCommRealData(QString,int)",sCode,high_fid)                                  # +(-) 2500
        open = kiwoom.dynamicCall("GetCommRealData(QString,int)",sCode,open_fid)                                  # +(-) 2500
        low = kiwoom.dynamicCall("GetCommRealData(QString,int)",sCode,low_fid)                                    # +(-) 2500
        
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
        
        if sCode not in kiwoom.portfolio_stock_dict:
            kiwoom.portfolio_stock_dict.update({sCode:{}})
            
        kiwoom.portfolio_stock_dict[sCode].update({
            '체결시간': time_tick, 
            '현재가': current_price, 
            '전일대비': com_prev_day, 
            '등락율': fluctuation, 
            '(최우선)매도호가': best_selling_price, 
            '(최우선)매수호가': best_buying_price, 
            '거래량': volume, 
            '누적거래량': cum_volume, 
            '고가': high, 
            '시가': open, 
            '저가': low,
            })

            
        if sCode in kiwoom.account_stock_dict.keys() and sCode not in kiwoom.jango_dict.keys(): 
            # 계좌평가잔고내역에서 이평선을 기준으로 매도
            ma_4 = kiwoom.portfolio_stock_dict[sCode]['ma_4']
            # ma_9 = kiwoom.portfolio_stock_dict[sCode]['ma_9']
            ma_14 = kiwoom.portfolio_stock_dict[sCode]['ma_14']
            # ma_19 = kiwoom.portfolio_stock_dict[sCode]['ma_19']

            ma_5 = (ma_4 * 4 + current_price) / 5
            # ma_10 = (ma_9 * 9 + current_price) / 10
            ma_15 = (ma_14 * 14 + current_price) / 15
            # ma_20 = (ma_19 * 19 + current_price) / 20

            if ma_5 < ma_15 : 

                print(f'계좌평가 잔고내역에서 신규매도를 한다. {sCode}')
                account_stock = kiwoom.account_stock_dict[sCode]

                order_success = kiwoom.send_order(
                    order='신규매도',
                    sCode=sCode,
                    quantity=account_stock['매매가능수량'],
                    price=0,
                    trade_type='시장가',
                    order_number='')
                
                # 주문전달 성공
                if order_success == 0 :
                    print('[계좌] 주문 전달 성공')
                    del kiwoom.account_stock_dict[sCode]    

                # 주문전달 실패 
                else : 
                    print('[계좌] 주문 전달 실패')


        if sCode in kiwoom.jango_dict.keys():

            jan_dict = kiwoom.jango_dict[sCode]
            meme_rate = (current_price - jan_dict['매입단가']) / jan_dict['매입단가'] * 100
            
            if jan_dict['주문가능수량'] > 0 and  meme_rate < -5:
                print(f'잔고에서 신규매도 {sCode}')
                order_success = kiwoom.send_order(
                    order='신규매도',
                    sCode=sCode,
                    quantity=jan_dict['보유수량'],
                    price=0,
                    trade_type='시장가',
                    order_number='')
            
                # 주문전달 성공
                if order_success == 0 :
                    print('[잔고] 주문 전달 성공')  

                # 주문전달 실패 
                else : 
                    print('[잔고] 주문 전달 실패')

            if jan_dict['보유수량'] == 0 : 
                del kiwoom.jango_dict[sCode] 

        
        # print(kiwoom.portfolio_stock_dict)
        
        
        # # 계좌평가잔고내역에 있고 오늘 산 잔고에는 없을 경우 매도 
        # if sCode in kiwoom.account_stock_dict.keys() and sCode not in kiwoom.jango_dict.keys():
        #     print(f'계좌평가 잔고내역에서 신규매도를 한다. {sCode}')
        #     account_stock = kiwoom.account_stock_dict[sCode]
            
        #     # meme_rate = (current_price - account_stock['매입가']) / account_stock['매입가'] * 100
            
            
        #     # if account_stock['매매가능수량'] > 0 and (meme_rate > 5 or meme_rate < -5):
                
        #     order_success = kiwoom.send_order(order = '신규매도', sCode=sCode, quantity=account_stock['매매가능수량'])
            
        #     # 주문전달 성공
        #     if order_success == 0 :
        #         print('주문 전달 성공')
        #         del kiwoom.account_stock_dict[sCode]    # 이건 너무 간단한 식임.. 고려하샘 

        #     # 주문전달 실패 
        #     else : 
        #         print('주문 전달 실패')
        

        # # 오늘 산 잔고에 종목에 있을 경우 매도
        # if sCode in kiwoom.jango_dict.keys():
            
        #     jan_dict = kiwoom.jango_dict[sCode]
        #     # meme_rate = (current_price - jan_dict['매입단가']) / jan_dict['매입단가'] * 100
            
        #     # if jan_dict['주문가능수량'] > 0 and (meme_rate > 5 or meme_rate < -5):
        #     #     print(f'잔고에서 신규매도 {sCode}')
        #     order_success = kiwoom.send_order(order = '신규매도', sCode=sCode, quantity=jan_dict['보유수량'])
            
        #     # 주문전달 성공
        #     if order_success == 0 :
        #         print('주문 전달 성공')

        #     # 주문전달 실패 
        #     else : 
        #         print('주문 전달 실패')
        
        # 등락률이 2.0% 이상이고 오늘 산 잔고에 없을 경우 신규매수
        # elif fluctuation > 2.0 and sCode not in kiwoom.jango_dict.keys():
        #     print(f'신규매수를 한다. {sCode}')
        #     money = 1000000
        #     buy_quan = int(money / current_price)
        #     order_success = kiwoom.send_order(order = '신규매수', sCode=sCode, quantity=buy_quan)
            
        #                     # 주문전달 성공
        #     if order_success == 0 :
        #         print('주문 전달 성공')

        #     # 주문전달 실패 
        #     else : 
        #         print('주문 전달 실패')
        
        
        # 미체결된 종목들 처리 
        
        # michaegul_list = list(kiwoom.michaegul_dict)  # list로 감싸기 때문에 새로운 주소가 할당됨. 
        
        # for order_num in michaegul_list:
            
        #     code = kiwoom.michaegul_dict[order_num]['종목코드']
        #     order_price = kiwoom.michaegul_dict[order_num]['주문가격']
        #     michaegul_num = kiwoom.michaegul_dict[order_num]['미체결수량']
        #     order_gubun = kiwoom.michaegul_dict[order_num]['주문구분']
        
        
        #     if order_gubun == '매수' and michaegul_num > 0 and current_price > order_price : 
        #         print(f'미체결 수 : {michaegul_num}')
        #         order_success = kiwoom.send_order(order = '매수취소',sCode=code,quantity=0,order_number=order_num)  # 0 은 전량 취소
        #         if order_success == 0 :
        #             print('주문 전달 성공')
    
        #         # 주문전달 실패 
        #         else : 
        #             print('주문 전달 실패')
        
            
        #     elif michaegul_num == 0 : 
        #         del kiwoom.michaegul_dict[order_num]
                
                