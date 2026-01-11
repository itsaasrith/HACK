import sqlite3

def init_shop_db():
    conn = sqlite3.connect("dammed.db")
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS shop_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        seller TEXT,
        item_name TEXT,
        description TEXT,
        price REAL,
        image_path TEXT
    )
    """)

    conn.commit()
    conn.close()


def add_item(seller, item_name, description, price, image_path):
    conn = sqlite3.connect("dammed.db")
    c = conn.cursor()

    c.execute("""
    INSERT INTO shop_items (seller, item_name, description, price, image_path)
    VALUES (?, ?, ?, ?, ?)
    """, (seller, item_name, description, price, image_path))

    conn.commit()
    conn.close()


def get_all_items():
    conn = sqlite3.connect("dammed.db")
    c = conn.cursor()

    c.execute("SELECT * FROM shop_items")
    items = c.fetchall()

    conn.close()
    return items
