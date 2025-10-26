import sqlite3
import datetime # Pastikan ini ada

DB_NAME = "finance.db"

def get_db_connection():
    """Membuat koneksi ke database SQLite."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row  # Ini memungkinkan kita mengambil data seperti dictionary
    return conn

def create_tables():
    """Membuat tabel jika belum ada."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS budgets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT NOT NULL UNIQUE,
        amount REAL NOT NULL
    );
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        description TEXT,
        amount REAL NOT NULL,
        type TEXT NOT NULL CHECK(type IN ('Pemasukan', 'Pengeluaran')),
        category TEXT NOT NULL
    );
    """)
    
    conn.commit()
    conn.close()
    print("Tabel (kembali) dicek/dibuat.")

# --- Fungsi untuk Anggaran (Budgets) ---

def add_budget(category, amount):
    """Menambah atau memperbarui anggaran (case-insensitive)."""
    # FIX: Normalisasi kategori ke Title Case dan hapus spasi
    category = category.strip().title()
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO budgets (category, amount) VALUES (?, ?)", (category, amount))
    conn.commit()
    conn.close()

def get_all_budgets():
    """Mengambil semua data anggaran."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT category, amount FROM budgets ORDER BY category")
    budgets = cursor.fetchall()
    conn.close()
    return budgets

def get_budget_categories():
    """Hanya mengambil nama-nama kategori anggaran (untuk dropdown)."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT category FROM budgets ORDER BY category")
    categories = [row['category'] for row in cursor.fetchall()]
    conn.close()
    return categories

def delete_budget_by_category(category):
    """Menghapus kategori anggaran berdasarkan namanya."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM budgets WHERE category = ?", (category,))
    conn.commit()
    conn.close()
    
def get_all_transactions():
    """Mengambil SEMUA transaksi (termasuk ID) untuk tab riwayat."""
    conn = get_db_connection()
    cursor = conn.cursor()
    # Kita ambil ID untuk tombol hapus
    cursor.execute("SELECT id, date, description, amount, type, category FROM transactions ORDER BY date DESC")
    transactions = cursor.fetchall() # Mengambil semua baris
    conn.close()
    return transactions

def delete_transaction_by_id(transaction_id):
    """Menghapus satu transaksi berdasarkan ID-nya."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM transactions WHERE id = ?", (transaction_id,))
    conn.commit()
    conn.close()
# --- Fungsi untuk Transaksi (Transactions) ---

def add_transaction(date, description, amount, type, category):
    """Menambah satu transaksi baru (case-insensitive)."""
    # FIX: Normalisasi kategori dan tipe
    category = category.strip().title()
    type = type.strip().title() # "pengeluaran" -> "Pengeluaran"
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO transactions (date, description, amount, type, category) VALUES (?, ?, ?, ?, ?)",
        (date, description, amount, type, category)
    )
    conn.commit()
    conn.close()

# --- Fungsi untuk Dasbor ---

def get_transactions_for_month(year_month):
    """
    Mengambil semua transaksi untuk bulan tertentu.
    Format year_month adalah 'YYYY-MM'.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT date, description, amount, type, category FROM transactions WHERE strftime('%Y-%m', date) = ?",
        (year_month,)
    )
    transactions = cursor.fetchall()
    conn.close()
    return transactions

def update_transaction(trx_id, date, description, amount, type, category):
    """Memperbarui transaksi yang ada berdasarkan ID-nya."""
    # Normalisasi data untuk konsistensi
    category = category.strip().title()
    type = type.strip().title()
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE transactions 
        SET date = ?, description = ?, amount = ?, type = ?, category = ?
        WHERE id = ?
        """,
        (date, description, amount, type, category, trx_id)
    )
    conn.commit()
    conn.close()

