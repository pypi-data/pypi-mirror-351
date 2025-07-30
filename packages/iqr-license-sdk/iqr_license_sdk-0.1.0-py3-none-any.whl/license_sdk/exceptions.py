'''
Author: Mr_Yao 2316718372@qq.com
Date: 2024-05-30
Description: 授权SDK异常类定义
'''

class LicenseError(Exception):
    """授权错误基类"""
    pass

class LicenseExpiredError(LicenseError):
    """授权过期错误"""
    pass

class MachineIdMismatchError(LicenseError):
    """机器ID不匹配错误"""
    pass 