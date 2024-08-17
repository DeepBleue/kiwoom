import os
from PyQt5.QtCore import *
from PyQt5.QtTest import * 
from PyQt5.QtWidgets import *
from PyQt5.QAxContainer import *
from config.kiwoomType import *
from config.errorCode import errors


class RealFunctions:
    def __init__(self, kiwoom):
        self.kiwoom = kiwoom
        

    def register_stock_on_real_time(self):
        for code in self.kiwoom.portfolio_stock_dict.keys():
            secreen_number = self.kiwoom.portfolio_stock_dict[code]['스크린번호']
            fids = self.kiwoom.realType.REALTYPE['주식체결']['체결시간']
            self.kiwoom.dynamicCall("SetRealReg(QString,QString,QString,QString)",secreen_number,code,fids,'1')
            print(f'실시간 등록 코드: {code}, 스크린번호 : {secreen_number}, fid번호 : {fids}')
    
    
    def get_market_time(self):
        self.kiwoom.dynamicCall("SetRealReg(QString,QString,QString,QString)",self.kiwoom.market_time_screen,'',self.kiwoom.realType.REALTYPE['장시작시간']['장운영구분'],'0')

