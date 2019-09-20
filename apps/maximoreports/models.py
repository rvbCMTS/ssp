from django.db import models


STATUS_TYPES = (
    ("PL", "PLANNED"),
    ("ST", "STARTED"),
    ("AB", "ABORTED"),
    ("FI", "FINISHED"),
    ("UC", "UNCATEGORIZED")
)


class Asset(models.Model):
    asset_number = models.CharField(max_length=100, null=False, blank=False)
    manufacturer = models.CharField(max_length=400, null=False, blank=False)
    model = models.CharField(max_length=400, null=False, blank=False)
    description = models.CharField(max_length=600, null=False, blank=False)

    def __str__(self):
        return self.asset_number

    class Meta:
        ordering = ["asset_number"]


class WorkOrderStatus(models.Model):
    status = models.CharField(max_length=60, blank=False, null=False)
    status_type = models.CharField(max_length=2, choices=STATUS_TYPES, blank=False, null=False)

    def __str__(self):
        return self.status

    class Meta:
        ordering = ["status"]


class WorkOrderRoute(models.Model):
    route = models.CharField(max_length=400, blank=False, null=False)
    description = models.CharField(max_length=4000, blank=False, null=False)

    def __str__(self):
        return self.description

    class Meta:
        ordering = ["description"]


class WorkOrder(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, blank=False, null=False)
    order_number = models.CharField(max_length=400, blank=False, null=False)
    work_order_class = models.CharField(max_length=400, blank=True, null=True)
    work_type = models.CharField(max_length=400, blank=False, null=False)
    pm_number = models.CharField(max_length=400, blank=True, null=True)
    target_start_date = models.DateTimeField(blank=True, null=True)
    target_complete_date = models.DateTimeField(blank=True, null=True)
    activity_start_date = models.DateTimeField(blank=True, null=True)
    activity_finished_date = models.DateTimeField(blank=True, null=True)
    report_date = models.DateTimeField(blank=True, null=True)
    changed_date = models.DateTimeField(blank=False, null=False)
    status = models.ForeignKey(WorkOrderStatus, on_delete=models.DO_NOTHING)
    supervisor = models.CharField(max_length=400, blank=True, null=True)
    owner = models.CharField(max_length=400, blank=True, null=True)
    route = models.ForeignKey(WorkOrderRoute, on_delete=models.DO_NOTHING, blank=True, null=True)
    siteid = models.CharField(max_length=400, blank=True, null=True)
    is_task = models.BooleanField(blank=True, null=True)

    def __str__(self):
        return f"{self.order_number} ({self.asset.asset_number})"

    class Meta:
        ordering = ["-order_number"]
