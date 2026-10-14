import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .utils import recommend_movies


@csrf_exempt
def recommend_view(request):
    if request.method == "POST":
        try:
            body = json.loads(request.body)
            movie_title = body.get("title", "")

            if not movie_title:
                return JsonResponse({"error": "Missing 'title' field"}, status=400)

            matched_title, recommendations = recommend_movies(movie_title)
            payload = {"matched": matched_title, "recommendations": recommendations}
            if matched_title.lower() != movie_title.strip().lower():
                payload["query"] = movie_title.strip()
            return JsonResponse(payload, safe=False)

        except ValueError as e:
            return JsonResponse({"error": str(e)}, status=404)
        except Exception as e:
            return JsonResponse({"error": f"Unexpected error: {str(e)}"}, status=500)

    return JsonResponse({"error": "Only POST method allowed"}, status=405)
