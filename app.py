import streamlit as st
import database as db  # Fungsi database kita (yang sekarang sudah pakai Firebase)
import datetime
import pandas as pd
import plotly.express as px  # Library untuk grafik interaktif

# --- Konfigurasi Halaman ---
st.set_page_config(
    page_title="e-Ftari | Dasbor",
    page_icon="💰",
    layout="wide"
)

# --- Inisialisasi Database ---
# BARIS "db.create_tables()" SUDAH DIHAPUS DARI SINI.
# Database Firebase akan otomatis diinisialisasi saat 'database.py' diimpor.

# --- Judul ---
st.title("💰 Dasbor Keuangan e-Ftari")

# --- Filter Bulan ---
st.header("Pilih Bulan untuk Analisis")
today = datetime.date.today()
selected_month = st.date_input(
    "Pilih Bulan",
    today,
    format="YYYY-MM-DD", # Format tampilan
    key="month_selector"
)
current_month_str = selected_month.strftime('%Y-%m')
st.header(f"Gambaran Keuangan Bulan: {current_month_str}")

# --- Ambil Data dari Database ---
# Fungsi-fungsi ini namanya tetap sama, tapi sekarang mengambil data dari Firebase
transactions_data = db.get_transactions_for_month(current_month_str)
budgets_data = db.get_all_budgets()

# Jika tidak ada data, tampilkan pesan
if not transactions_data:
    st.info(f"Belum ada data transaksi untuk bulan {current_month_str}.")
    # Kita tidak 'stop' di sini agar anggaran tetap bisa ditampilkan
else:
    # --- Proses Data dengan Pandas ---
    df_transactions = pd.DataFrame(transactions_data)
    df_transactions['amount'] = pd.to_numeric(df_transactions['amount'])

    # --- 1. Ringkasan Metrik (Pemasukan, Pengeluaran, Sisa) ---
    total_pemasukan = df_transactions[df_transactions['type'] == 'Pemasukan']['amount'].sum()
    total_pengeluaran = df_transactions[df_transactions['type'] == 'Pengeluaran']['amount'].sum()
    sisa_netto = total_pemasukan - total_pengeluaran

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Pemasukan", f"Rp {total_pemasukan:,.0f}")
    col2.metric("Total Pengeluaran", f"Rp {total_pengeluaran:,.0f}")
    col3.metric("Sisa (Netto)", f"Rp {sisa_netto:,.0f}")
    
    st.markdown("---") # Garis pemisah
    
    # --- 3. Grafik Pie Chart Pengeluaran ---
    st.header("Pengeluaran Berdasarkan Kategori")
    
    df_pengeluaran_chart = df_transactions[df_transactions['type'] == 'Pengeluaran']
    
    if total_pengeluaran > 0 and not df_pengeluaran_chart.empty:
        # Hitung total pengeluaran per kategori untuk pie chart
        spending_by_category_chart = df_pengeluaran_chart.groupby('category')['amount'].sum().reset_index()

        fig = px.pie(
            spending_by_category_chart,
            values='amount',
            names='category',
            title='Proporsi Pengeluaran per Kategori'
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Belum ada data pengeluaran untuk digambarkan di grafik.")

# --- 2. Status Anggaran vs. Aktual (Selalu tampilkan) ---
st.markdown("---") # Garis pemisah
st.header("Status Anggaran vs. Aktual")

if not budgets_data:
    st.warning("Anda belum mengatur anggaran apapun. Silakan atur di tab 'Manajemen Anggaran'.")
else:
    df_budgets = pd.DataFrame(budgets_data)
    df_budgets['amount'] = pd.to_numeric(df_budgets['amount'])
    
    # Siapkan df pengeluaran jika ada, jika tidak, buat yang kosong
    if not transactions_data or df_transactions[df_transactions['type'] == 'Pengeluaran'].empty:
        df_summary = df_budgets
        df_summary['actual_spending'] = 0.0 # Tidak ada pengeluaran
    else:
        df_pengeluaran = df_transactions[df_transactions['type'] == 'Pengeluaran']
        spending_by_category = df_pengeluaran.groupby('category')['amount'].sum().reset_index()
        spending_by_category = spending_by_category.rename(columns={'amount': 'actual_spending'})
        
        # Gabungkan data anggaran dengan data pengeluaran
        df_summary = pd.merge(df_budgets, spending_by_category, on='category', how='left')
        df_summary['actual_spending'] = df_summary['actual_spending'].fillna(0) # Ganti NaN dengan 0

    # Hitung persentase
    df_summary['percent_spent'] = (df_summary['actual_spending'] / df_summary['amount']) * 100
    df_summary['progress_percent'] = df_summary['percent_spent'].apply(lambda x: min(x, 100))

    # Tampilkan progress bar untuk setiap kategori
    for row in df_summary.itertuples():
        st.write(f"**{row.category}** (Anggaran: Rp {row.amount:,.0f})")
        st.write(f"Terpakai: Rp {row.actual_spending:,.0f} ({row.percent_spent:.1f}%)")
        
        if row.percent_spent > 100:
            st.progress(100, text="Overbudget!")
            st.error(f"Overbudget sebesar Rp {row.actual_spending - row.amount:,.0f}!")
        else:
            st.progress(int(row.progress_percent))
        st.write("") # Kasih jarak
