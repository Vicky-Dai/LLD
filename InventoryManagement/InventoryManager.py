from typing import Optional

class InventoryManager:
    def __init__(self, warehouse_ids: list[str]):
        self._warehouses: dict[str, Warehouse] = {}
        for id in warehouse_ids:
            self._warehouses[id] = Warehouse(id)

        pass

    def addStock(self, warehouseId, productId, quantity) -> boolean:
        # check exist
        # use warehouse to add stock
        if not warehouseId:
            raise ValueError(f"No such warehouseId: {warehouseId}")
        if not productId:
            raise ValueError(f"No ")
        pass
    
    def transfer(self, productId, fromWarehouseId, toWarehouseId, quantity) -> boolean:
        # check exist
        # check availability
        # remove from 
        # add to
        # getAlerts
        if quantity <= 0:
            return False
        
        if fromWarehouseId == toWarehouseId:
            return False
        
        fromWarehouse = self._warehouses.get(fromWarehouseId)
        toWarehouse = self._warehouses.get(toWarehouseId)
        if not fromWarehouse or not toWarehouse:
            raise ValueError(f"Warehouse does not exist")

        if not fromWarehouse.checkAvailability(productId, quantity):
            raise ValueError(f"Not enough product {productId} in warehouse{fromWarehouseId}")

        first_id = min(int(fromWarehouseId, toWarehouseId))
        second_id = max(int(fromWarehouseId, toWarehouseId))
        first_warehouse = self._warehouses.get(first_id)
        second_warehouse = self._warehouses.get(second_id)
        
        with first_warehouse._lock: # 保持顺序，防止两个thread导致deadlock
            with second_warehouse._lock:
                fromWarehouse.removeStock(productId, quantity)
                toWarehouse.addStock(productId, quantity)

        return True


        pass