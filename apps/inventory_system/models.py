from django.db import models


class Machine(models.Model):
    display_name = models.TextField(blank=True, null=True)
    inventory_system_id = models.TextField(blank=False, null=False)
    machine_type = models.TextField(blank=True, null=True)
    vendor = models.TextField(blank=True, null=True)
    machine_model_vendor = models.TextField(blank=True, null=True)
    in_use = models.BooleanField(null=False, default=True)

    def __str__(self):
        return '{} - {} ({}, {})'.format(self.machine_type, self.display_name, self.inventory_system_id,
                                         self.machine_model_vendor)


class InventorySystemInfo(models.Model):
    machine = models.ForeignKey(Machine, on_delete=models.CASCADE)
    work_order_number = models.TextField(blank=False, null=False)
    work_order_class = models.TextField(blank=True, null=True)
    work_instruction = models.TextField(blank=True, null=True)
    work_instruction_version = models.TextField(blank=True, null=True)
    work_type = models.TextField(blank=True, null=True)
    long_description = models.TextField(blank=True, null=True)
    site_id = models.TextField(blank=True, null=True)
    group = models.TextField(blank=True, null=True)
    owner = models.TextField(blank=True, null=True)
    supervisor = models.TextField(blank=True, null=True)
    task_under_work_order = models.TextField(blank=True, null=True)
    status = models.TextField(blank=True, null=True)
    target_start = models.DateTimeField(blank=True, null=True)
    target_finish = models.DateTimeField(blank=True, null=True)
    activity_start = models.DateTimeField(blank=True, null=True)
    activity_finish = models.DateTimeField(blank=True, null=True)
    report_date = models.DateTimeField(blank=True, null=True)
    attachment_description = models.TextField(blank=True, null=True)
    attachment_link = models.TextField(blank=True, null=True)
    attachment_owner = models.TextField(blank=True, null=True)
    total_down_time = models.FloatField(blank=True, null=True)
    route = models.TextField(blank=True, null=True)
    preventive_maintenance_template = models.TextField(blank=True, null=True)
    company_evaluation_long_description = models.TextField(blank=True, null=True)
    company_evaluation_signature = models.TextField(blank=True, null=True)
    company_evaluation_date = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return '{} ()'.format(self.work_order_number, self.machine.display_name)

