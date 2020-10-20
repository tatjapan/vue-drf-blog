import requests

def get_client_ip(request):
    # HTTP_X_FORWARDED_FORは、プロキシサーバー経由時に、アクセス元のIPが入る（空の時もある）
    # ここが空ならばプロキシ経由ではないということで、単純にREMOTE_ADDRでIPを取得
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip_address = x_forwarded_for.split(',')[0]
    else:
        ip_address = request.META.get('REMOTE_ADDR')
    return ip_address