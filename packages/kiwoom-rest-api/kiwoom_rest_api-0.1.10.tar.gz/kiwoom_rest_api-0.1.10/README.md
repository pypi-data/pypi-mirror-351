# Kiwoom REST API
Python client for interacting with [Kiwoom REST API](https://openapi.kiwoom.com/).


## Table of Contents
- [Introduction](#introduction)
- [Features](#features)
- [Installation](#installation)
  - [Using pip](#using-pip)
  - [Using uv](#using-uv)
  - [Using Poetry](#using-poetry)
- [Usage](#Usage)
- [CLI Usage](#CLI-Usage)
  - [Using uvx](#Using-uvx)
  - [Set API Key](#Set-API-Key)
- [Docs](#Docs)
- [License](#license)

## Installation

### using pip
```bash
pip install kiwoom-rest-api
```

### using uv
```
uv add kiwoom-rest-api
```

### using poetry
```
poetry add kiwoom-rest-api
```

## Usage

```python
    import os
    os.environ["KIWOOM_API_KEY"] = "your_api_key"
    os.environ["KIWOOM_API_SECRET"] = "your_api_secret"

    from kiwoom_rest_api.koreanstock.stockinfo import StockInfo
    from kiwoom_rest_api.auth.token import TokenManager

    # 토큰 매니저 초기화
    token_manager = TokenManager()

    # StockInfo 인스턴스 생성 (base_url 수정)
    stock_info = StockInfo(base_url="https://api.kiwoom.com", token_manager=token_manager)

    try:
        result = stock_info.basic_stock_information_request_ka10001("005930")
        print("API 응답:", result)
    except Exception as e:
        print("에러 발생:", str(e))
```

## CLI Usage

### Using uvx
```bash
    uvx --from kiwoom-rest-api kiwoom -k "YOUR_KEY" -s "YOUR_SECRET" ka10001 005930
```

### Set API Key
```bash
    # Linux/macOS/Windows(git bash)
    export KIWOOM_API_KEY="YOUR_ACTUAL_API_KEY"
    export KIWOOM_API_SECRET="YOUR_ACTUAL_API_SECRET"

    # Windows (CMD)
    set KIWOOM_API_KEY="YOUR_ACTUAL_API_KEY"
    set KIWOOM_API_SECRET="YOUR_ACTUAL_API_SECRET"

    # Windows (PowerShell)
    $env:KIWOOM_API_KEY="YOUR_ACTUAL_API_KEY"
    $env:KIWOOM_API_SECRET="YOUR_ACTUAL_API_SECRET"
```

```bash
    # 가상 환경 활성화 (필요시)
    poetry shell

    # 도움말 보기
    kiwoom --help
    kiwoom ka10001 --help

    # ka10001 명령어 실행 (환경 변수 사용 시)
    kiwoom ka10001 005930 # 삼성전자 예시

    # ka10001 명령어 실행 (옵션 사용 시)
    kiwoom --api-key "YOUR_KEY" --api-secret "YOUR_SECRET" ka10001 005930

    # 다른 base URL 사용 시
    kiwoom --base-url "https://mockapi.kiwoom.com" ka10001 005930
```

# Docs
[pypi](https://pypi.org/project/kiwoom-rest-api/)
[github](https://github.com/bamjun/kiwoom-rest-api)

# License

This project is licensed under the terms of the MIT license.