from django.contrib import admin
from django.utils.html import format_html

from apps.payment.models import Transaction, PromoCode, UserPromoCode, CoinReservation, PromoCodeReservation


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "course",
        "amount",
        "original_amount",
        "provider",
        "status",
        "promo_code",
        "promo_discount",
        "coins_used",
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


@admin.register(PromoCode)
class PromoCodeAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "code",
        "discount_amount",
        "is_active",
        "courses_count",
        "created_at",
    )
    list_display_links = ("id", "code")
    list_filter = ("is_active", "created_at", "discount")
    search_fields = ("code",)
    date_hierarchy = "created_at"
    filter_horizontal = ("courses",)
    
    def discount_amount(self, obj):
        return f"{obj.discount} coins"
    discount_amount.short_description = "Discount Amount"
    
    def courses_count(self, obj):
        return obj.courses.count()
    courses_count.short_description = "Courses Count"


@admin.register(UserPromoCode)
class UserPromoCodeAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "promocode",
        "is_used",
        "created_at",
    )
    list_display_links = ("id",)
    list_filter = ("is_used", "created_at", "promocode__is_active")
    search_fields = (
        "user__phone",
        "user__full_name",
        "user__email",
        "promocode__code",
    )
    date_hierarchy = "created_at"
    readonly_fields = ("created_at", "updated_at")


@admin.register(CoinReservation)
class CoinReservationAdmin(admin.ModelAdmin):
    list_display = (
        "id", "user", "amount", "transaction", "is_active", "expires_at", "created_at",
    )
    list_filter = ("is_active", "created_at", "expires_at")
    search_fields = ("user__full_name", "user__phone")
    date_hierarchy = "created_at"
    readonly_fields = ("created_at", "updated_at")


@admin.register(PromoCodeReservation)
class PromoCodeReservationAdmin(admin.ModelAdmin):
    list_display = (
        "id", "user", "promocode", "transaction", "is_active", "expires_at", "created_at",
    )
    list_filter = ("is_active", "created_at", "expires_at")
    search_fields = ("user__full_name", "user__phone", "promocode__code")
    date_hierarchy = "created_at"
    readonly_fields = ("created_at", "updated_at")
