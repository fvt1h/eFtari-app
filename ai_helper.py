import streamlit as st
import google.generativeai as genai
import json

def parse_transaction_with_ai(user_input, categories):
    """
    Mengirim input pengguna ke Gemini untuk diproses dan mengembalikan JSON terstruktur.
    """
    
    # 1. Konfigurasi model AI dengan API key dari st.secrets
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel('models/gemini-flash-latest') # Menggunakan model dari hasil tes
    except Exception as e:
        st.error(f"Error konfigurasi Gemini: {e}")
        st.error("Pastikan Anda sudah mengatur GEMINI_API_KEY di file .streamlit/secrets.toml")
        return None

    # 2. Membuat prompt yang sangat spesifik
    # Ini adalah bagian terpenting (Prompt Engineering)
    
    # Mengubah list kategori menjadi string yang mudah dibaca AI
    category_list_string = ", ".join(categories)

    prompt = f"""
    Anda adalah asisten keuangan pribadi yang cerdas. 
    Tugas Anda adalah mengekstrak informasi transaksi dari teks bahasa Indonesia 
    dan mengembalikannya dalam format JSON yang ketat.
    
    Teks dari pengguna: "{user_input}"

    Anda HARUS mengikuti aturan ini:
    1.  'type' harus 'Pemasukan' atau 'Pengeluaran'. Tentukan dari konteks. 
        (Contoh: "dapat gaji" -> Pemasukan, "beli kopi" -> Pengeluaran).
    2.  'amount' harus berupa angka (integer) saja, tanpa "Rp", "rb", atau "k". 
        (Contoh: "50rb" -> 50000, "1.5 juta" -> 1500000).
    3.  'description' adalah deskripsi singkat dari teks asli.
    4.  'category' HARUS dipilih dari daftar berikut: {category_list_string}.
    5.  Jika kategori tidak ada di daftar, pilih kategori yang paling mirip. 
        Contoh: "makan siang" harus masuk ke "Makanan". "ongkos ojol" ke "Transportasi".
    6.  Jika tidak ada kategori yang cocok sama sekali, gunakan "Lain-lain (Pengeluaran)".
    
    Format output HARUS berupa JSON saja, tanpa teks tambahan:
    {{
      "type": "...",
      "amount": ...,
      "description": "...",
      "category": "..."
    }}
    """

    # 3. Panggil API
    try:
        response = model.generate_content(prompt)
        
        # 4. Bersihkan dan parse output
        # Menghapus "```json" dan "```" yang mungkin ditambahkan oleh model
        cleaned_response = response.text.strip().replace("```json", "").replace("```", "").strip()
        
        # Ubah string JSON menjadi dictionary Python
        parsed_json = json.loads(cleaned_response)
        return parsed_json
    
    except json.JSONDecodeError:
        st.error("Error: AI mengembalikan format yang tidak valid.")
        print("AI response (invalid):", response.text) # Untuk debug di terminal
        return None
    except Exception as e:
        st.error(f"Error saat memanggil AI: {e}")
        return None