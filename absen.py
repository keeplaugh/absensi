import pandas as pd  

# Variabel untuk menentukan periode tanggal yang bisa diubah
start_date = "21-01-2025"  # Format: dd-mm-yyyy
end_date = "20-02-2025"    # Format: dd-mm-yyyy

# Baca data CSV dengan memastikan format tanggal sesuai
df = pd.read_csv("raw scanlog test.csv", parse_dates=["Tanggal"], dayfirst=True)

# Pastikan tanggal sudah dalam format datetime yang benar
df["Tanggal"] = pd.to_datetime(df["Tanggal"], format="%d-%m-%Y", errors="coerce")

# Hapus data dengan tanggal yang tidak terbaca
df = df.dropna(subset=["Tanggal"])

# Filter data berdasarkan periode yang ditentukan
start_date = pd.to_datetime(start_date, format="%d-%m-%Y")
end_date = pd.to_datetime(end_date, format="%d-%m-%Y")
df = df[(df["Tanggal"] >= start_date) & (df["Tanggal"] <= end_date)]

# Gabungkan kolom Tanggal dan Jam untuk memudahkan perhitungan
df["Datetime"] = pd.to_datetime(df["Tanggal"].dt.strftime("%d-%m-%Y") + " " + df["Jam"], errors="coerce")

# Hapus data yang gagal dikonversi ke datetime
df = df.dropna(subset=["Datetime"])

# Format ulang kolom tanggal menjadi dd/mm/yyyy agar rapi
df["Tanggal"] = df["Tanggal"].dt.strftime("%d/%m/%Y")

# Mengelompokkan berdasarkan NIP, Nama, dan Tanggal untuk mendapatkan jam masuk dan pulang
hasil = df.groupby(["NIP", "Nama", "Tanggal"]).agg(
    Jam_Masuk=("Datetime", "min"),  
    Jam_Pulang=("Datetime", "max")  
).reset_index()

# Hitung total jam kerja
hasil["Total_Jam_Kerja"] = (hasil["Jam_Pulang"] - hasil["Jam_Masuk"]).dt.total_seconds() / 3600

# Format total jam kerja menjadi 2 angka di belakang koma
hasil["Total_Jam_Kerja"] = hasil["Total_Jam_Kerja"].round(2)

# Pivot data agar format sesuai yang diinginkan
pivot_hasil = hasil.pivot(index=["NIP", "Nama"], columns="Tanggal", values="Total_Jam_Kerja").reset_index()

# Urutkan tanggal agar berurutan secara kronologis
sorted_tanggal = sorted([col for col in pivot_hasil.columns if col not in ["NIP", "Nama"]],
                        key=lambda x: pd.to_datetime(x, format="%d/%m/%Y", errors="coerce"))

# Susun kembali kolom dengan NIP dan Nama tetap di kiri
pivot_hasil = pivot_hasil[["NIP", "Nama"] + sorted_tanggal]

# Simpan hasil ke CSV
pivot_hasil.to_csv("rekap_jam_kerja_pivot11.csv", index=False)

# Tampilkan hasil
print(pivot_hasil)
