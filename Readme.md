# Mikrobiyoloji Bakteri ve Alg Tespit Web Sitesi
Web sitemiz, kirli sularda bulunan bakteri ve algleri tespit ederek virüs riski hakkında olasılık hesaplamaları yapmaktadır.
Kullanıcıların yüklediği fotoğraflar, backend tarafında Python ile çalışan sistemimiz ve kendi oluşturduğumuz veri setiyle eğitilmiş model aracılığıyla analiz edilmektedir. 
Frontend ise bu analiz sonuçlarını görselleştirerek, verilen su örneğinde virüs bulunma ihtimalini yüzde olarak göstermektedir.

### Frontend’i çalıştırmak için:
```Bash
cd ...\Mikrobiyoloji\Frontend\mikrobi-app
npm run dev
```

### Backend’i çalıştırmak için:
```Bash
cd ...\Mikrobiyoloji\Backend
python app.py
```
![WebGörünüm](WebGörünüm.png)
![DetectionAfter](Detection.png)
⚠️ Uyarı: Bu sistem %100 kesin sonuç vermez. Tespit sonrası elde edilen bulguların doğrulanması için mutlaka laboratuvar ortamında ek testler yapılmalıdır.