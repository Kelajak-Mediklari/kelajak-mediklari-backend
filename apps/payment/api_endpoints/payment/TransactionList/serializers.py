from rest_framework import serializers
from apps.payment.models import Transaction


class TransactionListSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source='course.title', read_only=True)
    
    class Meta:
        model = Transaction
        fields = ['id', 'user', 'course_title', 'amount', 'status', 'created_at']
