from rest_framework import serializers
from apps.payment.models import Transaction


class TransactionDetailSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source='course.title', read_only=True)
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    
    class Meta:
        model = Transaction
        fields = ['id', 'user_name', 'course_title', 'amount', 'status', 'provider', 'created_at', 'paid_at', 'canceled_at']
