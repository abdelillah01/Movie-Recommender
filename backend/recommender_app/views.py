from django.http import JsonResponse
from .utils import get_recommendations

def recommend_view(request):
    title = request.GET.get("title", "")
    if not title:
        return JsonResponse({"error": "Missing 'title' parameter"}, status=400)

    result = get_recommendations(title)
    return JsonResponse(result)


# Create your views here.
