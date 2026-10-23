"""
Finomaly - Synthetic Financial Transaction Generator
Generates realistic multi-year personal banking & credit card transaction data
complete with merchant noise, recurring subscriptions, seasonal trends, and edge cases.
"""

import os
import random
import datetime
import numpy as np
import pandas as pd

# Set fixed seed for reproducibility
np.random.seed(42)
random.seed(42)

START_DATE = datetime.date(2024, 1, 1)
END_DATE = datetime.date(2026, 9, 30)

ACCOUNTS = [
    {"account_id": "ACC_CHK_01", "name": "Chase Total Checking", "type": "Checking"},
    {"account_id": "ACC_SAV_01", "name": "Ally High-Yield Savings", "type": "Savings"},
    {"account_id": "ACC_CC_01", "name": "Chase Sapphire Preferred", "type": "Credit Card"},
    {"account_id": "ACC_CC_02", "name": "Amex Blue Cash Everyday", "type": "Credit Card"},
]

MERCHANTS_TAXONOMY = {
    "Housing": {
        "Rent/Mortgage": [
            ("Avalon Bay Communities", ["AVALON BAY APTS E-PAY", "AVALON RESIDENTIAL ACH"], 2200, 2400, "Needs", "Checking"),
        ],
        "Utilities": [
            ("ConEdison", ["CONED ELECTRIC NY", "CON EDISON BILL PAY", "CONEDISON ONLINE"], 95, 180, "Needs", "Checking"),
            ("National Grid", ["NATL GRID GAS NY", "NATIONAL GRID ACH"], 45, 120, "Needs", "Checking"),
            ("Verizon Fios", ["VERIZON*FIOS INTERNET", "VERIZON BILLPAY 800-837-4966"], 79.99, 79.99, "Needs", "Credit Card"),
        ]
    },
    "Food & Dining": {
        "Groceries": [
            ("Trader Joe's", ["TRADER JOE'S #541 NYC", "TRADER JOES MANHATTAN", "TRADER JOE'S #102"], 45, 130, "Needs", "Credit Card"),
            ("Whole Foods", ["WHOLEFDS #10294 NY", "WHOLE FOODS MKT COLUMBUS", "WFM METRO"], 60, 195, "Needs", "Credit Card"),
            ("Target Grocery", ["TARGET T-0854 GROCERY", "TARGET CORP MINNEAPOLIS"], 25, 85, "Needs", "Credit Card"),
            ("Costco Wholesale", ["COSTCO WHSE #0312", "COSTCO WHOLESALE CLUB"], 120, 320, "Needs", "Credit Card"),
        ],
        "Restaurants": [
            ("Chipotle", ["CHIPOTLE 1842 NYC", "CHIPOTLE ONLINE ORD"], 14, 28, "Wants", "Credit Card"),
            ("Sweetgreen", ["SWEETGREEN 0042 NYC", "SWEETGREEN APP"], 16, 26, "Wants", "Credit Card"),
            ("Local Italian Trattoria", ["TRATTORIA DELL ARTE NY", "TRATTORIA PESCE"], 75, 185, "Wants", "Credit Card"),
            ("Sushi Katsu", ["SUSHI KATSU MIDTOWN", "KATSU SUSHI BAR"], 55, 140, "Wants", "Credit Card"),
        ],
        "Coffee Shops": [
            ("Starbucks", ["STARBUCKS STORE #14920 NY", "STARBUCKS COFFEE #0281", "STARBUCKS APP RELOAD"], 4.5, 9.5, "Wants", "Credit Card"),
            ("Blue Bottle Coffee", ["BLUE BOTTLE COFFEE NYC", "BLUE BOTTLE WEB"], 6.0, 14.0, "Wants", "Credit Card"),
        ],
        "Food Delivery": [
            ("DoorDash", ["DOORDASH*DASHPASS", "DOORDASH*CHIPOTLE REST", "DOORDASH*DELIVERY FEE"], 25, 65, "Wants", "Credit Card"),
            ("Uber Eats", ["UBER* EATS PENDING", "UBER *EATS HELP.UBER.COM"], 22, 58, "Wants", "Credit Card"),
        ]
    },
    "Transportation": {
        "Public Transit": [
            ("MTA Metro", ["MTA*OMNY NY PAYGO", "MTA METROCARD VENDING"], 2.90, 34.0, "Needs", "Credit Card"),
        ],
        "Rideshare": [
            ("Uber", ["UBER *TRIP HELP.UBER.COM CA", "UBER *TRIP 800-592-8996", "UBER TRIP PENDING"], 15, 62, "Wants", "Credit Card"),
            ("Lyft", ["LYFT *RIDE 855-865-9553", "LYFT RIDE WEDNESDAY"], 14, 48, "Wants", "Credit Card"),
        ],
        "Fuel": [
            ("Shell Oil", ["SHELL OIL 5754291840", "SHELL SERVICE STN"], 35, 75, "Needs", "Credit Card"),
            ("Mobil", ["EXXONMOBIL 4829104", "MOBIL GAS STN"], 38, 70, "Needs", "Credit Card"),
        ],
        "Auto Insurance": [
            ("Geico", ["GEICO DIRECT AUTO INS", "GEICO MONTHLY PREM"], 138.50, 138.50, "Needs", "Checking"),
        ]
    },
    "Entertainment & Subscriptions": {
        "Streaming": [
            ("Netflix", ["NETFLIX.COM 866-579-7172 CA", "NETFLIX MO SERVICE"], 15.49, 15.49, "Wants", "Credit Card"),
            ("Spotify", ["SPOTIFY USA NEW YORK NY", "SPOTIFY PREMIUM MO"], 10.99, 10.99, "Wants", "Credit Card"),
            ("HBO Max", ["HBO MAX / WARNERMEDIA", "MAX.COM DIGITAL SUB"], 15.99, 15.99, "Wants", "Credit Card"),
            ("Apple Services", ["APPLE.COM/BILL 866-712-7753 CA", "APPLE ICLOUD STORAGE"], 2.99, 12.99, "Wants", "Credit Card"),
            ("YouTube Premium", ["GOOGLE *YOUTUBE PREMIUM", "YOUTUBE MEMBER"], 13.99, 13.99, "Wants", "Credit Card"),
        ],
        "Fitness": [
            ("Equinox Gym", ["EQUINOX FITNESS CLUBS NYC", "EQUINOX MO DUES"], 185.00, 185.00, "Wants", "Credit Card"),
        ],
        "Recreation & Events": [
            ("AMC Theatres", ["AMC 1419 THEATRES NY", "AMC ONLINE TICKET"], 24, 55, "Wants", "Credit Card"),
            ("Ticketmaster", ["TICKETMASTER CONCERT NY", "TM *EVENT TICKETS"], 85, 260, "Wants", "Credit Card"),
            ("Steam Games", ["STEAM GAMES VALVE CORP", "STEAM PURCHASE WA"], 19.99, 69.99, "Wants", "Credit Card"),
        ]
    },
    "Shopping & Retail": {
        "Online Retail": [
            ("Amazon", ["AMZN MKTP US*8A91B0 SEATTLE WA", "AMAZON.COM*291AK9", "AMZN PRIME MEMBERSHIP", "AMAZON DIGITAL SVCS"], 12, 185, "Wants", "Credit Card"),
            ("Target", ["TARGET STORES T-1182", "TARGET.COM RET"], 28, 140, "Wants", "Credit Card"),
        ],
        "Clothing & Apparel": [
            ("Zara", ["ZARA USA NEW YORK", "ZARA RETAIL STORE"], 45, 180, "Wants", "Credit Card"),
            ("Uniqlo", ["UNIQLO 5TH AVE NY", "UNIQLO ONLINE USA"], 35, 125, "Wants", "Credit Card"),
            ("Nike", ["NIKE RETAIL SOHO NY", "NIKE.COM DIRECT"], 65, 210, "Wants", "Credit Card"),
        ],
        "Electronics": [
            ("Best Buy", ["BEST BUY #0492 NYC", "BESTBUY.COM 888-237-8289"], 45, 350, "Wants", "Credit Card"),
            ("Apple Store", ["APPLE STORE #R042 NYC", "APPLE ONLINE STORE"], 99, 1299, "Wants", "Credit Card"),
        ]
    },
    "Healthcare & Personal": {
        "Pharmacy": [
            ("CVS Pharmacy", ["CVS/PHARMACY #02941 NY", "CVS STORE PHARM"], 12, 65, "Needs", "Credit Card"),
            ("Walgreens", ["WALGREENS STORE #1084", "WALGREENS PHARMACY"], 14, 55, "Needs", "Credit Card"),
        ],
        "Medical": [
            ("CityMD Urgent Care", ["CITYMD MEDICAL NY", "CITYMD COPAY 212"], 40, 150, "Needs", "Credit Card"),
            ("Dental Associates", ["METRO DENTAL NYC", "DENTAL CLINIC COPAY"], 85, 280, "Needs", "Credit Card"),
        ],
        "Personal Care": [
            ("Salon / Barber", ["MANHATTAN BARBER SHOP", "SEPHORA #0412 BEAUTY"], 35, 95, "Wants", "Credit Card"),
        ]
    }
}

