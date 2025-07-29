from dataclasses import dataclass

@dataclass
class ConditionReport:
    description: str
    
    def __str__(self):
        return self.description