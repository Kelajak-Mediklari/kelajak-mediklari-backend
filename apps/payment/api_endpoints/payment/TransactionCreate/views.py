from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from apps.payment.models import Transaction, TransactionStatus
from apps.course.models import Course
from apps.payment.api_endpoints.payment.TransactionCreate.serializers import TransactionCreateSerializer


class TransactionCreateAPIView(CreateAPIView):
    """
    API endpoint to create a new transaction
    """
    serializer_class = TransactionCreateSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Get course from course_id
        course = get_object_or_404(Course, id=serializer.validated_data['course_id'])

        # Create transaction with user from request and course
        transaction = Transaction.objects.create(
            user=request.user,
            course=course,
            amount=serializer.validated_data['amount'],
            provider=serializer.validated_data['provider'],
            status=TransactionStatus.PENDING
        )

        # Generate payment URL
        payment_url = transaction.payment_url

        return Response({
            'transaction_id': transaction.id,
            'course_id': course.id,
            'amount': transaction.amount,
            'provider': transaction.provider,
            'payment_url': payment_url
        }, status=status.HTTP_201_CREATED)
