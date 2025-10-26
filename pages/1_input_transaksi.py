import streamlit as st
import database as db
import datetime
import ai_helper
import json

st.set_page_config(page_title="Input Transaksi", page_icon="💸")
st.title("💸 Input Transaksi")

# --- Persiapan Kategori ---
budget_categories = db.get_budget_categories()
income_categories = ["Gaji", "Bonus", "Investasi", "Lain-Lain (Pemasukan)"]

if "Lain-Lain (Pengeluaran)" not in budget_categories:
    budget_categories.append("Lain-Lain (Pengeluaran)")

# --- Cek Mode Edit ---
is_edit_mode = False
if 'edit_trx' in st.session_state:
    is_edit_mode = True
    trx_data = st.session_state.edit_trx
    st.info(f"Anda sedang mengedit transaksi ID: {trx_data['id']}. Silakan ubah data di form 'Input Manual' di bawah.")

# --- Bagian Input Cepat (AI) ---
st.subheader("Input Cepat (AI)")
ai_disabled = is_edit_mode

with st.form("ai_form"):
    user_input = st.text_area("Apa yang baru?", "Contoh: makan siang di warteg 25rb", disabled=ai_disabled)
    submit_ai = st.form_submit_button("Catat dengan AI ⚡", disabled=ai_disabled)

# Inisialisasi state jika belum ada
if 'ai_result' not in st.session_state:
    st.session_state.ai_result = None

if submit_ai and user_input:
    with st.spinner("AI sedang memproses..."):
        all_categories = budget_categories + income_categories
        ai_result = ai_helper.parse_transaction_with_ai(user_input, all_categories)
        
        if ai_result:
            # NORMALISASI: Pastikan output AI juga konsisten
            ai_result['category'] = ai_result['category'].strip().title()
            ai_result['type'] = ai_result['type'].strip().title()
            
            # Validasi kategori AI
            if ai_result['type'] == 'Pengeluaran' and ai_result['category'] not in budget_categories:
                st.warning(f"AI memilih kategori '{ai_result['category']}' yang tidak ada di daftar anggaran Anda. Menggantinya ke 'Lain-Lain (Pengeluaran)'.")
                ai_result['category'] = 'Lain-Lain (Pengeluaran)'
            
            elif ai_result['type'] == 'Pemasukan' and ai_result['category'] not in income_categories:
                st.warning(f"AI memilih kategori '{ai_result['category']}' yang tidak ada di daftar pemasukan. Menggantinya ke 'Lain-Lain (Pemasukan)'.")
                ai_result['category'] = 'Lain-Lain (Pemasukan)'
                
            st.session_state.ai_result = ai_result
        else:
            st.error("AI tidak dapat memproses input Anda. Coba lagi.")
            st.session_state.ai_result = None

# --- Bagian Konfirmasi AI ---
if st.session_state.ai_result:
    res = st.session_state.ai_result
    st.info(f"**Konfirmasi Data dari AI:**\n"
            f"- **Tipe:** {res['type']}\n"
            f"- **Jumlah:** Rp {res['amount']:,.0f}\n"
            f"- **Kategori:** {res['category']}\n"
            f"- **Deskripsi:** {res['description']}")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ Ya, Simpan", use_container_width=True, type="primary"):
            try:
                db.add_transaction(
                    date=str(datetime.date.today()),
                    description=res['description'],
                    amount=res['amount'],
                    type=res['type'],
                    category=res['category']
                )
                st.success("Transaksi berhasil disimpan oleh AI!")
                st.session_state.ai_result = None
                st.rerun()
            except Exception as e:
                st.error(f"Gagal menyimpan ke database: {e}")
                
    with col2:
        if st.button("❌ Batal", use_container_width=True):
            st.session_state.ai_result = None
            st.rerun()

st.markdown("---")

# --- Form Input Manual (Sekarang dengan Mode Edit) ---
st.subheader("Input Manual")

# Siapkan nilai default untuk form
if is_edit_mode:
    trx_data = st.session_state.edit_trx
    default_date = datetime.date.fromisoformat(trx_data['date'])
    default_type = trx_data['type']
    default_amount = trx_data['amount']
    default_desc = trx_data['description']
    default_category = trx_data['category']
    submit_label = "Update Transaksi"
else:
    default_date = datetime.date.today()
    default_type = "Pengeluaran"
    default_amount = 0.0
    default_desc = ""
    default_category = None
    submit_label = "Simpan Transaksi"

# Tentukan daftar kategori dan indeks default
if default_type == "Pengeluaran":
    categories_list = budget_categories
else:
    categories_list = income_categories

default_category_index = 0
if default_category and default_category in categories_list:
    default_category_index = categories_list.index(default_category)
elif default_category:
    # Jika kategori (dari data edit) tidak ada di list (misal sudah dihapus)
    # Tambahkan sementara ke list agar tidak error
    categories_list.append(default_category)
    default_category_index = categories_list.index(default_category)

# Buat form
with st.form("manual_input_form", clear_on_submit=False):
    date = st.date_input("Tanggal", value=default_date)
    type = st.radio("Tipe Transaksi", ["Pengeluaran", "Pemasukan"], 
                    index=["Pengeluaran", "Pemasukan"].index(default_type), 
                    horizontal=True)
    
    # Kategori: Pilihan berubah berdasarkan Tipe
    if type == "Pengeluaran":
        category = st.selectbox("Kategori", budget_categories, index=default_category_index)
    else:
        category = st.selectbox("Kategori", income_categories, index=default_category_index)
        
    amount = st.number_input("Jumlah (Rp)", min_value=0.0, step=1000.0, value=default_amount)
    description = st.text_input("Deskripsi Singkat (Opsional)", value=default_desc)
    
    submitted = st.form_submit_button(submit_label)

    if submitted:
        if not category:
            st.error("Error: Kategori tidak boleh kosong.")
        elif amount <= 0:
            st.error("Error: Jumlah harus lebih dari nol.")
        else:
            if is_edit_mode:
                # Panggil fungsi UPDATE
                db.update_transaction(
                    trx_id=trx_data['id'],
                    date=str(date),
                    description=description,
                    amount=amount,
                    type=type,
                    category=category
                )
                st.success(f"Transaksi ID {trx_data['id']} berhasil di-update!")
                del st.session_state.edit_trx
                st.rerun()
            else:
                # Panggil fungsi ADD (Tambah baru)
                db.add_transaction(str(date), description, amount, type, category)
                st.success(f"Transaksi '{type}' sebesar Rp {amount:,.0f} untuk '{category.title()}' berhasil disimpan!")
                st.rerun()
                
# Tombol untuk batal edit
if is_edit_mode:
    if st.button("Batal Edit"):
        del st.session_state.edit_trx
        st.rerun()