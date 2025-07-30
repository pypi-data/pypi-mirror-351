'''
Author: Mr_Yao 2316718372@qq.com
Date: 2024-05-30
Description: 授权SDK核心实现
'''
import requests
import json
import base64
from typing import Dict, Any, Optional
import os
import sys
from cryptography.fernet import Fernet
from datetime import datetime
from .exceptions import LicenseError, LicenseExpiredError, MachineIdMismatchError

class LicenseSDK:
    """授权码SDK类"""
    
    def __init__(self, auth_server_url: str, key: str):
        """
        初始化SDK
        
        Args:
            auth_server_url: 授权服务器地址，例如：http://localhost:1153
            key: 加密密钥
        """
        self.auth_server_url = auth_server_url.rstrip('/')
        self.encryption_key = key.encode() if isinstance(key, str) else key
            
    def _encrypt_data(self, data: Dict[str, Any]) -> bytes:
        """加密数据"""
        try:
            f = Fernet(self.encryption_key)
            return f.encrypt(json.dumps(data).encode())
        except Exception as e:
            raise LicenseError(f"加密错误: {str(e)}")
            
    def _decrypt_data(self, encrypted_data: bytes) -> Dict[str, Any]:
        """解密数据"""
        try:
            f = Fernet(self.encryption_key)
            return json.loads(f.decrypt(encrypted_data).decode())
        except Exception as e:
            raise LicenseError(f"解密错误: {str(e)}")
        
    def verify_license(self) -> Dict[str, Any]:
        """
        验证授权信息
        
        Returns:
            Dict[str, Any]: 包含以下字段的字典：
                - status: 状态（success/error）
                - authorized: 是否授权
                - message: 错误信息（如果有）
                - data: 授权数据（如果成功）
        """
        try:
            # 从授权服务器获取原始授权信息
            response = requests.get(f"{self.auth_server_url}/get_raw_license")
            if response.status_code != 200:
                return {
                    'status': 'error',
                    'authorized': False,
                    'message': f"获取授权信息失败: {response.text}"
                }
                
            result = response.json()
            if result['status'] != 'success':
                return {
                    'status': 'error',
                    'authorized': False,
                    'message': result['message']
                }
                
            # 解析授权信息
            license_data = self._parse_license_data(result['license_data'])
            
            return {
                'status': 'success',
                'authorized': True,
                'data': license_data
            }
            
        except requests.RequestException as e:
            return {
                'status': 'error',
                'authorized': False,
                'message': f"连接授权服务器失败: {str(e)}"
            }
        except Exception as e:
            return {
                'status': 'error',
                'authorized': False,
                'auth_url':self.auth_server_url,
                'message': f"验证授权失败: {str(e)}"
            }
            
    def _parse_license_data(self, license_base64: str) -> Dict[str, Any]:
        """
        解析授权数据
        
        Args:
            license_base64: base64编码的授权数据
            
        Returns:
            Dict[str, Any]: 解析后的授权数据
        """
        try:
            # 解码base64数据
            encrypted_data = base64.b64decode(license_base64)
            license_data = self._decrypt_data(encrypted_data)
            
            # 验证到期时间
            expiry_date = datetime.strptime(license_data.get('expiry_date'), '%Y-%m-%d')
            if datetime.now() > expiry_date:
                raise LicenseExpiredError("授权已过期")
                
            return {
                'license_key': license_data.get('license_key'),
                'expiry_date': license_data.get('expiry_date'),
                'activation_date': license_data.get('activation_date'),
                'max_devices': license_data.get('max_devices'),
                'last_check': license_data.get('last_check')
            }
            
        except base64.binascii.Error:
            raise LicenseError("授权数据格式错误")
        except json.JSONDecodeError:
            raise LicenseError("授权数据解析失败")
        except Exception as e:
            raise LicenseError(f"解析授权数据失败: {str(e)}")

    def check_license(self) -> Dict[str, Any]:
        """
        检查授权状态的便捷方法
        
        Returns:
            Dict[str, Any]: 授权验证结果
        """
        try:
            # 获取授权信息
            result = self.verify_license()
            
            if result['status'] == 'success':
                return result
            else:
                return {
                    'authorized': False,
                    'auth_url':self.auth_server_url,
                    'message': result['message']
                }
        except Exception as e:
            return {
                'authorized': False,
                'auth_url':self.auth_server_url,
                'message': str(e)
            } 