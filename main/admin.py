from django.contrib import admin
from .models import Category, MenuItem, Reservation, Order, OrderItem, Review, MenuItemReview


# =========================
# CATEGORY
# =========================
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'order', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('order', 'is_active')


# =========================
# MENU ITEM
# =========================
@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'is_available')
    list_filter = ('category', 'is_available')
    search_fields = ('name', 'description')
    list_editable = ('price', 'is_available')


# =========================
# RESERVATION
# =========================
@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'date', 'time', 'guests', 'status', 'created_at')
    list_filter = ('status', 'date')
    search_fields = ('name', 'phone', 'email')
    readonly_fields = ('created_at',)


# =========================
# ORDER
# =========================
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'phone', 'status', 'total_price', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('phone', 'id')
    list_editable = ('status',)
    readonly_fields = ('created_at', 'updated_at')


# =========================
# ORDER ITEM
# =========================
@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'item_name', 'quantity', 'price')

    def get_total(self, obj):
        return obj.price * obj.quantity
    get_total.short_description = "Сумма"


# =========================
# REVIEW (SITE)
# =========================
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'is_approved', 'created_at')
    list_filter = ('is_approved', 'created_at')
    search_fields = ('name', 'email', 'message')
    list_editable = ('is_approved',)


# =========================
# MENU ITEM REVIEW
# =========================
@admin.register(MenuItemReview)
class MenuItemReviewAdmin(admin.ModelAdmin):
    list_display = ('menu_item', 'author_name', 'rating', 'is_approved', 'created_at')
    list_filter = ('rating', 'is_approved')
    search_fields = ('author_name', 'text')
    list_editable = ('is_approved',)