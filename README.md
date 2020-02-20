# RESTFUL-facebook-scraper
Server API untuk *scraping* data facebook. Server ini membutuhkan chrome, flas, flask-restful, dan selenium pada server.

Server menerima perintah lalu melakukan *automated browsing* menggunakan selenium. Membutuhkan input email dan password facebook untuk melakukan *scraping* pada profil teman. 

## Disclaimer ##
> PENULIS KODE BELUM MEMPERTIMBANGKAN KEAMANAN DAN LEGALITAS DARI PERILAKU SCRAPING. SERVER MEMBUTUHKAN EMAIL DAN PASSWORD ANDA. MESKIPUN PENULIS KODE TIDAK MEMILIKI NIAT UNTUK MENCURI DATA, PENULIS KODE TIDAK BISA MENJAMIN KEAMANAN DATA LOGIN ANDA. SANGAT DISARANKAN LOGIN DENGAN AKUN DUMMY. **USE AT YOUR OWN RISK, FOR EDUCATIONAL PURPOSE ONLY**

### Mulai server dengan menjalankan *serve-api-fb.py*

## Perintah-perintah:

|HTTP Method| Alamat | Keterangan |
|--------|-------|-------|
| GET | http://[localhost]/fb-api/login | Melakukan pengecekan apakah ada cookie tersimpan dan mengembalikan login atas username siapa |
| POST | http://[localhost]/fb-api/login?email=\<email anda\>&password=\<password anda\> | Login ke profil facebook anda |
| GET | http://[localhost]/fb-api/logout | Menghapus cookie yang tersimpan |
| POST | http://[localhost]/fb-api/find-user?u=\<masukkan nama\> | Cari profil facebook atas nama orang tersebut |
  
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

