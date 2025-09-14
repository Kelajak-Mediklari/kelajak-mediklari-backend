from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from apps.payment.models import Transaction
from apps.payment.api_endpoints.payment.TransactionDetail.serializers import TransactionDetailSerializer


class TransactionDetailAPIView(RetrieveAPIView):
    """
    API endpoint to get transaction details
    """
    serializer_class = TransactionDetailSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Return transactions for the authenticated user"""
        return Transaction.objects.filter(user=self.request.user)
    
    def get_object(self):
        """Get transaction by ID for the authenticated user"""
        transaction_id = self.kwargs.get('transaction_id')
        return get_object_or_404(self.get_queryset(), id=transaction_id)
