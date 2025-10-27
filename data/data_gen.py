# Generate sample hitlog data per Telegraph exercise specs
"""Data generator for synthetic hitlog CSV files used in tests and demos.

This module creates a deterministic (seeded) set of user journeys over a
catalog of articles and writes a CSV file to `data/logs/`.
"""

import pandas as pd
import random
from datetime import datetime, timedelta

random.seed(42)

N_USERS = 20
N_ARTICLES = 50


# ----- Helper functions -----
def slugify(title: str) -> str:
    """Create a URL-friendly slug from an article title.

    Keeps alphanumerics and spaces, replaces other characters with '-'
    and collapses whitespace to single dashes. Result is truncated to 80
    characters and trimmed of leading/trailing dashes.
    """
    base = title.lower()
    base = "".join(ch if ch.isalnum() or ch == " " else "-" for ch in base)
    base = "-".join(base.split())
    # ensure max length
    return base[:80].strip("-")


def ts(base_date: datetime, min_sec=0, max_sec=60 * 60 * 16):
    """Return a timestamp offset from base_date by random seconds within [min_sec, max_sec]."""
    return base_date + timedelta(seconds=random.randint(min_sec, max_sec))


# ----- Build article catalog -----
categories = [
    "Politics",
    "World",
    "Business",
    "Tech",
    "Sport",
    "Culture",
    "Lifestyle",
    "Science",
    "Health",
    "Travel",
]

# A pool of headline stems to make names look realistic
stems = [
    "Budget 2025: What it means for households",
    "Prime Minister faces questions over policy shift",
    "Markets rally as inflation cools",
    "New smartphone chips promise longer battery life",
    "Championship title race down to the wire",
    "Critics hail revival of classic play",
    "Five habits linked to longer life",
    "Breakthrough in clean energy storage",
    "How to sleep better in darker months",
    "Hidden gems for autumn city breaks",
    "Mortgage rates fall for third month",
    "AI start-ups race to raise funding",
    "Captain inspires dramatic comeback win",
    "Art exhibition draws record crowds",
    "Scientists map deep-sea coral reefs",
    "Flu season: What doctors want you to know",
    "The rise of slow travel",
    "Investor guide to dividend stocks",
    "Cyberattack disrupts major retailer",
    "The etiquette of hybrid working",
    "UK house prices show signs of stabilising",
    "Space agency unveils lunar plans",
    "Star striker completes big-money move",
    "Streaming service announces new series",
    "Protein-rich lunches you can make fast",
    "University rankings shake-up explained",
    "Electric cars: charging myths debunked",
    "Europe braces for winter storms",
    "The ultimate guide to marathon tapering",
    "Remembering a legendary conductor",
    "Gadget gifts under £100",
    "What next for interest rates?",
    "Inside a pioneering vertical farm",
    "Why everyone is talking about magnesium",
    "Top museums to visit this weekend",
    "Rugby World Cup tactical trends",
    "How to negotiate your salary",
    "Major airline plans new transatlantic route",
    "Recipe: One-pan roast chicken",
    "Volcano eruption prompts evacuations",
    "Start-up founders on surviving downturns",
    "Workouts that actually fit into lunch",
    "Gardeners’ tips for late blooms",
    "What the new data rules mean for you",
    "How to back up your photos",
    "The psychology of procrastination",
    "Winners and losers from the tax changes",
    "The best hikes near London",
    "Inside the race to build fusion",
    "The future of home working",
]

# Ensure we have at least N_ARTICLES stems
while len(stems) < N_ARTICLES:
    stems.append(f"Feature no. {len(stems) + 1}")

articles = []
for i in range(N_ARTICLES):
    cat = random.choice(categories)
    title = stems[i]
    page_name = f"{cat} | {title}"
    url = f"/articles/{slugify(title)}"
    articles.append({"article_id": i + 1, "page_name": page_name, "page_url": url})

# Map and quick access
article_catalog = {a["article_id"]: a for a in articles}
article_list = list(article_catalog.values())

# ----- Generate user journeys -----
rows = []
start_date = datetime(2025, 10, 26, 6, 0, 0)  # a single daily file starting 06:00

user_ids = [f"u{str(i + 1).zfill(3)}" for i in range(N_USERS)]

