from django.contrib import admin
from django.utils.html import format_html

from apps.payment.models import Transaction


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "course",
        "amount",
        "provider",
        "status",
        "paid_at",
        "canceled_at",
        "created_at",
        "payment_link",
    )
    list_display_links = ("id",)
    list_filter = ("provider", "status", "paid_at", "canceled_at", "created_at")
    search_fields = (
        "user__phone",
        "user__full_name",
        "user__email",
        "user__username",
        "course__title",
    )
    date_hierarchy = "created_at"
    readonly_fields = ("paid_at", "canceled_at")

    def payment_link(self, obj):
        url = obj.payment_url
        if url:
            return format_html('<a href="{}" target="_blank">Open</a>', url)
        return "-"

    payment_link.short_description = "Payment URL"
