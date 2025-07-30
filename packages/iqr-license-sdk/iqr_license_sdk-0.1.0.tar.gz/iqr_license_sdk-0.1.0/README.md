# IQR License SDK

一个用于软件授权的 SDK 工具包，提供简单易用的授权验证功能。

## 功能特点

- 支持授权码验证
- 支持授权过期检查
- 支持机器 ID 验证
- 使用 Fernet 加密保护授权数据
- 简单易用的 API 接口

## 安装

```bash
pip install iqr-license-sdk
```

## 使用方法

```python
from license_sdk import LicenseSDK

# 初始化SDK
sdk = LicenseSDK(
    auth_server_url="http://your-auth-server.com",
    key="your-encryption-key"
)

# 检查授权
result = sdk.check_license()

if result['authorized']:
    print("授权验证成功！")
    print(f"授权信息：{result['data']}")
else:
    print(f"授权验证失败：{result['message']}")
```

## 依赖要求

- Python >= 3.6
- requests >= 2.25.1
- cryptography >= 3.4.7

## 许可证

MIT License
