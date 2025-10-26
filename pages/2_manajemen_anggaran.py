import streamlit as st
import database as db
import pandas as pd

st.set_page_config(page_title="Manajemen Anggaran", page_icon="📊")
st.title("📊 Manajemen Anggaran")

# --- Inisialisasi Session State untuk Edit ---
if 'edit_category' not in st.session_state:
    st.session_state.edit_category = None
if 'edit_amount' not in st.session_state:
    st.session_state.edit_amount = 0.0

# --- Form untuk Menambah/Edit Anggaran ---
st.subheader("Tambah atau Edit Anggaran Bulanan")

# Jika kita dalam mode edit, isi form dengan data yang ada
if st.session_state.edit_category:
    st.write(f"Anda sedang mengedit: **{st.session_state.edit_category}**")
    default_category = st.session_state.edit_category
    default_amount = st.session_state.edit_amount
    submit_label = "Update Anggaran"
else:
    default_category = ""
    default_amount = 0.0
    submit_label = "Simpan Anggaran Baru"

with st.form("budget_form", clear_on_submit=False):
    # Kategori: Nonaktifkan input teks jika sedang mengedit (mencegah ganti nama)
    category = st.text_input(
        "Kategori", 
        value=default_category, 
        disabled=bool(st.session_state.edit_category) # Nonaktifkan jika edit
    )
    amount = st.number_input(
        "Jumlah Anggaran (Rp)", 
        min_value=0.0, 
        step=50000.0,
        value=default_amount
    )
    
    submitted = st.form_submit_button(submit_label)

    if submitted:
        # Jika tidak dalam mode edit, ambil kategori dari input
        category_to_save = st.session_state.edit_category if st.session_state.edit_category else category
        
        if not category_to_save or amount <= 0:
            st.error("Kategori dan Jumlah harus diisi dan lebih dari nol.")
        else:
            db.add_budget(category_to_save, amount) # add_budget akan update jika kategori ada
            st.success(f"Anggaran untuk '{category_to_save.title()}' disimpan/diperbarui ke Rp {amount:,.0f}")
            
            # Keluar dari mode edit setelah update
            st.session_state.edit_category = None
            st.session_state.edit_amount = 0.0
            st.rerun()

# Tombol untuk batal edit
if st.session_state.edit_category:
    if st.button("Batal Edit"):
        st.session_state.edit_category = None
        st.session_state.edit_amount = 0.0
        st.rerun()

# --- Menampilkan Anggaran Saat Ini (Dengan Tombol Edit & Hapus) ---
st.markdown("---")
st.subheader("Anggaran Anda Saat Ini")

budgets_data = db.get_all_budgets()

if not budgets_data:
    st.info("Anda belum menetapkan anggaran apapun.")
else:
    # Buat header tabel manual
    col1, col2, col3 = st.columns([2, 2, 2]) # Beri ruang lebih untuk 2 tombol
    col1.write("**Kategori**")
    col2.write("**Jumlah (Rp)**")
    col3.write("**Aksi**")

    st.markdown("---")

    # Loop untuk setiap anggaran
    for budget in budgets_data:
        col1, col2, col3 = st.columns([2, 2, 2])
        with col1:
            st.write(budget['category'])
        with col2:
            st.write(f"Rp {budget['amount']:,.0f}")
        with col3:
            # Buat 2 kolom di dalam kolom Aksi
            b_col1, b_col2 = st.columns(2)
            with b_col1:
                # Tombol Edit: Set session state
                if st.button("✏️", key=f"edit_budget_{budget['category']}"):
                    st.session_state.edit_category = budget['category']
                    st.session_state.edit_amount = budget['amount']
                    st.rerun() # Refresh untuk memuat data ke form
            
            with b_col2:
                # Tombol Hapus: Panggil fungsi delete
                if st.button("🗑️", key=f"del_budget_{budget['category']}", type="primary"):
                    db.delete_budget_by_category(budget['category'])
                    st.toast(f"Anggaran '{budget['category']}' telah dihapus.")
                    # Jika kita menghapus item yang sedang diedit, batalkan edit
                    if st.session_state.edit_category == budget['category']:
                        st.session_state.edit_category = None
                        st.session_state.edit_amount = 0.0
                    st.rerun() # Refresh halaman