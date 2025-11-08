from sqlalchemy.orm import Session
from datetime import date, timedelta, datetime
from .models import User, Transaction, Goal, Budget, RecurringTransaction, Stock, MutualFund
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

        # Seed stocks for test user
        stocks = [
            Stock(user_id=uid, symbol="AAPL", name="Apple Inc.", quantity=10, avg_buy_price=150.00, current_price=178.50, exchange="NASDAQ", currency="USD", last_updated=datetime.now()),
            Stock(user_id=uid, symbol="MSFT", name="Microsoft Corporation", quantity=5, avg_buy_price=280.00, current_price=370.25, exchange="NASDAQ", currency="USD", last_updated=datetime.now()),
            Stock(user_id=uid, symbol="GOOGL", name="Alphabet Inc.", quantity=8, avg_buy_price=110.00, current_price=138.75, exchange="NASDAQ", currency="USD", last_updated=datetime.now()),
            Stock(user_id=uid, symbol="TSLA", name="Tesla Inc.", quantity=3, avg_buy_price=220.00, current_price=245.80, exchange="NASDAQ", currency="USD", last_updated=datetime.now()),
            Stock(user_id=uid, symbol="RELIANCE.NS", name="Reliance Industries Ltd", quantity=20, avg_buy_price=2400.00, current_price=2650.50, exchange="NSE", currency="INR", last_updated=datetime.now()),
            Stock(user_id=uid, symbol="TCS.NS", name="Tata Consultancy Services", quantity=15, avg_buy_price=3200.00, current_price=3580.25, exchange="NSE", currency="INR", last_updated=datetime.now()),
            Stock(user_id=uid, symbol="INFY.NS", name="Infosys Limited", quantity=25, avg_buy_price=1400.00, current_price=1520.75, exchange="NSE", currency="INR", last_updated=datetime.now()),
            Stock(user_id=uid, symbol="HDFCBANK.NS", name="HDFC Bank Limited", quantity=12, avg_buy_price=1550.00, current_price=1675.30, exchange="NSE", currency="INR", last_updated=datetime.now()),
        ]
        for s in stocks:
            if not db.query(Stock).filter(Stock.user_id==uid, Stock.symbol==s.symbol).first():
                db.add(s)

        # Seed mutual funds for test user
        mutual_funds = [
            MutualFund(user_id=uid, scheme_code="120503", scheme_name="SBI Bluechip Fund - Direct Growth", fund_house="SBI Mutual Fund", units=250.50, avg_nav=65.50, current_nav=72.80, scheme_type="Equity", sip_amount=5000, sip_date=5, currency="INR", last_updated=datetime.now()),
            MutualFund(user_id=uid, scheme_code="118989", scheme_name="HDFC Mid-Cap Opportunities Fund - Direct Growth", fund_house="HDFC Mutual Fund", units=180.75, avg_nav=110.25, current_nav=128.50, scheme_type="Equity", sip_amount=3000, sip_date=10, currency="INR", last_updated=datetime.now()),
            MutualFund(user_id=uid, scheme_code="119551", scheme_name="ICICI Prudential Balanced Advantage Fund - Direct Growth", fund_house="ICICI Prudential Mutual Fund", units=320.00, avg_nav=48.75, current_nav=52.30, scheme_type="Hybrid", sip_amount=4000, sip_date=15, currency="INR", last_updated=datetime.now()),
            MutualFund(user_id=uid, scheme_code="120836", scheme_name="Axis Bluechip Fund - Direct Growth", fund_house="Axis Mutual Fund", units=150.25, avg_nav=45.80, current_nav=50.25, scheme_type="Equity", currency="INR", last_updated=datetime.now()),
            MutualFund(user_id=uid, scheme_code="119597", scheme_name="Parag Parikh Flexi Cap Fund - Direct Growth", fund_house="PPFAS Mutual Fund", units=200.00, avg_nav=52.50, current_nav=61.75, scheme_type="Equity", sip_amount=6000, sip_date=1, currency="INR", last_updated=datetime.now()),
            MutualFund(user_id=uid, scheme_code="120828", scheme_name="Kotak Emerging Equity Fund - Direct Growth", fund_house="Kotak Mahindra Mutual Fund", units=175.50, avg_nav=58.25, current_nav=65.90, scheme_type="Equity", sip_amount=3500, sip_date=20, currency="INR", last_updated=datetime.now()),
        ]
        for mf in mutual_funds:
            if not db.query(MutualFund).filter(MutualFund.user_id==uid, MutualFund.scheme_code==mf.scheme_code).first():
                db.add(mf)

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

        # Seed stocks for demo user
        stocks_demo = [
            Stock(user_id=uid_demo, symbol="NVDA", name="NVIDIA Corporation", quantity=4, avg_buy_price=450.00, current_price=495.30, exchange="NASDAQ", currency="USD", last_updated=datetime.now()),
            Stock(user_id=uid_demo, symbol="META", name="Meta Platforms Inc.", quantity=6, avg_buy_price=300.00, current_price=328.75, exchange="NASDAQ", currency="USD", last_updated=datetime.now()),
            Stock(user_id=uid_demo, symbol="AMZN", name="Amazon.com Inc.", quantity=7, avg_buy_price=135.00, current_price=148.25, exchange="NASDAQ", currency="USD", last_updated=datetime.now()),
            Stock(user_id=uid_demo, symbol="WIPRO.NS", name="Wipro Limited", quantity=30, avg_buy_price=420.00, current_price=465.50, exchange="NSE", currency="INR", last_updated=datetime.now()),
            Stock(user_id=uid_demo, symbol="ITC.NS", name="ITC Limited", quantity=50, avg_buy_price=390.00, current_price=425.75, exchange="NSE", currency="INR", last_updated=datetime.now()),
        ]
        for s in stocks_demo:
            if not db.query(Stock).filter(Stock.user_id==uid_demo, Stock.symbol==s.symbol).first():
                db.add(s)

        # Seed mutual funds for demo user
        mutual_funds_demo = [
            MutualFund(user_id=uid_demo, scheme_code="120716", scheme_name="Mirae Asset Large Cap Fund - Direct Growth", fund_house="Mirae Asset Mutual Fund", units=220.00, avg_nav=75.50, current_nav=82.25, scheme_type="Equity", sip_amount=4500, sip_date=7, currency="INR", last_updated=datetime.now()),
            MutualFund(user_id=uid_demo, scheme_code="119600", scheme_name="UTI Flexi Cap Fund - Direct Growth", fund_house="UTI Mutual Fund", units=160.25, avg_nav=95.75, current_nav=105.80, scheme_type="Equity", sip_amount=3500, sip_date=12, currency="INR", last_updated=datetime.now()),
            MutualFund(user_id=uid_demo, scheme_code="120465", scheme_name="DSP Equity Opportunities Fund - Direct Growth", fund_house="DSP Mutual Fund", units=190.50, avg_nav=68.25, current_nav=74.90, scheme_type="Equity", currency="INR", last_updated=datetime.now()),
        ]
        for mf in mutual_funds_demo:
            if not db.query(MutualFund).filter(MutualFund.user_id==uid_demo, MutualFund.scheme_code==mf.scheme_code).first():
                db.add(mf)

        db.commit()
        return {"status":"ok","test_user_id": 1, "demo_user_id": uid_demo}
    finally:
        db.close()

if __name__ == "__main__":
    print(seed_demo())
