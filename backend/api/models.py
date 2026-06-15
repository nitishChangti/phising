from django.db import models

class URLScan(models.Model):
    url = models.TextField()
    prediction = models.CharField(max_length=20)  # 'legitimate' or 'phishing'
    confidence = models.FloatField()              # confidence percentage
    risk_level = models.CharField(max_length=20)  # 'safe', 'low', 'medium', 'high', 'critical'
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.url[:50]} - {self.prediction} ({self.confidence}%)"

class SystemMetrics(models.Model):
    """Stores the latest machine learning metrics (percentages) in the database"""
    metrics_data = models.JSONField()
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "System Metrics"

    def __str__(self):
        return f"Metrics updated on {self.updated_at.strftime('%Y-%m-%d %H:%M:%S')}"
