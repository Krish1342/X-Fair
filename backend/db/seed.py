from sqlalchemy.orm import Session
from datetime import date, timedelta
from .models import User, Transaction, Goal, Budget, RecurringTransaction
from .database import SessionLocal, engine, Base
from passlib.context import CryptContext

pwd = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def seed_demo():
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()
    try:
        # Create test user (ID 1) for chat testing
        test_user = db.query(User).filter(User.id == 1).first()
        if not test_user:
            test_user = User(
                id=1,
                email="test@example.com",
                name="Test User",
                password_hash=pwd.hash("password123"),
            )
            db.add(test_user)
            db.commit()
            db.refresh(test_user)
        
        # Seed test data for user ID 1
        uid = 1
        
        # Add comprehensive test data
        today = date.today()
        
        # Seed budgets (current & last month)
        budgets = [
            Budget(user_id=uid, category="Food & Dining", budgeted=600, month="2025-10"),
            Budget(user_id=uid, category="Transportation", budgeted=400, month="2025-10"),
            Budget(user_id=uid, category="Entertainment", budgeted=200, month="2025-10"),
            Budget(user_id=uid, category="Shopping", budgeted=300, month="2025-10"),
            Budget(user_id=uid, category="Utilities", budgeted=150, month="2025-10"),
        ]
        for b in budgets:
            if not db.query(Budget).filter(Budget.user_id==uid, Budget.month==b.month, Budget.category==b.category).first():
                db.add(b)

        # Seed goals
        goals = [
            Goal(user_id=uid, name="Emergency Fund", target=10000, current=6500, deadline=date(2025,12,31)),
            Goal(user_id=uid, name="Vacation Fund", target=3000, current=1200, deadline=date(2025,7,1)),
            Goal(user_id=uid, name="Car Down Payment", target=5000, current=800, deadline=date(2026,3,15)),
        ]
        for g in goals:
            if not db.query(Goal).filter(Goal.user_id==uid, Goal.name==g.name).first():
                db.add(g)

        # Seed recurring transactions
        recur = [
            RecurringTransaction(user_id=uid, description="Rent", amount=-1500, category="Housing", start_date=date(2025,1,1), frequency="monthly", interval=1, next_date=date(2025,11,1)),
            RecurringTransaction(user_id=uid, description="Netflix", amount=-15.99, category="Entertainment", start_date=date(2025,8,1), frequency="monthly", interval=1, next_date=date(2025,11,1)),
            RecurringTransaction(user_id=uid, description="Gym Membership", amount=-29.99, category="Health & Fitness", start_date=date(2025,6,1), frequency="monthly", interval=1, next_date=date(2025,11,1)),
        ]
        for r in recur:
            if not db.query(RecurringTransaction).filter(RecurringTransaction.user_id==uid, RecurringTransaction.description==r.description).first():
                db.add(r)


        # Seed realistic transactions for the last 3 months (salary + a few expenses per month)
        txs = []
        for month_offset in range(0, 3):
            salary_date = today - timedelta(days=month_offset*30 + 2)
            txs.append(Transaction(user_id=uid, description=f"Salary Deposit", amount=3500, date=salary_date, category="Income", merchant="Employer"))
            txs.append(Transaction(user_id=uid, description=f"Grocery Shopping", amount=-120.00, date=salary_date + timedelta(days=2), category="Food & Dining", merchant="Walmart"))
            txs.append(Transaction(user_id=uid, description=f"Electric Bill", amount=-85.00, date=salary_date + timedelta(days=5), category="Utilities", merchant="Power Company"))
            txs.append(Transaction(user_id=uid, description=f"Restaurant", amount=-60.00, date=salary_date + timedelta(days=10), category="Food & Dining", merchant="Olive Garden"))
            txs.append(Transaction(user_id=uid, description=f"Gas Station", amount=-50.00, date=salary_date + timedelta(days=15), category="Transportation", merchant="Shell"))
        # Add a couple of small extras
        txs.append(Transaction(user_id=uid, description="Coffee Shop", amount=-5.00, date=today - timedelta(days=3), category="Food & Dining", merchant="Starbucks"))
        txs.append(Transaction(user_id=uid, description="Movie Night", amount=-20.00, date=today - timedelta(days=12), category="Entertainment", merchant="AMC Theaters"))
        txs.append(Transaction(user_id=uid, description="Pharmacy", amount=-15.00, date=today - timedelta(days=18), category="Health & Fitness", merchant="CVS"))
        for t in txs:
            exists = db.query(Transaction).filter(Transaction.user_id==uid, Transaction.description==t.description, Transaction.date==t.date).first()
            if not exists:
                db.add(t)

        # idempotent: check existing demo user
        demo = db.query(User).filter(User.email == "demo@example.com").first()
        if not demo:
            demo = User(
                email="demo@example.com",
                name="Demo User",
                password_hash=pwd.hash("demo123"),
            )
            db.add(demo)
            db.commit()
            db.refresh(demo)

        uid_demo = demo.id

        # Seed budgets for demo user
        budgets_demo = [
            Budget(user_id=uid_demo, category="Food & Dining", budgeted=600, month="2025-10"),
            Budget(user_id=uid_demo, category="Transportation", budgeted=400, month="2025-10"),
            Budget(user_id=uid_demo, category="Entertainment", budgeted=200, month="2025-10"),
            Budget(user_id=uid_demo, category="Shopping", budgeted=300, month="2025-10"),
            Budget(user_id=uid_demo, category="Miscellaneous", budgeted=550, month="2025-09"),
        ]
        for b in budgets_demo:
            if not db.query(Budget).filter(Budget.user_id==uid_demo, Budget.month==b.month, Budget.category==b.category).first():
                db.add(b)

        # Seed goals for demo user
        goals_demo = [
            Goal(user_id=uid_demo, name="Emergency Fund", target=10000, current=6500, deadline=date(2025,12,31)),
            Goal(user_id=uid_demo, name="Vacation Fund", target=3000, current=1200, deadline=date(2025,7,1)),
        ]
        for g in goals_demo:
            if not db.query(Goal).filter(Goal.user_id==uid_demo, Goal.name==g.name).first():
                db.add(g)

        # Seed recurring for demo user
        recur_demo = [
            RecurringTransaction(user_id=uid_demo, description="Rent", amount=-1500, category="Housing", start_date=date(2025,1,1), frequency="monthly", interval=1, next_date=date(2025,10,1)),
            RecurringTransaction(user_id=uid_demo, description="Music Subscription", amount=-9.99, category="Entertainment", start_date=date(2025,8,1), frequency="monthly", interval=1, next_date=date(2025,10,1)),
        ]
        for r in recur_demo:
            if not db.query(RecurringTransaction).filter(RecurringTransaction.user_id==uid_demo, RecurringTransaction.description==r.description).first():
                db.add(r)

        # Seed realistic transactions for demo user for the last 3 months
        txs_demo = []
        for month_offset in range(0, 3):
            salary_date = today - timedelta(days=month_offset*30 + 2)
            txs_demo.append(Transaction(user_id=uid_demo, description=f"Salary Deposit", amount=2500, date=salary_date, category="Income"))
            txs_demo.append(Transaction(user_id=uid_demo, description=f"Grocery Shopping", amount=-90.00, date=salary_date + timedelta(days=2), category="Food & Dining"))
            txs_demo.append(Transaction(user_id=uid_demo, description=f"Electric Bill", amount=-70.00, date=salary_date + timedelta(days=5), category="Utilities"))
            txs_demo.append(Transaction(user_id=uid_demo, description=f"Restaurant", amount=-40.00, date=salary_date + timedelta(days=10), category="Food & Dining"))
            txs_demo.append(Transaction(user_id=uid_demo, description=f"Gas Station", amount=-35.00, date=salary_date + timedelta(days=15), category="Transportation"))
        # Add a couple of small extras
        txs_demo.append(Transaction(user_id=uid_demo, description="Coffee Shop", amount=-4.50, date=today - timedelta(days=3), category="Food & Dining"))
        txs_demo.append(Transaction(user_id=uid_demo, description="Movie Night", amount=-12.00, date=today - timedelta(days=12), category="Entertainment"))
        txs_demo.append(Transaction(user_id=uid_demo, description="Pharmacy", amount=-8.00, date=today - timedelta(days=18), category="Health & Fitness"))
        for t in txs_demo:
            exists = db.query(Transaction).filter(Transaction.user_id==uid_demo, Transaction.description==t.description, Transaction.date==t.date).first()
            if not exists:
                db.add(t)

        db.commit()
        return {"status":"ok","test_user_id": 1, "demo_user_id": uid_demo}
    finally:
        db.close()

if __name__ == "__main__":
    print(seed_demo())
