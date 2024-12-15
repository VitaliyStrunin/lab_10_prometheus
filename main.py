from prometheus_client import Gauge, start_http_server
import psutil
import time
import os
import logging

logger = logging.getLogger(__name__)
cpu_metrics = Gauge("core_usage", "Процент использования ядер", ['core_id'])
total_disk_space = Gauge("disk_space_total", "Память на разделах дисков, ГБ", ['partition'])
used_disk_space = Gauge("disk_space_used", "Используемая память на разделах дисков, ГБ", ['partition'])
total_ram = Gauge("ram_total", "Всего ОЗУ, МБ")
used_ram = Gauge("ram_used", "Используется ОЗУ, МБ")

def get_cpu_info():
    cpu_cores = psutil.cpu_percent(percpu=True)
    for core_id, usage in enumerate(cpu_cores):
        try:
            cpu_metrics.labels(core_id=f"core_{core_id}").set(usage)
        except Exception as e:
            logger.error(f"Ошибка получения информации о ядре: {e}")

def get_ram_info():
    try:
        ram_info = psutil.virtual_memory()
        total_ram.set(ram_info.total / 1024 / 1024)
        used_ram.set(ram_info.used / 1024 / 1024)
    except Exception as e:
        logger.error(f"Ошибка получения информации об ОЗУ: {e}")

def get_disks_info():
    for partition in psutil.disk_partitions():
        try:
            disk_usage = psutil.disk_usage(partition.mountpoint)
            partition_name = partition.device
            total_disk_space.labels(partition=partition_name).set(disk_usage.total / 1024**3)
            used_disk_space.labels(partition=partition_name).set(disk_usage.used / 1024**3)
        except Exception as e:
            logger.error(f": {e}")

if __name__ == "__main__":
    exporter_host = os.getenv("EXPORTER_HOST", "localhost")
    exporter_port = int(os.getenv("EXPORTER_PORT", 9000))
    print(f"Экспортёр доступен по адресу: {exporter_host}:{exporter_port}")
    start_http_server(exporter_port, addr=exporter_host)

    while True:
        get_cpu_info()
        get_ram_info()
        get_disks_info()
        time.sleep(0.5)
