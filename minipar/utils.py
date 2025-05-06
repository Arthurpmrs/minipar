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