INCOME_SOURCES = [
    {
        "source": "TechNova Corp Salary",
        "raw_names": ["TECHNOVA CORP DIR DEP", "TECHNOVA CORP PAYROLL ACH"],
        "base_amount": 4650.00,
        "frequency": "biweekly", # 1st and 15th (or every 2 weeks)
        "account": "ACC_CHK_01"
    },
    {
        "source": "Freelance Analytics Consulting",
        "raw_names": ["STRIPE PAYOUT *CONSULT", "UPWORK ESCROW TRANSFER"],
        "base_amount": 750.00,
        "frequency": "occasional",
        "account": "ACC_CHK_01"
    },
    {
        "source": "Ally Savings Interest",
        "raw_names": ["ALLY BANK INTEREST PAYMENT", "ALLY HYSA MO INT"],
        "base_amount": 62.50,
        "frequency": "monthly_end",
        "account": "ACC_SAV_01"
    }
]

def generate_transactions():
    records = []
    current_date = START_DATE
    tx_counter = 10001

    while current_date <= END_DATE:
        day_of_month = current_date.day
        is_weekend = current_date.weekday() >= 5
        month = current_date.month

        # ----------------------------------------------------
        # 1. Income Generation
        # ----------------------------------------------------
        # Bi-weekly salary on 1st and 15th
        if day_of_month in [1, 15]:
            sal = INCOME_SOURCES[0]
            # Small merit bump in 2025 and 2026
            year_factor = 1.0 if current_date.year == 2024 else (1.05 if current_date.year == 2025 else 1.10)
            sal_amt = round(sal["base_amount"] * year_factor + random.uniform(-20, 20), 2)
            # Year-end bonus in December 15
            if month == 12 and day_of_month == 15:
                sal_amt += round(random.uniform(2500, 4000), 2)

            records.append({
                "transaction_id": f"TX_{tx_counter}",
                "date": current_date.isoformat(),
                "account_id": sal["account"],
                "raw_description": random.choice(sal["raw_names"]),
                "amount": sal_amt,
                "transaction_type": "Income",
                "category": "Income",
                "subcategory": "Salary & Wages",
                "clean_merchant": "TechNova Corp",
                "budget_bucket": "Income",
                "is_recurring": True,
                "payment_channel": "ACH Transfer",
                "city": "New York",
                "state": "NY"
            })
            tx_counter += 1

        # Interest at month end
        if (current_date + datetime.timedelta(days=1)).month != current_date.month:
            intr = INCOME_SOURCES[2]
            records.append({
                "transaction_id": f"TX_{tx_counter}",
                "date": current_date.isoformat(),
                "account_id": intr["account"],
                "raw_description": random.choice(intr["raw_names"]),
                "amount": round(intr["base_amount"] + random.uniform(5, 25), 2),
                "transaction_type": "Income",
                "category": "Income",
                "subcategory": "Investment & Interest",
                "clean_merchant": "Ally Bank",
                "budget_bucket": "Income",
                "is_recurring": True,
                "payment_channel": "Direct Deposit",
                "city": "Midvale",
                "state": "UT"
            })
            tx_counter += 1

        # Occasional freelance (about 1-2 times a month, ~3% chance per day)
        if random.random() < 0.04:
            free = INCOME_SOURCES[1]
            records.append({
                "transaction_id": f"TX_{tx_counter}",
                "date": current_date.isoformat(),
                "account_id": free["account"],
                "raw_description": random.choice(free["raw_names"]),
                "amount": round(random.uniform(450, 1400), 2),
                "transaction_type": "Income",
                "category": "Income",
                "subcategory": "Freelance / Side Gig",
                "clean_merchant": "Freelance Consulting",
                "budget_bucket": "Income",
                "is_recurring": False,
                "payment_channel": "Online Transfer",
                "city": "San Francisco",
                "state": "CA"
            })
            tx_counter += 1

        # ----------------------------------------------------
        # 2. Monthly Fixed Expenses (Rent, Utilities, Insurance)
        # ----------------------------------------------------
        if day_of_month == 1:
            # Rent
            m_name, raw_opts, min_p, max_p, bucket, acc_type = MERCHANTS_TAXONOMY["Housing"]["Rent/Mortgage"][0]
            records.append({
                "transaction_id": f"TX_{tx_counter}",
                "date": current_date.isoformat(),
                "account_id": "ACC_CHK_01",
                "raw_description": random.choice(raw_opts),
                "amount": round(random.uniform(min_p, max_p), 2),
                "transaction_type": "Expense",
                "category": "Housing",
                "subcategory": "Rent/Mortgage",
                "clean_merchant": m_name,
                "budget_bucket": bucket,
                "is_recurring": True,
                "payment_channel": "ACH / Electronic",
                "city": "New York",
                "state": "NY"
            })
            tx_counter += 1

        if day_of_month == 5:
            # Internet (Verizon)
            m_name, raw_opts, min_p, max_p, bucket, acc_type = MERCHANTS_TAXONOMY["Housing"]["Utilities"][2]
            records.append({
                "transaction_id": f"TX_{tx_counter}",
                "date": current_date.isoformat(),
                "account_id": "ACC_CC_01",
                "raw_description": random.choice(raw_opts),
                "amount": min_p,
                "transaction_type": "Expense",
                "category": "Housing",
                "subcategory": "Utilities",
                "clean_merchant": m_name,
                "budget_bucket": bucket,
                "is_recurring": True,
                "payment_channel": "Credit Card",
                "city": "New York",
                "state": "NY"
            })
            tx_counter += 1

        if day_of_month == 12:
            # Electric (ConEd)
            m_name, raw_opts, min_p, max_p, bucket, acc_type = MERCHANTS_TAXONOMY["Housing"]["Utilities"][0]
            # Higher in summer (AC) & winter (heating)
            seasonal_mult = 1.35 if month in [6, 7, 8, 12, 1, 2] else 1.0
            records.append({
                "transaction_id": f"TX_{tx_counter}",
                "date": current_date.isoformat(),
                "account_id": "ACC_CHK_01",
                "raw_description": random.choice(raw_opts),
                "amount": round(random.uniform(min_p, max_p) * seasonal_mult, 2),
                "transaction_type": "Expense",
                "category": "Housing",
                "subcategory": "Utilities",
                "clean_merchant": m_name,
                "budget_bucket": bucket,
                "is_recurring": True,
                "payment_channel": "ACH / Electronic",
                "city": "New York",
                "state": "NY"
            })
            tx_counter += 1

        if day_of_month == 18:
            # Auto Insurance (Geico)
            m_name, raw_opts, min_p, max_p, bucket, acc_type = MERCHANTS_TAXONOMY["Transportation"]["Auto Insurance"][0]
            records.append({
                "transaction_id": f"TX_{tx_counter}",
                "date": current_date.isoformat(),
                "account_id": "ACC_CHK_01",
                "raw_description": random.choice(raw_opts),
                "amount": min_p,
                "transaction_type": "Expense",
                "category": "Transportation",
                "subcategory": "Auto Insurance",
                "clean_merchant": m_name,
                "budget_bucket": bucket,
                "is_recurring": True,
                "payment_channel": "ACH / Electronic",
                "city": "Chevy Chase",
                "state": "MD"
            })
            tx_counter += 1

        # ----------------------------------------------------
        # 3. Monthly Recurring Subscriptions
        # ----------------------------------------------------
        # Gym on 1st
        if day_of_month == 1:
            gym = MERCHANTS_TAXONOMY["Entertainment & Subscriptions"]["Fitness"][0]
            records.append({
                "transaction_id": f"TX_{tx_counter}",
                "date": current_date.isoformat(),
                "account_id": "ACC_CC_01",
                "raw_description": random.choice(gym[1]),
                "amount": gym[2],
                "transaction_type": "Expense",
                "category": "Entertainment & Subscriptions",
                "subcategory": "Fitness",
                "clean_merchant": gym[0],
                "budget_bucket": gym[4],
                "is_recurring": True,
                "payment_channel": "Recurring Card",
                "city": "New York",
                "state": "NY"
            })
            tx_counter += 1

        # Streaming on specific days
        stream_days = {
            7: MERCHANTS_TAXONOMY["Entertainment & Subscriptions"]["Streaming"][0], # Netflix
            10: MERCHANTS_TAXONOMY["Entertainment & Subscriptions"]["Streaming"][1], # Spotify
            14: MERCHANTS_TAXONOMY["Entertainment & Subscriptions"]["Streaming"][2], # HBO Max
            20: MERCHANTS_TAXONOMY["Entertainment & Subscriptions"]["Streaming"][3], # Apple
            24: MERCHANTS_TAXONOMY["Entertainment & Subscriptions"]["Streaming"][4], # YouTube
        }
        if day_of_month in stream_days:
            st = stream_days[day_of_month]
            records.append({
                "transaction_id": f"TX_{tx_counter}",
                "date": current_date.isoformat(),
                "account_id": "ACC_CC_01" if random.random() > 0.3 else "ACC_CC_02",
                "raw_description": random.choice(st[1]),
                "amount": st[2],
                "transaction_type": "Expense",
                "category": "Entertainment & Subscriptions",
                "subcategory": "Streaming",
                "clean_merchant": st[0],
                "budget_bucket": st[4],
                "is_recurring": True,
                "payment_channel": "Recurring Card",
                "city": "San Jose" if "NETFLIX" in st[1][0] else "New York",
                "state": "CA" if "NETFLIX" in st[1][0] else "NY"
            })
            tx_counter += 1

        # ----------------------------------------------------
        # 4. Daily Variable Spending (Groceries, Dining, Coffee, Rides, Shopping)
        # ----------------------------------------------------
        # Higher volume on weekends
        num_daily_tx = random.randint(2, 6) if is_weekend else random.randint(1, 4)

        # November/December holiday shopping boost
        if month in [11, 12]:
            num_daily_tx += random.randint(1, 3)

        for _ in range(num_daily_tx):
            # Select category group based on realistic probabilities
            cat_weights = {
                "Food & Dining": 0.45,
                "Transportation": 0.18,
                "Shopping & Retail": 0.22,
                "Entertainment & Subscriptions": 0.08,
                "Healthcare & Personal": 0.07
            }
            cat_choice = random.choices(list(cat_weights.keys()), weights=list(cat_weights.values()))[0]
            subcat_choices = list(MERCHANTS_TAXONOMY[cat_choice].keys())
            # Exclude fixed utilities/mortgage/fitness from random pool
            valid_subcats = [s for s in subcat_choices if s not in ["Rent/Mortgage", "Utilities", "Auto Insurance", "Fitness", "Streaming"]]
            if not valid_subcats:
                continue
            subcat_choice = random.choice(valid_subcats)
            merchant_list = MERCHANTS_TAXONOMY[cat_choice][subcat_choice]
            merchant_info = random.choice(merchant_list)

            m_name, raw_opts, min_p, max_p, bucket, pref_acc = merchant_info
            
            # Weekend restaurant/delivery multiplier
            amt_multiplier = 1.25 if (is_weekend and subcat_choice in ["Restaurants", "Food Delivery", "Shopping"]) else 1.0
            
            # Holiday shopping multiplier
            if month in [11, 12] and cat_choice == "Shopping & Retail":
                amt_multiplier *= 1.30

            amt = round(random.uniform(min_p, max_p) * amt_multiplier, 2)
            
            # Determine payment card
            acc_id = "ACC_CC_01" if random.random() < 0.65 else "ACC_CC_02"
            
            # Channel
            channel = "In-Store POS" if subcat_choice in ["Groceries", "Coffee Shops", "Pharmacy"] else "E-Commerce / Online"

            records.append({
                "transaction_id": f"TX_{tx_counter}",
                "date": current_date.isoformat(),
                "account_id": acc_id,
                "raw_description": random.choice(raw_opts),
                "amount": amt,
                "transaction_type": "Expense",
                "category": cat_choice,
                "subcategory": subcat_choice,
                "clean_merchant": m_name,
                "budget_bucket": bucket,
                "is_recurring": False,
                "payment_channel": channel,
                "city": "New York",
                "state": "NY"
            })
            tx_counter += 1

        # ----------------------------------------------------
        # 5. Realistic Outliers / Rare Financial Events
        # ----------------------------------------------------
        # Rare car maintenance, flight/vacation, medical surprise
        if random.random() < 0.015:
            rare_events = [
                ("Auto Maintenance & Tires", "Transportation", "Car Repair", "Needs", "MIDAS AUTO SERVICE NYC", 450, 1150),
                ("Delta Air Lines Flight", "Travel & Vacation", "Flights", "Wants", "DELTA AIR 006249182374", 320, 890),
                ("Marriott Hotel Stay", "Travel & Vacation", "Hotels", "Wants", "MARRIOTT DOWNTOWN CHI", 410, 920),
                ("Apple MacBook Pro", "Shopping & Retail", "Electronics", "Wants", "APPLE STORE #R042 NYC", 1699, 2399),
                ("Emergency Dental Crown", "Healthcare & Personal", "Dental", "Needs", "SPECIALTY DENTAL SURG", 650, 1300),
            ]
            event = random.choice(rare_events)
            records.append({
                "transaction_id": f"TX_{tx_counter}",
                "date": current_date.isoformat(),
                "account_id": "ACC_CC_01",
                "raw_description": event[4],
                "amount": round(random.uniform(event[5], event[6]), 2),
                "transaction_type": "Expense",
                "category": event[1],
                "subcategory": event[2],
                "clean_merchant": event[0],
                "budget_bucket": event[3],
                "is_recurring": False,
                "payment_channel": "Credit Card",
                "city": "New York",
                "state": "NY"
            })
            tx_counter += 1

        # ----------------------------------------------------
        # 6. Monthly Savings Transfer (Pay yourself first)
        # ----------------------------------------------------
        if day_of_month == 2:
            records.append({
                "transaction_id": f"TX_{tx_counter}",
                "date": current_date.isoformat(),
                "account_id": "ACC_CHK_01",
                "raw_description": "TRANSFER TO ALLY HYSA - SAVINGS ALLOC",
                "amount": round(random.uniform(900, 1400), 2),
                "transaction_type": "Transfer",
                "category": "Savings & Investments",
                "subcategory": "High-Yield Savings",
                "clean_merchant": "Ally HYSA Transfer",
                "budget_bucket": "Savings",
                "is_recurring": True,
                "payment_channel": "Internal Transfer",
                "city": "New York",
                "state": "NY"
            })
            tx_counter += 1

        current_date += datetime.timedelta(days=1)

    df = pd.DataFrame(records)
    return df

