from datetime import timedelta
from decimal import Decimal

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from menu.models import Menu
from menuItem.models import MenuItem
from order.models import Order, OrderItem
from restaurant.models import Restaurant
from table.models import Table
from user.models import User


class Command(BaseCommand):
    help = "Create repeatable development data for testing the RestoHub frontend."

    def add_arguments(self, parser):
        parser.add_argument(
            "--password",
            default="RestoHubDemo!2026",
            help="Password assigned to every demo account.",
        )
        parser.add_argument(
            "--allow-production",
            action="store_true",
            help="Explicitly allow seeding while DJANGO_DEBUG=False.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if not settings.DEBUG and not options["allow_production"]:
            raise CommandError(
                "Production seeding is blocked. Pass --allow-production explicitly."
            )

        password = options["password"]
        if not settings.DEBUG and password == "RestoHubDemo!2026":
            raise CommandError(
                "The default local password cannot be used in production. "
                "Pass a different value with --password."
            )

        admin = self._upsert_user(
            email="admin@restohub.local",
            password=password,
            first_name="RestoHub",
            last_name="Admin",
            role=User.RoleChoices.PLATFORM_ADMIN,
            is_staff=True,
            is_superuser=True,
        )
        owner = self._upsert_user(
            email="owner@restohub.local",
            password=password,
            first_name="Ahmad",
            last_name="Owner",
            role=User.RoleChoices.OWNER,
        )

        restaurant, _ = Restaurant.objects.update_or_create(
            email="downtown@restohub.local",
            defaults={
                "name": "RestoHub Downtown",
                "owner": owner,
                "address": "21 Market Street, Hebron",
                "phone": "+970 59 555 0101",
                "description": (
                    "A modern casual restaurant serving burgers, pasta, pizza, "
                    "desserts, and fresh drinks."
                ),
            },
        )

        waiter = self._upsert_user(
            email="waiter@restohub.local",
            password=password,
            first_name="Omar",
            last_name="Waiter",
            role=User.RoleChoices.WAITER,
            restaurant=restaurant,
        )
        chef = self._upsert_user(
            email="chef@restohub.local",
            password=password,
            first_name="Lina",
            last_name="Chef",
            role=User.RoleChoices.CHEF,
            restaurant=restaurant,
        )

        menu, _ = Menu.objects.update_or_create(
            restuarant=restaurant,
            defaults={
                "name": "All-day Menu",
                "description": "RestoHub Downtown's main food and drinks menu.",
            },
        )

        item_specs = [
            ("Classic Burger", "Mains", "12.50", "Beef patty, cheddar, lettuce, tomato, and house sauce."),
            ("Margherita Pizza", "Mains", "10.00", "Tomato sauce, mozzarella, basil, and olive oil."),
            ("Chicken Alfredo", "Mains", "14.75", "Creamy Alfredo pasta with grilled chicken and parmesan."),
            ("BBQ Chicken Wings", "Starters", "9.50", "Crispy wings coated in smoky barbecue sauce."),
            ("Caesar Salad", "Salads", "8.50", "Romaine, parmesan, croutons, and Caesar dressing."),
            ("Fresh Lemonade", "Drinks", "4.00", "Fresh lemon juice, mint, and a touch of sweetness."),
            ("Espresso", "Drinks", "2.75", "A rich double-shot espresso."),
            ("Tiramisu", "Desserts", "6.50", "Coffee-soaked sponge, mascarpone, and cocoa."),
        ]
        items = {}
        for name, category, price, description in item_specs:
            item, _ = MenuItem.objects.update_or_create(
                menu=menu,
                name=name,
                defaults={
                    "category": category,
                    "price": Decimal(price),
                    "description": description,
                },
            )
            items[name] = item

        capacities = [2, 4, 4, 4, 6, 6, 2, 4, 8, 4, 2, 6]
        tables = {}
        for number, capacity in enumerate(capacities, start=1):
            table, _ = Table.objects.update_or_create(
                restaurant=restaurant,
                table_number=number,
                defaults={"capacity": capacity, "status": Table.StatusChoices.AVAILABLE},
            )
            tables[number] = table

        order_specs = [
            (2, Order.StatusChoices.PENDING, 3, "[DEMO] No onions on the burger.", [("Classic Burger", 2), ("Fresh Lemonade", 2)]),
            (3, Order.StatusChoices.PREPARING, 8, "[DEMO] Pizza well done.", [("Margherita Pizza", 1), ("Caesar Salad", 1)]),
            (4, Order.StatusChoices.READY, 13, "[DEMO] Extra napkins, please.", [("Chicken Alfredo", 2), ("Fresh Lemonade", 1)]),
            (5, Order.StatusChoices.SERVED, 28, "[DEMO] Birthday dessert plate.", [("Classic Burger", 1), ("Tiramisu", 2), ("Espresso", 2)]),
            (6, Order.StatusChoices.SERVED, 52, "[DEMO] Sauce served on the side.", [("BBQ Chicken Wings", 2), ("Margherita Pizza", 1)]),
            (7, Order.StatusChoices.CANCELLED, 70, "[DEMO] Customer cancelled before preparation.", [("Caesar Salad", 1)]),
        ]

        active_tables = set()
        for table_number, status, minutes_ago, note, order_items in order_specs:
            order, _ = Order.objects.update_or_create(
                restuarant=restaurant,
                note=note,
                defaults={
                    "table": tables[table_number],
                    "waiter": waiter,
                    "status": status,
                },
            )
            order.order_items.all().delete()
            total = Decimal("0.00")
            for item_name, quantity in order_items:
                menu_item = items[item_name]
                OrderItem.objects.create(
                    order=order,
                    menu_item=menu_item,
                    quantity=quantity,
                    price=menu_item.price,
                )
                total += menu_item.price * quantity
            order.total_price = total
            order.save(update_fields=["total_price", "updated_at"])
            Order.objects.filter(pk=order.pk).update(
                created_at=timezone.now() - timedelta(minutes=minutes_ago),
                updated_at=timezone.now() - timedelta(minutes=max(1, minutes_ago - 2)),
            )
            if status in {
                Order.StatusChoices.PENDING,
                Order.StatusChoices.PREPARING,
                Order.StatusChoices.READY,
            }:
                active_tables.add(table_number)

        Table.objects.filter(
            restaurant=restaurant,
            table_number__in=active_tables,
        ).update(status=Table.StatusChoices.OCCUPIED)

        self.stdout.write(self.style.SUCCESS("RestoHub demo data is ready."))
        self.stdout.write(f"Restaurant: {restaurant.name}")
        self.stdout.write(f"Password for every account: {password}")
        self.stdout.write("  Platform admin: admin@restohub.local")
        self.stdout.write("  Owner:          owner@restohub.local")
        self.stdout.write("  Waiter:         waiter@restohub.local")
        self.stdout.write("  Chef:           chef@restohub.local")
        self.stdout.write(
            f"Created/updated {len(items)} menu items, {len(tables)} tables, "
            f"and {len(order_specs)} sample orders."
        )

    def _upsert_user(
        self,
        *,
        email,
        password,
        first_name,
        last_name,
        role,
        restaurant=None,
        is_staff=False,
        is_superuser=False,
    ):
        user, _ = User.objects.update_or_create(
            email=email,
            defaults={
                "first_name": first_name,
                "last_name": last_name,
                "role": role,
                "restaurant": restaurant,
                "is_active": True,
                "is_staff": is_staff,
                "is_superuser": is_superuser,
            },
        )
        user.set_password(password)
        user.save(update_fields=["password"])
        return user
