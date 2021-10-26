from django.shortcuts import render


# 主页
def home(request):
    return render(request, "home.html")


# 显示信息
def info(request, *args, **kwargs):
    title = request.session.get("title", "")
    if title:
        del request.session["title"]
    
    info = request.session.get("info", "")
    if info:
        del request.session["info"]

    next_url = request.session.get("next", "")
    if next_url:
        del request.session["next"]

    context = {'title': title,
               'info': info,
               'next': next_url}
    return render(request, "info.html", context)
