class Utils:
    @staticmethod
    def is_number(s):
        try:
            float(s)
            return True
        except ValueError:
            return False
        
    @staticmethod
    def to_number(s):
        try:
            return int(s)
        except ValueError:
            try:
                return float(s)
            except ValueError:
                return None
    
    @staticmethod
    def isalpha(s):
        return str(s).isalpha()
    
    @staticmethod
    def strip(s):
        return str(s).strip()
    
    @staticmethod
    def lower(s):
        return str(s).lower()
    
    @staticmethod
    def contains(a: list | dict, b):
        if(isinstance(a, dict)):
            return a.__contains__(b)
        return a.count(b) > 0
    
    @staticmethod
    def sleep(seconds):
        import time
        time.sleep(seconds)
    
    @staticmethod
    def sort(a: list, reverse: bool = False):
        a.sort(reverse=reverse)
        return a
    
    @staticmethod
    def intersection(a: list, b: list):
        return list(set(a) & set(b))
    
    @staticmethod
    def keys(d: dict):
        return d.keys()
    
    @staticmethod
    def sqrt(x):
        import math
        return  math.sqrt(x)
    
    @staticmethod
    def items(d: dict):
        return d.items()