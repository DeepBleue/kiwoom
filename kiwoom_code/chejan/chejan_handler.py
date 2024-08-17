                
# 주문이 들어가면 ( send order ) 여기로 데이터가 반환됨
def  chejan_slot(kiwoom,sGubun,nItemCnt,sFIdList):
    '''
        BSTR sGubun, // 체결구분. 접수와 체결시 '0'값, 국내주식 잔고변경은 '1'값, 파생잔고변경은 '4'
        LONG nItemCnt,
        BSTR sFIdList
    '''
    # 주문체결
    if int((sGubun)) == 0:
        jumun_chaegul = kiwoom.realType.REALTYPE['주문체결']
        
        account_num = kiwoom.dynamicCall("GetChejanData(int)",jumun_chaegul['계좌번호'])
        sCode = kiwoom.dynamicCall("GetChejanData(int)",jumun_chaegul['종목코드'])[1:]
        stock_name = kiwoom.dynamicCall("GetChejanData(int)",jumun_chaegul['종목명'])
        origin_order_no = kiwoom.dynamicCall("GetChejanData(int)",jumun_chaegul['원주문번호'])
        order_num = kiwoom.dynamicCall("GetChejanData(int)",jumun_chaegul['주문번호'])
        order_status = kiwoom.dynamicCall("GetChejanData(int)",jumun_chaegul['주문상태'])
        order_quan = kiwoom.dynamicCall("GetChejanData(int)",jumun_chaegul['주문수량'])
        order_price = kiwoom.dynamicCall("GetChejanData(int)",jumun_chaegul['주문가격'])
        michaegul_quan = kiwoom.dynamicCall("GetChejanData(int)",jumun_chaegul['미체결수량'])
        order_gubun = kiwoom.dynamicCall("GetChejanData(int)",jumun_chaegul['주문구분'])
        chaegul_time = kiwoom.dynamicCall("GetChejanData(int)",jumun_chaegul['주문/체결시간'])
        chaegul_price = kiwoom.dynamicCall("GetChejanData(int)",jumun_chaegul['체결가'])
        cheagul_quan = kiwoom.dynamicCall("GetChejanData(int)",jumun_chaegul['체결량'])
        current_price = kiwoom.dynamicCall("GetChejanData(int)",jumun_chaegul['현재가'])
        best_sell_price = kiwoom.dynamicCall("GetChejanData(int)",jumun_chaegul['(최우선)매도호가'])
        best_buy_price = kiwoom.dynamicCall("GetChejanData(int)",jumun_chaegul['(최우선)매수호가'])

        
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
        
        if order_num not in kiwoom.michaegul_dict.keys():
            # kiwoom.michaegul_dict.update({order_num:{}})
            # kiwoom.michaegul_dict[order_num].update({'종목코드':sCode})
            # kiwoom.michaegul_dict[order_num].update({'주문번호':order_num})
            # kiwoom.michaegul_dict[order_num].update({'종목명':stock_name})
            # kiwoom.michaegul_dict[order_num].update({'주문상태':order_status})
            # kiwoom.michaegul_dict[order_num].update({'주문수량':order_quan})
            # kiwoom.michaegul_dict[order_num].update({'주문가격':order_price})
            # kiwoom.michaegul_dict[order_num].update({'미체결수량':michaegul_quan})
            # kiwoom.michaegul_dict[order_num].update({'원주문번호':origin_order_no})
            # kiwoom.michaegul_dict[order_num].update({'주문구분':order_gubun})
            # kiwoom.michaegul_dict[order_num].update({'주문/체결시간':chaegul_time})
            # kiwoom.michaegul_dict[order_num].update({'체결가':chaegul_price})
            # kiwoom.michaegul_dict[order_num].update({'체결량':cheagul_quan})
            # kiwoom.michaegul_dict[order_num].update({'현재가':current_price})
            # kiwoom.michaegul_dict[order_num].update({'(최우선)매도호가':best_sell_price})
            # kiwoom.michaegul_dict[order_num].update({'(최우선)매수호가':best_buy_price})
            
            kiwoom.michaegul_dict.update({order_num:{}})
            kiwoom.michaegul_dict[order_num].update({'종목코드':sCode,
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
        jango = kiwoom.realType.REALTYPE['잔고']
        
        account_num = kiwoom.dynamicCall("GetChejanData(int)",jango['계좌번호'])
        sCode = kiwoom.dynamicCall("GetChejanData(int)",jango['종목코드'])[1:]
        stock_name = kiwoom.dynamicCall("GetChejanData(int)",jango['종목명'])
        current_price = kiwoom.dynamicCall("GetChejanData(int)",jango['현재가'])
        stock_quan = kiwoom.dynamicCall("GetChejanData(int)",jango['보유수량'])
        avail_quan = kiwoom.dynamicCall("GetChejanData(int)",jango['주문가능수량'])
        buy_price = kiwoom.dynamicCall("GetChejanData(int)",jango['매입단가'])
        total_buy_price = kiwoom.dynamicCall("GetChejanData(int)",jango['총매입가'])
        order_gubun = kiwoom.dynamicCall("GetChejanData(int)",jango['매도매수구분'])
        best_sell_price = kiwoom.dynamicCall("GetChejanData(int)",jango['(최우선)매도호가'])
        best_buy_price = kiwoom.dynamicCall("GetChejanData(int)",jango['(최우선)매수호가'])
        
        account_num = account_num
        sCode = sCode
        stock_name = stock_name.strip()
        current_price = abs(int(current_price))
        stock_quan = int(stock_quan)
        avail_quan = int(avail_quan)
        buy_price = abs(int(buy_price))
        total_buy_price = int(total_buy_price)
        meme_gubun = kiwoom.realType.REALTYPE['매도수구분'][order_gubun]
        best_sell_price = abs(int(best_sell_price))
        best_buy_price = abs(int(best_buy_price))
        
        if sCode not in kiwoom.jango_dict.keys():
            kiwoom.jango_dict.update({sCode:{}})
            kiwoom.jango_dict[sCode].update({
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
            del kiwoom.jango_dict[sCode]
            kiwoom.dynamicCall("SetRealRemove(QString,QString)",kiwoom.portfolio_stock_dict[sCode]['스크린번호'],sCode)
        


