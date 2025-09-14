from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated

from apps.payment.models import Transaction
from apps.payment.api_endpoints.payment.TransactionList.serializers import TransactionListSerializer


class TransactionListAPIView(ListAPIView):
    """
    API endpoint to list user's transactions
    """
    serializer_class = TransactionListSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Return transactions for the authenticated user"""
        return Transaction.objects.filter(user=self.request.user).order_by('-created_at')
