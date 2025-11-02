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

        # Seed diverse recent transactions
        txs = [
            # Recent transactions (last 30 days)
            Transaction(user_id=uid, description="Salary Deposit", amount=3500, date=today - timedelta(days=1), category="Income", merchant="Employer"),
            Transaction(user_id=uid, description="Starbucks Coffee", amount=-5.75, date=today - timedelta(days=1), category="Food & Dining", merchant="Starbucks"),
            Transaction(user_id=uid, description="Gas Station", amount=-45.20, date=today - timedelta(days=2), category="Transportation", merchant="Shell"),
            Transaction(user_id=uid, description="Grocery Shopping", amount=-127.89, date=today - timedelta(days=3), category="Food & Dining", merchant="Walmart"),
            Transaction(user_id=uid, description="Electric Bill", amount=-89.45, date=today - timedelta(days=5), category="Utilities", merchant="Power Company"),
            Transaction(user_id=uid, description="Amazon Purchase", amount=-67.99, date=today - timedelta(days=7), category="Shopping", merchant="Amazon"),
            Transaction(user_id=uid, description="Restaurant Dinner", amount=-78.50, date=today - timedelta(days=8), category="Food & Dining", merchant="Olive Garden"),
            Transaction(user_id=uid, description="Car Insurance", amount=-125.00, date=today - timedelta(days=10), category="Transportation", merchant="State Farm"),
            Transaction(user_id=uid, description="Movie Tickets", amount=-28.50, date=today - timedelta(days=12), category="Entertainment", merchant="AMC Theaters"),
            Transaction(user_id=uid, description="Emergency Fund Transfer", amount=500, date=today - timedelta(days=15), category="Savings", merchant="Bank Transfer"),
            Transaction(user_id=uid, description="Pharmacy", amount=-23.45, date=today - timedelta(days=18), category="Health & Fitness", merchant="CVS"),
            Transaction(user_id=uid, description="Coffee Shop", amount=-4.25, date=today - timedelta(days=20), category="Food & Dining", merchant="Local Cafe"),
        ]
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
            Budget(user_id=uid_demo, category="Food & Dining", budgeted=550, month="2025-09"),
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

        # Seed a few recent transactions for demo user
        txs_demo = [
            Transaction(user_id=uid_demo, description="Coffee Shop", amount=-4.50, date=today - timedelta(days=1), category="Food & Dining"),
            Transaction(user_id=uid_demo, description="Salary Deposit", amount=2500, date=today - timedelta(days=2), category="Income"),
            Transaction(user_id=uid_demo, description="Gas Station", amount=-45.00, date=today - timedelta(days=3), category="Transportation"),
        ]
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