def generate_accounts_and_budgets():
    accounts_df = pd.DataFrame(ACCOUNTS)
    
    # Target monthly budget per category for benchmark comparisons
    budget_data = [
        {"category": "Housing", "budget_bucket": "Needs", "monthly_budget_target": 2600.00},
        {"category": "Food & Dining", "budget_bucket": "Needs/Wants", "monthly_budget_target": 950.00},
        {"category": "Transportation", "budget_bucket": "Needs", "monthly_budget_target": 350.00},
        {"category": "Shopping & Retail", "budget_bucket": "Wants", "monthly_budget_target": 450.00},
        {"category": "Entertainment & Subscriptions", "budget_bucket": "Wants", "monthly_budget_target": 350.00},
        {"category": "Healthcare & Personal", "budget_bucket": "Needs", "monthly_budget_target": 250.00},
        {"category": "Travel & Vacation", "budget_bucket": "Wants", "monthly_budget_target": 300.00},
        {"category": "Savings & Investments", "budget_bucket": "Savings", "monthly_budget_target": 1200.00},
    ]
    budgets_df = pd.DataFrame(budget_data)
    return accounts_df, budgets_df

if __name__ == "__main__":
    print("[*] Generating Finomaly transactional data...")
    df_tx = generate_transactions()
    accounts_df, budgets_df = generate_accounts_and_budgets()

    raw_dir = os.path.join(os.path.dirname(__file__), "..", "data", "raw")
    os.makedirs(raw_dir, exist_ok=True)

    # Inject realistic 'raw' dirty features for the raw dataset:
    # 1. Messy date formats in a subset of rows
    # 2. Occasional missing merchant or city
    # 3. Trailing spaces / casing issues
    raw_df = df_tx.copy()
    
    # Introduce ~1.5% missing cities to simulate real messy transaction feeds
    mask_city = np.random.rand(len(raw_df)) < 0.015
    raw_df.loc[mask_city, "city"] = np.nan

    # Introduce some casing variation in raw_description
    raw_df["raw_description"] = raw_df["raw_description"].apply(
        lambda s: s.lower() if random.random() < 0.2 else (s.upper() if random.random() < 0.3 else s)
    )

    # Save raw datasets
    raw_tx_path = os.path.join(raw_dir, "raw_transactions.csv")
    accounts_path = os.path.join(raw_dir, "accounts.csv")
    budgets_path = os.path.join(raw_dir, "monthly_budgets.csv")

    raw_df.to_csv(raw_tx_path, index=False)
    accounts_df.to_csv(accounts_path, index=False)
    budgets_df.to_csv(budgets_path, index=False)

    print(f"[+] Successfully generated {len(df_tx):,} transactions spanning {START_DATE} to {END_DATE}!")
    print(f"[+] Total Spend: ${df_tx[df_tx['transaction_type'] == 'Expense']['amount'].sum():,.2f}")
    print(f"[+] Total Income: ${df_tx[df_tx['transaction_type'] == 'Income']['amount'].sum():,.2f}")
    print(f"[+] Raw files saved to '{raw_dir}'")
