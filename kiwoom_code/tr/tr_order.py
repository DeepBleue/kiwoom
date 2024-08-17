import os
from PyQt5.QtCore import *
from PyQt5.QtTest import * 
from PyQt5.QtWidgets import *
from PyQt5.QAxContainer import *
from config.kiwoomType import *
from config.errorCode import errors


class TRFunctions:
    def __init__(self, kiwoom):
        self.kiwoom = kiwoom


    def day_chart(self,code,date=None,sPrevNext='0'):
        
        QTest.qWait(3600)
        
        self.kiwoom.dynamicCall(f"SetInputValue(String,String)","종목코드",code)
        if date != None : 
            self.kiwoom.dynamicCall(f"SetInputValue(String,String)","기준일자",date)
        self.kiwoom.dynamicCall(f"SetInputValue(String,String)","수정주가구분","1")
        
        self.kiwoom.dynamicCall(f"CommRqData(String,String,int,String)","주식일봉차트초회요청","OPT10081",sPrevNext,self.kiwoom.day_chart_screen)
        
        if sPrevNext=='0':
            self.kiwoom.day_chart_event_loop = QEventLoop()
            self.kiwoom.day_chart_event_loop.exec_()