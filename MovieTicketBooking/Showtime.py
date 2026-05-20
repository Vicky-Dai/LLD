class Showtime:
    def __init__(self, id:str, theater:Theater, datetime:DateTime, screenLabel:str, 
                 movie:Movie, reservations:None):
        self.id = id
        self._lock = threading.RLock()
        
    def book(self, reservation):
        with self._lock:
            seat_ids = reservation.get_seat_ids()
            
            if not seat_ids:
                raise ValueError(f"Must select at least one seat")
                
            for seat_id in seat_ids:
                if not self._is_valid_seat_id(seat_id):
                    raise ValueError(f"Seat id is invalid:{seat_id}")
                    
            for seat_id in seat_ids:
                if not self.is_available(seat_id):
                    raise ValueError(f"Seat {}")
                    
            self._reservations.append(reservation)
                    
    def is_available(self, seat_id:str):
        for reservation in self.reservations:
            if seat_id in reservation.get_seat_ids():
                return False
        return True
            
    @staticmethod
    def _is_valid_seat_id(seat_id):
        if not seat_id or len(seat_id) < 2:
            return False
        row = seat_id[0]
        line = int(seat_id[1:])
        if "A" <= row <= "Z" and 0 <= line <= 20:
            return True
        return False