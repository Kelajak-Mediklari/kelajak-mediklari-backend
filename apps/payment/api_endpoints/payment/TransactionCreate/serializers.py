from rest_framework import serializers
from apps.payment.models import Transaction, PaymentProvider


class TransactionCreateSerializer(serializers.ModelSerializer):
    provider_type = serializers.ChoiceField(
        choices=PaymentProvider.choices,
        source='provider',
        help_text="Payment provider type (Payme or Click)"
    )
    course_id = serializers.IntegerField(help_text="Course ID to purchase")
    duration = serializers.IntegerField(
        help_text="Duration in months",
        min_value=1,
        max_value=120
    )

    class Meta:
        model = Transaction
        fields = ['amount', 'provider_type', 'course_id', 'duration']

    def validate_amount(self, value):
        """Validate that amount is positive"""
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero")
        return value
