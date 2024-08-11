import os 


class UnusedFunction:
    def __init__(self, kiwoom):
        self.kiwoom = kiwoom


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
        
        code_list = self.kiwoom.dynamicCall("GetCodeListByMarket(QString)",market_code)
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
            
            self.kiwoom.dynamicCall('DisconnectRealData(QString)',self.day_chart_screen)
            
            
            print(f"KOSDAQ {idx+1}/{len(code_list)} - {code} 분석중 ...")
            self.kiwoom.day_chart(code=code)
        
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
                    
                    self.kiwoom.portfolio_stock_dict.update({stock_code:{'종목명':stock_name,'현재가':stock_price}})
            f.close()
            print(self.kiwoom.portfolio_stock_dict)