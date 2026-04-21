from django.contrib import admin
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('price',)
    
@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'product', 'quantity', 'price')
    list_filter = ('order', 'product')
    search_fields = ('order__user__username', 'order__user__email', 'product__name')
    readonly_fields = ('price',)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'created_at', 'address', 'phone', 'total_price', 'total_quantity', 'status')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'user__email', 'address', 'phone')
    inlines = [OrderItemInline]
    readonly_fields = ('created_at', 'updated_at')

    def has_add_permission(self, request):
        return False