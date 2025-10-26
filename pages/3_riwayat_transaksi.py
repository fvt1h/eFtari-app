import streamlit as st
import database as db
import pandas as pd

st.set_page_config(page_title="Riwayat Transaksi", page_icon="🧾")
st.title("🧾 Riwayat Semua Transaksi Anda")

# (Nanti kita akan tambahkan filter di sini)
st.subheader("Daftar Transaksi")

# Ambil semua data transaksi
all_transactions = db.get_all_transactions()

if not all_transactions:
    st.info("Belum ada data transaksi yang tercatat.")
else:
    # Buat header tabel manual
    cols = st.columns([1, 2, 2, 2, 2, 2]) # Beri ruang lebih untuk 2 tombol
    headers = ["Tanggal", "Kategori", "Tipe", "Jumlah (Rp)", "Deskripsi", "Aksi"]
    for col, header in zip(cols, headers):
        col.write(f"**{header}**")
    
    st.markdown("---")

    # Loop untuk setiap transaksi
    for trx in all_transactions:
        cols = st.columns([1, 2, 2, 2, 2, 2])
        cols[0].write(trx['date'])
        cols[1].write(trx['category'])
        cols[2].write(trx['type'])
        cols[3].write(f"Rp {trx['amount']:,.0f}")
        cols[4].write(trx['description'])
        
        # Kolom ke-5 (indeks 5) untuk tombol Aksi
        with cols[5]:
            # Buat 2 kolom di dalam kolom Aksi
            b_col1, b_col2 = st.columns(2)
            with b_col1:
                # Tombol Edit
                if st.button("✏️", key=f"edit_trx_{trx['id']}"):
                    # Simpan seluruh data transaksi ke session state
                    st.session_state.edit_trx = dict(trx) 
                    # Pindah ke halaman input
                    st.switch_page("pages/1_Input_Transaksi.py")
            
            with b_col2:
                # Tombol Hapus
                if st.button("🗑️", key=f"del_trx_{trx['id']}", type="primary"):
                    db.delete_transaction_by_id(trx['id'])
                    st.toast(f"Transaksi (ID: {trx['id']}) telah dihapus.")
                    st.rerun()