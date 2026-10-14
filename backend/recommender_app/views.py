from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework import serializers, status
from rest_framework.decorators import api_view, throttle_classes
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle

from .utils import recommend_movies


class RecommendRequestSerializer(serializers.Serializer):
    title = serializers.CharField(min_length=1, max_length=300)
    n = serializers.IntegerField(min_value=1, max_value=50, default=10, required=False)


class MovieSerializer(serializers.Serializer):
    title = serializers.CharField()
    poster = serializers.URLField(allow_null=True)
    release_date = serializers.CharField(allow_null=True)
    vote_average = serializers.FloatField(allow_null=True)
    tmdb_id = serializers.IntegerField(allow_null=True)


class RecommendResponseSerializer(serializers.Serializer):
    matched = serializers.CharField()
    query = serializers.CharField(required=False)
    recommendations = MovieSerializer(many=True)


@extend_schema(
    request=RecommendRequestSerializer,
    responses={200: RecommendResponseSerializer},
    examples=[
        OpenApiExample(
            "Inception",
            value={"title": "Inception"},
            request_only=True,
        )
    ],
    summary="Get movie recommendations",
    description=(
        "Given a movie title, returns up to *n* content-similar movies ranked by "
        "TF-IDF cosine similarity (with optional rating-weighted re-ranking). "
        "Title matching is fuzzy — a near-miss resolves silently; the `matched` "
        "field in the response shows what was actually used."
    ),
)
@api_view(["POST"])
@throttle_classes([AnonRateThrottle])
def recommend_view(request):
    req = RecommendRequestSerializer(data=request.data)
    if not req.is_valid():
        return Response(req.errors, status=status.HTTP_400_BAD_REQUEST)

    title = req.validated_data["title"]
    top_n = req.validated_data.get("n", 10)

    try:
        matched_title, recommendations = recommend_movies(title, top_n=top_n)
    except ValueError as e:
        return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response(
            {"error": f"Unexpected error: {e}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    payload = {"matched": matched_title, "recommendations": recommendations}
    if matched_title.lower() != title.strip().lower():
        payload["query"] = title.strip()

    return Response(payload)
