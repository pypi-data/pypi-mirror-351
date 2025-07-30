import os
import requests
import zipfile
import io

def download_resources():
    url = "https://github.com/DeWeWO/uznltk_data/archive/refs/heads/master.zip"
    save_dir = os.path.join(os.path.dirname(__file__), "Manba")
    os.makedirs(save_dir, exist_ok=True)

    print("ZIP fayl yuklanmoqda...")
    response = requests.get(url)
    response.raise_for_status()

    print("ZIP fayl ochilmoqda...")
    with zipfile.ZipFile(io.BytesIO(response.content)) as z:
        # ZIP ichidagi fayllarni tekshirish
        for file_info in z.infolist():
            # Faqat Manba papkasidagi fayllarni olib chiqaramiz
            if file_info.filename.startswith("uznltk_data-master/Manba/") and not file_info.is_dir():
                # Fayl nomini olish (papkasiz)
                extracted_path = os.path.join(save_dir, os.path.relpath(file_info.filename, "uznltk_data-master/Manba/"))
                # Chiqarish uchun papka yaratish
                os.makedirs(os.path.dirname(extracted_path), exist_ok=True)
                # Faylni chiqarish
                with z.open(file_info) as source, open(extracted_path, "wb") as target:
                    target.write(source.read())
                print(f"Yuklandi: {extracted_path}")

    print("Barcha fayllar yuklandi va Manba papkasiga chiqarildi.")

# funksiyani chaqirish
# download_and_extract_manba()









import requests
import zipfile
import io
import os
import shutil

def download_folder(folder_name):
    repo_url = "https://github.com/JasurOmanov/Manbalar"
    repo_zip_url = repo_url.rstrip("/") + "/archive/refs/heads/main.zip"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:
        print(f"'{folder_name}' papkasi yuklab olinmoqda...")
        response = requests.get(repo_zip_url, headers=headers)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Yuklab olishda xatolik: {e}")
        return

    try:
        with zipfile.ZipFile(io.BytesIO(response.content)) as z:
            main_dir = z.namelist()[0].split('/')[0]
            extract_path = f"{main_dir}/{folder_name}"
            found = False
            extract_to = f"temp_extract_{folder_name}"

            if os.path.exists(extract_to):
                shutil.rmtree(extract_to)
            os.makedirs(extract_to)

            for file in z.namelist():
                if file.startswith(extract_path + "/") and not file.endswith("/"):
                    found = True
                    z.extract(file, extract_to)

            if not found:
                print(f"'{folder_name}' papkasi topilmadi.")
                shutil.rmtree(extract_to)
                return

            if not os.path.exists("Manba"):
                os.makedirs("Manba")

            final_path = os.path.join("Manba", folder_name)
            if os.path.exists(final_path):
                shutil.rmtree(final_path)
            shutil.move(os.path.join(extract_to, main_dir, folder_name), final_path)
            shutil.rmtree(extract_to)
            print(f"'{folder_name}' papkasi 'Manba/' ichiga muvaffaqiyatli yuklandi.")

    except zipfile.BadZipFile:
        print("ZIP faylni ochishda xatolik.")
    except Exception as e:
        print(f"Faylni ajratishda xatolik: {e}")

def book_download():
    download_folder("Uzb_kitoblar")

def news_download():
    download_folder("Yangiliklar")

def numbers_download():
    download_folder("number.txt")