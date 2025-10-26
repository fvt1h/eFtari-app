import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import datetime
import calendar

# --- Inisialisasi Firebase ---

# Path ke file service account lokal Anda (yang ada di folder .streamlit)
LOCAL_SERVICE_ACCOUNT_PATH = ".streamlit/eftari-app-firebase.json" 
# (Sesuaikan nama file ini jika Anda menamainya berbeda)

def init_firestore():
    """
    Menginisialisasi koneksi ke Firebase Firestore.
    Cek koneksi yang ada dulu. Jika tidak ada, buat koneksi baru.
    Coba pakai kredensial lokal dulu, jika gagal, pakai st.secrets (untuk deploy).
    """
    if not firebase_admin._apps:
        try:
            # 1. Coba koneksi lokal (untuk laptop Anda)
            cred = credentials.Certificate(LOCAL_SERVICE_ACCOUNT_PATH)
        except Exception as e:
            # 2. Jika gagal (di server Streamlit), pakai secrets
            print(f"Koneksi lokal gagal: {e}. Mencoba st.secrets...")
            # Ambil dari st.secrets (formatnya sudah kita siapkan)
            cred_dict = st.secrets["firebase_credentials"]["key"]
            cred = credentials.Certificate(cred_dict)
            
        firebase_admin.initialize_app(cred)
        print("Firebase App terinisialisasi.")
    
    return firestore.client()

# Panggil fungsi inisialisasi dan simpan koneksi DB
db = init_firestore()


# --- Fungsi untuk Anggaran (Budgets) ---
# Di Firestore, kita akan gunakan Kategori sebagai ID Dokumen agar unik

def add_budget(category, amount):
    """Menambah atau memperbarui anggaran (case-insensitive)."""
    category = category.strip().title()
    doc_ref = db.collection('budgets').document(category) # ID Dokumen = Nama Kategori
    doc_ref.set({'amount': amount}) # .set() akan create atau update

def get_all_budgets():
    """Mengambil semua data anggaran."""
    budgets_ref = db.collection('budgets').order_by('amount', direction='DESCENDING').stream()
    budgets = []
    for doc in budgets_ref:
        data = doc.to_dict()
        budgets.append({
            'category': doc.id, # Ambil ID dokumen sebagai kategori
            'amount': data['amount']
        })
    return budgets

def get_budget_categories():
    """Hanya mengambil nama-nama kategori anggaran (untuk dropdown)."""
    budgets_ref = db.collection('budgets').stream()
    # Ambil ID dokumen (yang merupakan nama kategori)
    categories = [doc.id for doc in budgets_ref]
    categories.sort()
    return categories

def delete_budget_by_category(category):
    """Menghapus kategori anggaran berdasarkan namanya (ID Dokumen)."""
    category = category.strip().title()
    db.collection('budgets').document(category).delete()


# --- Fungsi untuk Transaksi (Transactions) ---

def add_transaction(date, description, amount, type, category):
    """Menambah satu transaksi baru (case-insensitive)."""
    category = category.strip().title()
    type = type.strip().title()
    
    # Buat dictionary data
    data = {
        'date': str(date), # Pastikan formatnya string YYYY-MM-DD
        'description': description,
        'amount': float(amount), # Pastikan formatnya angka
        'type': type,
        'category': category
    }
    # .add() akan membuat dokumen baru dengan ID unik otomatis
    db.collection('transactions').add(data)

def update_transaction(trx_id, date, description, amount, type, category):
    """Memperbarui transaksi yang ada berdasarkan ID-nya."""
    category = category.strip().title()
    type = type.strip().title()
    
    doc_ref = db.collection('transactions').document(trx_id)
    doc_ref.update({
        'date': str(date),
        'description': description,
        'amount': float(amount),
        'type': type,
        'category': category
    })

def delete_transaction_by_id(transaction_id):
    """Menghapus satu transaksi berdasarkan ID-nya."""
    db.collection('transactions').document(transaction_id).delete()

def get_all_transactions():
    """Mengambil SEMUA transaksi (termasuk ID) untuk tab riwayat."""
    trx_ref = db.collection('transactions').order_by('date', direction='DESCENDING').stream()
    transactions = []
    for doc in trx_ref:
        data = doc.to_dict()
        data['id'] = doc.id # Tambahkan ID Dokumen ke dictionary
        transactions.append(data)
    return transactions

def get_transactions_for_month(year_month):
    """
    Mengambil semua transaksi untuk bulan tertentu.
    Format year_month adalah 'YYYY-MM'.
    """
    # Ubah 'YYYY-MM' menjadi tanggal awal dan akhir
    try:
        year, month = map(int, year_month.split('-'))
        # Cari hari terakhir di bulan itu
        last_day = calendar.monthrange(year, month)[1]
        
        start_date = f"{year_month}-01"
        end_date = f"{year_month}-{last_day:02d}" # :02d untuk format '01', '09'
        
    except Exception as e:
        print(f"Error parsing tanggal: {e}")
        return []

    # Buat kueri rentang tanggal
    trx_ref = db.collection('transactions') \
                .where('date', '>=', start_date) \
                .where('date', '<=', end_date) \
                .stream()
                
    transactions = []
    for doc in trx_ref:
        data = doc.to_dict()
        data['id'] = doc.id
        transactions.append(data)
    return transactions
