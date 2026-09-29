from django.db import transaction
from rest_framework import serializers
from .models import Customer, Device, Issue, Job

# OUTPUT SERIALIZERS

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['name', 'phone']

class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = ['category', 'brand', 'model', 'imei', 'color']

class CustomerListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ["phone"]


class DeviceListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = ["category", "brand", "model"]


class JobListSerializer(serializers.ModelSerializer):
    customer = CustomerListSerializer(read_only=True)
    device = DeviceListSerializer(read_only=True)

    class Meta:
        model = Job
        fields = [
            "job_number",
            "created_at",
            "status",
            "est_cost",
            "customer",
            "device",
        ]

class JobDetailSerializer(serializers.ModelSerializer):
    customer = CustomerSerializer(read_only=True)
    device = DeviceSerializer(read_only=True)
    issues = serializers.SlugRelatedField(
        many=True, read_only=True, slug_field="name"
    )

    class Meta:
        model = Job
        fields = [
            "job_number",
            "customer",
            "device",
            "job_type",
            "priority",
            "status",
            "condition",
            "est_cost",
            "adv_payment",
            "assigned_to",
            "expected_delivery",
            "remarks",
            "created_at",
            "updated_at",
            "issues",
        ]

# INPUT SERIALIZERS

class CustomerInputSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ["name", "phone"]
        extra_kwargs = {"phone": {"validators": []}}


class DeviceInputSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = ["category", "brand", "model", "imei", "color"]
        extra_kwargs = {"imei": {"validators": []}}

class JobCreateSerializer(serializers.ModelSerializer):
    customer = CustomerInputSerializer()
    device = DeviceInputSerializer()
    issues = serializers.ListField(
        child=serializers.CharField(), allow_empty=True
    )

    class Meta:
        model = Job
        fields = [
            "customer",
            "device",
            "job_type",
            "priority",
            "condition",
            "est_cost",
            "adv_payment",
            "assigned_to",
            "expected_delivery",
            "remarks",
            "issues",
        ]

    def validate_issues(self, value):
        known = set(Issue.objects.values_list("name", flat=True))
        unknown = [name for name in value if name not in known]
        if unknown:
            raise serializers.ValidationError(
            f"Unknown issue(s): {', '.join(unknown)}"
            )
        return value

    def create(self, validated_data):
        customer_data = validated_data.pop("customer")
        device_data = validated_data.pop("device")
        issue_names = validated_data.pop("issues")

        with transaction.atomic():
            customer, _ = Customer.objects.get_or_create(
                phone=customer_data["phone"],
                defaults={"name": customer_data["name"]},
            )

            imei = device_data.get("imei")
            if imei:
                device, _ = Device.objects.get_or_create(
                    imei=imei, defaults=device_data
                )
            else:
                device = Device.objects.create(**device_data)

            job = Job.objects.create(
                customer=customer, device=device, **validated_data
            )
            job.issues.set(Issue.objects.filter(name__in=issue_names))

        return job