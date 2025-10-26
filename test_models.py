import google.generativeai as genai

# GANTI INI DENGAN KUNCI API ANDA (copy dari secrets.toml)
API_KEY = "AIzaSyCTQohcBUlCm5R41lMQHW2CcBnrtYRAbVE"

try:
    genai.configure(api_key=API_KEY)

    print(f"Versi library yang digunakan: {genai.__version__}")
    print("-" * 30)
    print("Mencoba mendaftar model yang bisa Anda gunakan...")

    # Mari kita lakukan persis seperti yang disarankan error: "Call ListModels"
    count = 0
    for m in genai.list_models():
        # Kita hanya ingin model yang bisa 'generateContent'
        if 'generateContent' in m.supported_generation_methods:
            print(f"-> {m.name}")
            count += 1

    print("-" * 30)
    print(f"Selesai. Ditemukan {count} model yang valid.")

except Exception as e:
    print(f"\n!!! TERJADI ERROR !!!")
    print(e)