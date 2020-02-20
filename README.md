# RESTFUL-facebook-scraper
Server API untuk *scraping* data facebook. Server ini membutuhkan chrome, flas, flask-restful, dan selenium pada server.

## Disclaimer ##
> PENULIS KODE BELUM MEMPERTIMBANGKAN KEAMANAN DAN LEGALITAS DARI PERILAKU SCRAPING. SERVER MEMBUTUHKAN EMAIL DAN PASSWORD ANDA. MESKIPUN PENULIS KODE TIDAK MEMILIKI NIAT UNTUK MENCURI DATA, PENULIS KODE TIDAK BISA MENJAMIN KEAMANAN DATA LOGIN ANDA. SANGAT DISARANKAN LOGIN DENGAN AKUN DUMMY. **USE AT YOUR OWN RISK, FOR EDUCATIONAL PURPOSE ONLY**

Server menerima perintah lalu melakukan *automated browsing* menggunakan selenium. Membutuhkan input email dan password facebook untuk melakukan *scraping* pada profil teman. Hasil scraping akan mengembalikan data json yang berisi 
- Nama Lengkap
- User ID
- Photo Profil
- Cover Image
- Biografi
- Relationship
- Tanggal Lahir
- Jumlah Teman

Beberapa post terakhir yang ada di halaman utama profil dengan detail:
- Post Text
- Post Date
- Post Url
- Jumlah Reaction
- Komentar Post

Hasil pencarian juga disimpan dalam file db,csv, dan json di direktori server.

### Mulai server dengan menjalankan *serve-api-fb.py*

## Perintah-perintah:

|HTTP Method| Alamat | Keterangan |
|--------|-------|-------|
| GET | http://[localhost]/fb-api/login | Melakukan pengecekan apakah ada cookie tersimpan dan mengembalikan login atas username siapa |
| POST | http://[localhost]/fb-api/login?email=\<email anda\>&password=\<password anda\> | Login ke profil facebook anda |
| GET | http://[localhost]/fb-api/logout | Logout dan menghapus cookie yang tersimpan |
| POST | http://[localhost]/fb-api/find-user?u=\<masukkan nama\> | Cari profil facebook atas nama orang tersebut |

Untuk mencari profil, diharuskan memasukkan informasi login terlebih dahulu. Bila server mengembalikan ```{'message':"need login"}``` meskipun anda sudah login, silahkan mencoba restart app server atau lakukan logout/login.

 Pengetesan dilakukan dengan curl melalui comand prompt dengan perintah berikut ini:
 Untuk login gunakan 
``` curl -i http://127.0.0.1:5000/fb-api/login -d "email=\<email anda\>" -d "password=\<password anda\>"```

 Untuk mencari profil gunakan 
``` curl -i http://127.0.0.1:5000/fb-api/login -d "u=\<nama yang hendak dicari\>"```

Requirement:
- [Flask](https://flask.palletsprojects.com/en/1.1.x/)
- [Flask-RESTFUL](https://flask-restful.readthedocs.io/en/latest/)
- [Selenium](https://www.selenium.dev/projects/)
- Sqlite3

