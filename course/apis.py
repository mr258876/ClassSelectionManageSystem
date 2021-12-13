from .models import *


#######################################
# 课程相关API

# 课程查找API
@login_required
@user_passes_test(user_is_admin)
@require_http_methods(['POST'])
@ensure_csrf_cookie
def search_user_api(request):
    kList = ['courseId', 'name']

    k = request.POST.get("searchMode", "")
    kw = request.POST.get("keyword", "")
    pN = request.POST.get("page", 1)
    iPP = request.POST.get("itemPerPage", 25)
    
    if k and k in kList:
        if k == 'courseId':
            qSet = Course.objects.filter(id__contains=kw).only().values_list('id', 'name', 'credit').order_by('id')
            p = Paginator(qSet, iPP)
            # json_response = serializers.serialize('json', list(p.object_list))
            d = json.dumps(list(p.page(pN)))
            d = json.loads(d)
            plist = p.get_elided_page_range(pN, on_each_side=2, on_ends=1)
            pl = json.dumps(list(plist))
            pl = json.loads(pl)
        elif k == 'name':
            qSet = Course.objects.filter(name__contains=kw).only().values_list('id', 'name', 'credit').order_by('id')
            p = Paginator(qSet, iPP)
            # json_response = serializers.serialize('json', list(p.object_list))
            d = json.dumps(list(p.page(pN)))
            d = json.loads(d)
            plist = p.get_elided_page_range(pN, on_each_side=2, on_ends=1)
            pl = json.dumps(list(plist))
            pl = json.loads(pl)
        else:
            return JsonResponse({"success": False, "code": 400, "message":"操作失败", "data":""})
        return JsonResponse({"success": True, "code": 200, "message":"操作成功", "data":{'courses':d, 'plist':pl, 'page':pN}})
    else:
        return JsonResponse({"success": False, "code": 400, "message":"操作失败", "data":""})

