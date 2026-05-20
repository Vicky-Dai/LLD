import threading #！！！！！！
from typing import Optional


class AlertToFire:
    def __init__(self, listener: "AlertListener", product_id: str, quantity: int):
        self.listener = listener
        self.product_id = product_id
        self.quantity = quantity


class Warehouse:
    def __init__(self, warehouse_id: str):
        self._id = warehouse_id
        self._inventory: dict[str, int] = {}
        self._alert_configs: dict[str, list[AlertConfig]] = {} # 每个product_id对应一个config
        self._lock = threading.RLock()

    def get_id(self) -> str:
        return self._id

    def add_stock(self, product_id: str, quantity: int) -> None:
        # check valid
        if quantity <= 0:
            raise ValueError("Quantity must be positive")

        alerts_to_fire: Optional[list[AlertToFire]] = None
        # add stcok and get the alerts
        with self._lock:
            current_qty = self._inventory.get(product_id, 0)
            new_qty = current_qty + quantity
            self._inventory[product_id] = new_qty
            alerts_to_fire = self._get_alerts_to_fire(product_id, current_qty, new_qty)
        # fire alerts
        if alerts_to_fire:
            for alert in alerts_to_fire:
                alert.listener.on_low_stock(self._id, alert.product_id, alert.quantity)

    def remove_stock(self, product_id: str, quantity: int) -> bool:
        if quantity <= 0:
            return False

        alerts_to_fire: Optional[list[AlertToFire]] = None

        with self._lock:
            current_qty = self._inventory.get(product_id, 0)
            if current_qty < quantity:
                return False

            new_qty = current_qty - quantity
            self._inventory[product_id] = new_qty
            alerts_to_fire = self._get_alerts_to_fire(product_id, current_qty, new_qty)

        if alerts_to_fire:
            for alert in alerts_to_fire:
                alert.listener.on_low_stock(self._id, alert.product_id, alert.quantity)

        return True

    def get_stock(self, product_id: str) -> int:
        with self._lock:
            return self._inventory.get(product_id, 0)

    def check_availability(self, product_id: str, quantity: int) -> bool:
        if quantity <= 0:
            return False

        with self._lock:
            current_qty = self._inventory.get(product_id, 0)
            return current_qty >= quantity

    def set_low_stock_alert( # 初始化的时候外部调用增加config
        self, product_id: str, threshold: int, listener: "AlertListener"
    ) -> None:
        if threshold <= 0:
            raise ValueError("Threshold must be positive")
        if listener is None:
            raise ValueError("Listener cannot be None")

        with self._lock:
            if product_id not in self._alert_configs:
                self._alert_configs[product_id] = []

            config = AlertConfig(threshold, listener)
            self._alert_configs[product_id].append(config)

    def _get_alerts_to_fire( # 查找需要触发的alert
        self, product_id: str, previous_qty: int, new_qty: int
    ) -> Optional[list[AlertToFire]]:
        configs = self._alert_configs.get(product_id)
        if not configs:
            return None

        alerts_to_fire: list[AlertToFire] = []

        for config in configs: # 判断根据config有没有需要报警的
            if previous_qty >= config.get_threshold() and new_qty < config.get_threshold():
                alerts_to_fire.append(
                    AlertToFire(config.get_listener(), product_id, new_qty)
                )

        return alerts_to_fire if alerts_to_fire else None

