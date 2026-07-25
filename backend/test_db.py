# test_db.py - نسخه بسیار ساده و تست‌شده
import sqlite3
import os

print("=" * 50)
print("🧪 تست دیتابیس - نسخه ساده")
print("=" * 50)

# تعیین مسیر دیتابیس
db_folder = r"C:\Users\project.control\Desktop\gold-analyzer-web\backend\database"
db_file = os.path.join(db_folder, "market.db")

print(f"📂 پوشه دیتابیس: {db_folder}")
print(f"📄 فایل دیتابیس: {db_file}")

# ایجاد پوشه اگر وجود ندارد
if not os.path.exists(db_folder):
    os.makedirs(db_folder)
    print("✅ پوشه دیتابیس ایجاد شد!")

# تست اتصال
try:
    # اتصال به SQLite
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    print("✅ اتصال به دیتابیس برقرار شد!")
    
    # تست 1: ایجاد جدول
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS test_table (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            value REAL
        )
    """)
    conn.commit()
    print("✅ جدول تست ایجاد شد!")
    
    # تست 2: درج داده
    cursor.execute("INSERT INTO test_table (name, value) VALUES (?, ?)", ("test", 100))
    conn.commit()
    print("✅ داده تست درج شد!")
    
    # تست 3: خواندن داده
    cursor.execute("SELECT * FROM test_table")
    rows = cursor.fetchall()
    print(f"✅ تعداد رکوردها: {len(rows)}")
    
    # نمایش رکوردها
    for row in rows:
        print(f"   📋 {row}")
    
    # تست 4: حذف داده تست
    cursor.execute("DELETE FROM test_table WHERE name='test'")
    conn.commit()
    print("✅ داده تست پاک شد!")
    
    # بستن اتصال
    conn.close()
    print("✅ اتصال بسته شد!")
    
    print("\n" + "=" * 50)
    print("✅ **همه تست‌ها با موفقیت انجام شد!**")
    print("=" * 50)
    
except sqlite3.Error as e:
    print(f"❌ خطای SQLite: {e}")
    
except Exception as e:
    print(f"❌ خطای دیگر: {e}")
    
finally:
    if 'conn' in locals():
        conn.close()

print("\nبرای خروج Enter بزنید...")
input()