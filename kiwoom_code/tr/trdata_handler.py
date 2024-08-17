import numpy as np    


def trdata_slot(kiwoom, sScrNo, sRQName, sTrCode, sRecordName, sPrevNext):
    """Handles the responses from various TR requests."""
    
    if sRQName == "예수금상세현황요청":
        deposit = kiwoom.dynamicCall("GetCommData(String,String,int,String)",sTrCode,sRQName,0,'예수금')
        draw_deposit = kiwoom.dynamicCall("GetCommData(String,String,int,String)",sTrCode,sRQName,0,'출금가능금액')
        
        deposit = int(deposit)
        draw_deposit = int(draw_deposit)
        
        print(f"예수금 : {deposit}")
        print(f'출금가능금액 : {draw_deposit}')
        
        kiwoom.detail_acc_info_event_loop.exit()
    
    elif sRQName == "계좌평가잔고내역":
        total_return = kiwoom.dynamicCall("GetCommData(String,String,int,String)",sTrCode,sRQName,0,'총수익률(%)') 
        total_return = float(total_return)

        print(f"계좌평가잔고내역 총수익률 : {total_return}%")
        
        rows = kiwoom.dynamicCall("GetRepeatCnt(QString,QString)",sTrCode,sRQName)

        for i in range(rows):
            code = kiwoom.dynamicCall("GetCommData(QString,QString,int,QString)",sTrCode,sRQName,i,'종목번호')
            code_name = kiwoom.dynamicCall("GetCommData(QString,QString,int,QString)",sTrCode,sRQName,i,'종목명')
            stock_quantity = kiwoom.dynamicCall("GetCommData(QString,QString,int,QString)",sTrCode,sRQName,i,'보유수량')
            buy_price = kiwoom.dynamicCall("GetCommData(QString,QString,int,QString)",sTrCode,sRQName,i,'매입가')
            earn_rate = kiwoom.dynamicCall("GetCommData(QString,QString,int,QString)",sTrCode,sRQName,i,'수익률(%)')
            current_price = kiwoom.dynamicCall("GetCommData(QString,QString,int,QString)",sTrCode,sRQName,i,'현재가')
            total_buy_amount = kiwoom.dynamicCall("GetCommData(QString,QString,int,QString)",sTrCode,sRQName,i,'매입금액')
            possible_quantity = kiwoom.dynamicCall("GetCommData(QString,QString,int,QString)",sTrCode,sRQName,i,'매매가능수량')
            
            code = code.strip()[1:]
            code_name = code_name.strip()
            stock_quantity = int(stock_quantity)
            buy_price = int(buy_price)
            earn_rate = float(earn_rate.strip())
            current_price = int(current_price)
            total_buy_amount = int(total_buy_amount)
            possible_quantity = int(possible_quantity)
            
            if code in kiwoom.account_stock_dict:
                pass
            else: 
                kiwoom.account_stock_dict[code] = {}
            
            kiwoom.account_stock_dict[code].update({"종목명":code_name})
            kiwoom.account_stock_dict[code].update({"보유수량":stock_quantity})
            kiwoom.account_stock_dict[code].update({"매입가":buy_price})
            kiwoom.account_stock_dict[code].update({"수익률(%)":earn_rate})
            kiwoom.account_stock_dict[code].update({"현재가":current_price})
            kiwoom.account_stock_dict[code].update({"매입금액":total_buy_amount})
            kiwoom.account_stock_dict[code].update({"매매가능수량":possible_quantity})

        if sPrevNext == '2': 
            kiwoom.account_eval(sPrevNext='2')
        else: 
            print(f'계좌 보유 종목 개수 : {len(kiwoom.account_stock_dict)}')
            kiwoom.account_eval_event_loop.exit()
    
    elif sRQName == '미체결요청':
        rows = kiwoom.dynamicCall("GetRepeatCnt(QString,QString)",sTrCode,sRQName)
        
        for i in range(rows):
            code = kiwoom.dynamicCall("GetCommData(String,String,int,String)",sTrCode,sRQName,i,'종목코드') 
            code_name = kiwoom.dynamicCall("GetCommData(String,String,int,String)",sTrCode,sRQName,i,'종목명')       
            order_no = kiwoom.dynamicCall("GetCommData(String,String,int,String)",sTrCode,sRQName,i,'주문번호')  
            status = kiwoom.dynamicCall("GetCommData(String,String,int,String)",sTrCode,sRQName,i,'주문상태')
            quantity = kiwoom.dynamicCall("GetCommData(String,String,int,String)",sTrCode,sRQName,i,'주문수량') 
            price = kiwoom.dynamicCall("GetCommData(String,String,int,String)",sTrCode,sRQName,i,'주문가격') 
            order = kiwoom.dynamicCall("GetCommData(String,String,int,String)",sTrCode,sRQName,i,'주문구분')
            michaegul_num = kiwoom.dynamicCall("GetCommData(String,String,int,String)",sTrCode,sRQName,i,'미체결수량') 
            chagul_num = kiwoom.dynamicCall("GetCommData(String,String,int,String)",sTrCode,sRQName,i,'체결량') 
            
            code = code.strip()
            code_name = code_name.strip()
            order_no = int(order_no)
            status = status.strip()
            quantity = int(quantity)
            price = int(price)
            order = order.strip().lstrip('+').lstrip('-')
            michaegul_num = int(michaegul_num)
            chagul_num = int(chagul_num)

            if order_no in kiwoom.michaegul_dict:
                pass
            else: 
                kiwoom.michaegul_dict[order_no] = {}
                
            _michaegul_dict = kiwoom.michaegul_dict[order_no]
            _michaegul_dict.update({'종목코드':code})
            _michaegul_dict.update({'종목명':code_name})
            _michaegul_dict.update({'주문번호':order_no})
            _michaegul_dict.update({'주문상태':status})
            _michaegul_dict.update({'주문수량':quantity})
            _michaegul_dict.update({'주문가격':price})
            _michaegul_dict.update({'주문구분':order})
            _michaegul_dict.update({'미체결수량':michaegul_num})
            _michaegul_dict.update({'체결량':chagul_num})
        
        print(f'미체결 종목 개수 : {len(kiwoom.michaegul_dict)}')
        kiwoom.michaegul_event_loop.exit()
    
    elif sRQName == '주식일봉차트초회요청': 
        code = kiwoom.dynamicCall("GetCommData(String,String,int,String)",sTrCode,sRQName,0,'종목코드') 
        rows = kiwoom.dynamicCall("GetRepeatCnt(QString,QString)",sTrCode,sRQName)

        code = code.strip()
        print(f'code : {code}')
        
        ma_4, ma_9, ma_14, ma_19 = [], [], [], []
        for i in range(rows):
            close = int(kiwoom.dynamicCall("GetCommData(String,String,int,String)",sTrCode,sRQName,i,'현재가').strip())
            date = kiwoom.dynamicCall("GetCommData(String,String,int,String)",sTrCode,sRQName,i,'일자').strip()
            
            if i < 4: ma_4.append(close)
            if i < 9: ma_9.append(close)
            if i < 14: ma_14.append(close)
            if i < 19: ma_19.append(close)
        
        ma_4 = np.mean(np.array(ma_4))
        ma_9 = np.mean(np.array(ma_9))
        ma_14 = np.mean(np.array(ma_14))
        ma_19 = np.mean(np.array(ma_19))

        if code not in kiwoom.account_stock_dict:
            kiwoom.account_stock_dict[code] = {}

        kiwoom.account_stock_dict[code].update({"ma_4":ma_4})
        kiwoom.account_stock_dict[code].update({"ma_9":ma_9})
        kiwoom.account_stock_dict[code].update({"ma_14":ma_14})
        kiwoom.account_stock_dict[code].update({"ma_19":ma_19})
        
        print(ma_4)
        print(ma_9)
        print(ma_14)
        print(ma_19)
        print(kiwoom.account_stock_dict)
        kiwoom.day_chart_event_loop.exit()
  
            # if sPrevNext == '2':
            #     self.kiwoom.day_chart(code=code,sPrevNext=sPrevNext)
            
            # else : 
            #     print(self.kiwoom.day_data_all)
            #     self.kiwoom.day_chart_event_loop.exit()   
