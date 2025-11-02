import pandas as pd
import json
from typing import Dict, List, Any, Optional
from pathlib import Path
from config.settings import settings

class DataLoader:
    """Utility class to load financial data from files"""
    
    def __init__(self):
        self.data_dir = Path(settings.data_dir)
    
    def load_transactions(self) -> pd.DataFrame:
        """Load transaction data from CSV"""
        try:
            df = pd.read_csv(self.data_dir / "transactions.csv")
            df['date'] = pd.to_datetime(df['date'])
            df['amount'] = pd.to_numeric(df['amount'])
            return df
        except Exception as e:
            print(f"Error loading transactions: {e}")
            return pd.DataFrame()
    
    def load_investments(self) -> List[Dict]:
        """Load investment data from JSON"""
        try:
            with open(self.data_dir / "investments.json", 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading investments: {e}")
            return []
    
    def load_goals(self) -> List[Dict]:
        """Load financial goals from JSON"""
        try:
            with open(self.data_dir / "goals.json", 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading goals: {e}")
            return []
    
    def load_budget(self) -> Dict:
        """Load budget data from JSON"""
        try:
            with open(self.data_dir / "budget.json", 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading budget: {e}")
            return {}