for uid in user_ids:
    # Each user has 1-3 sessions in the day
    n_sessions = random.choices([1, 2, 3], weights=[0.55, 0.35, 0.10])[0]
    session_starts = sorted(
        [start_date + timedelta(hours=random.randint(0, 12)) for _ in range(n_sessions)]
    )

    # Decide if this user will register at most once across the day
    will_register = random.random() < 0.75  # ~75% of users ultimately register
    registration_done = False

    # Edge case knob: force some specific edge scenarios for a few users
    # Pick some users to create special patterns
    force_consecutive_dup = uid in {"u002", "u009"}
    force_nonconsecutive_dup = uid in {"u004", "u016"}
    force_direct_register = uid in {"u007"}  # visits /register first
    force_no_register = uid in {"u013"}  # never registers regardless of will_register

    if force_no_register:
        will_register = False

    for s_idx, session_start in enumerate(session_starts):
        # Decide number of article views in this session
        n_views = random.choices(
            list(range(1, 11)), weights=[6, 8, 10, 10, 10, 10, 10, 8, 6, 4]
        )[0]

        # Build a sequence of article indices for this session
        seq = []
        # Randomly choose a few "interests" for this user to bias article choice
        interests = random.sample(categories, k=random.randint(1, 3))
        # Candidate pool biased to interests
        interest_pool = [
            a
            for a in article_list
            if any(a["page_name"].startswith(cat) for cat in interests)
        ]
        general_pool = article_list

        # Generate base sequence
        for i in range(n_views):
            pool = (
                interest_pool
                if random.random() < 0.7 and interest_pool
                else general_pool
            )
            art = random.choice(pool)
            seq.append(art)

        # Inject edge cases
        if force_consecutive_dup and len(seq) >= 2:
            # Make two consecutive reads of the same article
            seq[1] = seq[0]
        if force_nonconsecutive_dup and len(seq) >= 4:
            seq[3] = seq[0]  # revisit the first article later
        if uid == "u012" and len(seq) >= 10:
            # Very long trail for stress testing
            seq += random.choices(article_list, k=5)

        # Timestamps strictly increasing within a session, but allow a tie for u005
        time_cursor = session_start
        for i, art in enumerate(seq):
            if uid == "u005" and i in (2, 3):
                # same-second hits to test tie-breaking
                ts_here = time_cursor
            else:
                ts_here = time_cursor + timedelta(seconds=random.randint(15, 240))
                time_cursor = ts_here

            rows.append(
                {
                    "page_name": art["page_name"],
                    "page_url": art["page_url"],
                    "user_id": uid,
                    "timestamp": ts_here.strftime("%Y-%m-%d %H:%M:%S"),
                }
            )

        # Decide on registration event placement
        # - If force_direct_register and it's the first session & not registered yet: register first
        # - Otherwise, 30-60% chance to register at end of session if not done
        if not registration_done and will_register:
            do_register = False
            if force_direct_register and s_idx == 0:
                do_register = True
            else:
                do_register = (
                    random.random() < 0.55
                )  # chance to complete registration in this session

            if do_register:
                # Registration may occur immediately (edge) or after the articles
                reg_time = (
                    session_start
                    if force_direct_register
                    else time_cursor + timedelta(seconds=random.randint(10, 300))
                )
                rows.append(
                    {
                        "page_name": "Register",
                        "page_url": "/register",
                        "user_id": uid,
                        "timestamp": reg_time.strftime("%Y-%m-%d %H:%M:%S"),
                    }
                )
                registration_done = True

        # Optional: post-registration browsing to test "reads after registering"
        if registration_done and random.random() < 0.35:
            # A couple of reads after registration
            for _ in range(random.randint(1, 3)):
                art = random.choice(article_list)
                time_cursor = time_cursor + timedelta(seconds=random.randint(20, 180))
                rows.append(
                    {
                        "page_name": art["page_name"],
                        "page_url": art["page_url"],
                        "user_id": uid,
                        "timestamp": time_cursor.strftime("%Y-%m-%d %H:%M:%S"),
                    }
                )

# Assemble dataframe
df = pd.DataFrame(rows, columns=["page_name", "page_url", "user_id", "timestamp"])

# Sort rows by user_id then timestamp to mimic log order
df["timestamp_dt"] = pd.to_datetime(df["timestamp"])
df.sort_values(by=["user_id", "timestamp_dt"], inplace=True)
df.drop(columns=["timestamp_dt"], inplace=True)

# Save CSV
date_str = datetime.now().strftime("%Y-%m-%d")
output_path = f"data/logs/hitlog_{date_str}.csv"
df.to_csv(output_path, index=False)
