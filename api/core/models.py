from django.db import models


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class Issue(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class Customer(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.phone = "".join(c for c in self.phone if c.isdigit())
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.phone})"

class Device(models.Model):
    class Category(models.TextChoices):
        PHONE = "phone", "Phone"
        LAPTOP = "laptop", "Laptop"
        TABLET = "tablet", "Tablet"

    category = models.CharField(max_length=20, choices=Category.choices)
    brand = models.CharField(max_length=30)
    model = models.CharField(max_length=50)
    imei = models.CharField(max_length=15, unique=True, null=True, blank=True)
    color = models.CharField(max_length=30)

    def __str__(self):
        return f"{self.brand} {self.model}"

class Job(TimeStampedModel):
    class JobType(models.TextChoices):
        NEW = "new", "New"
        WARRANTY = "warranty", "Warranty"
        AMC = "amc", "AMC"

    class Priority(models.TextChoices):
        URGENT = "urgent", "Urgent"
        MODERATE = "moderate", "Moderate"
        REGULAR = "regular", "Regular"

    class Status(models.TextChoices):
        OPEN = "open", "Open"
        IN_PROCESS = "in_process", "In process"
        WAITING = "waiting", "Waiting"
        READY_FOR_DELIVERY = "ready_for_delivery", "Ready for delivery"
        DELIVERED = "delivered", "Delivered"
        RETURNED = "returned", "Returned"

    class AssignedTo(models.TextChoices):
        SELF = "self", "Self"

    job_number = models.CharField(max_length=20, unique=True)
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)
    device = models.ForeignKey(Device, on_delete=models.PROTECT)
    job_type = models.CharField(max_length=20, choices=JobType.choices)
    priority = models.CharField(max_length=20, choices=Priority.choices)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.OPEN
    )
    condition = models.TextField()
    issues = models.ManyToManyField(Issue)
    est_cost = models.DecimalField(max_digits=10, decimal_places=2)
    adv_payment = models.DecimalField(max_digits=10, decimal_places=2)
    assigned_to = models.CharField(
        max_length=50, choices=AssignedTo.choices, default=AssignedTo.SELF
    )
    expected_delivery = models.DateField(null=True, blank=True)
    remarks = models.TextField(blank=True)

    def __str__(self):
        return self.job_number
    