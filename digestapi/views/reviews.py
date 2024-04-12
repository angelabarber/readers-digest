from rest_framework import viewsets, status, serializers, permissions
from rest_framework.response import Response
from digestapi.models import Review, Book
from datetime import datetime
from django.core.exceptions import ObjectDoesNotExist


class ReviewSerializer(serializers.ModelSerializer):
    is_owner = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = ["id", "book", "user", "rating", "comment", "posted_on", "is_owner"]
        read_only_fields = ["user"]

    def get_is_owner(self, obj):
        # Check if the user is the owner of the review
        return self.context["request"].user == obj.user


class ReviewViewSet(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]

    def list(self, request):
        # Get all reviews
        reviews = Review.objects.all()
        # Serialize the objects, and pass request to determine owner
        serializer = ReviewSerializer(reviews, many=True, context={"request": request})
        # Return the serialized data with 200 status code
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request):
        book_id = request.data.get("book_id")
        rating = request.data.get("rating")
        comment = request.data.get("comment")
        # book = Book.objects.get(pk=book_id)

        review = Review.objects.create(
            user_id=request.user.id,
            rating=rating,
            comment=comment,
            book_id=book_id,
            # posted_on=datetime.now(),
        )

        try:
            serializer = ReviewSerializer(review, context={"request": request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as ex:
            return Response(None, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        try:
            # Get the requested review
            review = Review.objects.get(pk=pk)

            # Serialize the object (make sure to pass the request as context)
            serializer = ReviewSerializer(review, context={"request": request})

            # Return the review with 200 status code
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Review.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def destroy(self, request, pk=None):
        try:
            # Get the requested review
            review = Review.objects.get(pk=pk)

            # Check if the user has permission to delete
            # Will return 403 if authenticated user is not author
            if review.user.id != request.user.id:
                return Response(status=status.HTTP_403_FORBIDDEN)

            # Delete the review
            review.delete()

            # Return success but no body
            return Response(status=status.HTTP_204_NO_CONTENT)

        except Review.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
