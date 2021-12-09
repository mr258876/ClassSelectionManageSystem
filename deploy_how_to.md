# 部署指南 - 使用Django+uWSGI+nginx

## Django部分
打开 scss/settings.py 并将:
```)
    DEBUG = True
    ALLOWED_HOSTS = []
```

更改为：
```)
    DEBUG = False
    ALLOWED_HOSTS = ['*']
```
