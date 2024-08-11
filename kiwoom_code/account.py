import os
from PyQt5.QtCore import *
from PyQt5.QtTest import * 
from PyQt5.QtWidgets import *
from PyQt5.QAxContainer import *
from config.kiwoomType import *
from config.errorCode import errors


class AccountFunctions:
    def __init__(self, kiwoom):
        self.kiwoom = kiwoom

    def get_ocx_instance(self):
        self.kiwoom.setControl('KHOPENAPI.KHOpenAPICtrl.1')  
    
    def event_slot(self):
        self.kiwoom.OnEventConnect.connect(self.login_slot)
        self.kiwoom.OnReceiveMsg.connect(self.msg_slot)
        
    def login_slot(self, errCode):
        err = errors(errCode)
        print(f'로그인 ... {err}')
        self.kiwoom.login_event_loop.exit()
        
    def msg_slot(self, sScrNo, sRQName, sTrCode, msg):
        print(f'스크린 : {sScrNo}, 요청이름 : {sRQName}, tr코드 : {sTrCode} - {msg}')
    
    def signal_login_CommConnect(self):
        self.kiwoom.dynamicCall('CommConnect')
        self.kiwoom.login_event_loop = QEventLoop()
        self.kiwoom.login_event_loop.exec_()
        
    def get_account_info(self):
        account_list = self.kiwoom.dynamicCall("GetLoginInfo(ACCNO)")    
        self.kiwoom.account_num = account_list.split(';')[0]
        print(f'계좌번호 : {self.kiwoom.account_num}')  # 모의 : 8065597211
        
    def detail_acc_info(self): 
        self.kiwoom.dynamicCall(f"SetInputValue(String,String)", "계좌번호", self.kiwoom.account_num)
        self.kiwoom.dynamicCall(f"SetInputValue(String,String)", '비밀번호', '0000')
        self.kiwoom.dynamicCall(f"SetInputValue(String,String)", '비밀번호입력매체구분', '00')
        self.kiwoom.dynamicCall(f"SetInputValue(String,String)", '조회구분', '2')
        self.kiwoom.dynamicCall(f"CommRqData(String,String,int,String)", '예수금상세현황요청', 'OPW00001', '0', self.kiwoom.screen_my_info)
        self.kiwoom.detail_acc_info_event_loop = QEventLoop()
        self.kiwoom.detail_acc_info_event_loop.exec_()
        
    def account_eval(self, sPrevNext="0"):
        self.kiwoom.dynamicCall(f"SetInputValue(String,String)", "계좌번호", self.kiwoom.account_num)
        self.kiwoom.dynamicCall(f"SetInputValue(String,String)", '비밀번호', '0000')
        self.kiwoom.dynamicCall(f"SetInputValue(String,String)", '비밀번호입력매체구분', '00')
        self.kiwoom.dynamicCall(f"SetInputValue(String,String)", '조회구분', '1')
        self.kiwoom.dynamicCall(f"CommRqData(String,String,int,String)", '계좌평가잔고내역', 'OPW00018', sPrevNext, self.kiwoom.screen_my_info)
        
        if sPrevNext == '0':
            self.kiwoom.account_eval_event_loop = QEventLoop()
            self.kiwoom.account_eval_event_loop.exec_()

