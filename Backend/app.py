from flask import Flask, request, jsonify
from flask import Flask, send_from_directory
from flask_cors import CORS
from ultralytics import YOLO
import cv2
import numpy as np
import base64
from PIL import Image
import io

app = Flask(__name__, static_folder="../Frontend/mikrobi-app/build", static_url_path="/")

@app.route("/")
def serve_index():
    return send_from_directory(app.static_folder, "index.html")

@app.route("/<path:path>")
def serve_static(path):
    return send_from_directory(app.static_folder, path)


CORS(app)
# YOLO modelini yükle
model = YOLO('best.pt')  # best.pt dosyası bu Python dosyası ile aynı klasörde olmalı

# Sınıf listelerini yükle
def load_class_data(filename):
    """Alg.txt veya Bakteri.txt dosyasından sınıf ve virüs oranlarını oku"""
    class_virus_prob = {}
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and '%' in line:
                parts = line.rsplit('%', 1)
                class_name = parts[0].strip()
                virus_prob = int(parts[1].strip())
                class_virus_prob[class_name] = virus_prob
    return class_virus_prob

# Başlangıçta dosyaları yükle
alg_virus_data = load_class_data('Alg.txt')
bakteri_virus_data = load_class_data('Bakteri.txt')

# Model sınıf isimlerini al (best.pt'nizden otomatik gelecek)
# Örnek: model.names = {0: 'Bacillus', 1: 'Algal', 2: 'Microcystis', ...}

def classify_organism(class_name):
    """Sınıf isminin bakteri mi alg mi olduğunu belirle"""
    if class_name in bakteri_virus_data:
        return 'bacteria', bakteri_virus_data[class_name]
    elif class_name in alg_virus_data:
        return 'algae', alg_virus_data[class_name]
    else:
        # Bilinmeyen sınıflar için varsayılan değer
        return 'unknown', 30

@app.route('/analyze', methods=['POST'])
def analyze_image():
    try:
        # Görüntüyü al
        image_file = request.files['image']
        image_bytes = image_file.read()
        
        # Görüntüyü numpy array'e çevir
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        # ====================================
        # YOLO PREDICT - DETECTION
        # ====================================
        results = model.predict(img, conf=0.25)  # Confidence threshold: 0.25
        
        # Tespit edilen nesneleri say
        bacteria_count = 0
        algae_count = 0
        virus_probabilities = []
        
        # Sonuçları işle
        for result in results:
            boxes = result.boxes
            for box in boxes:
                # Sınıf ID'sini al
                class_id = int(box.cls[0])
                class_name = model.names[class_id]
                confidence = float(box.conf[0])
                
                # Bu sınıfın bakteri mi alg mi olduğunu belirle
                org_type, virus_prob = classify_organism(class_name)
                
                if org_type == 'bacteria':
                    bacteria_count += 1
                    virus_probabilities.append(virus_prob)
                elif org_type == 'algae':
                    algae_count += 1
                    virus_probabilities.append(virus_prob)
                
                print(f"Tespit: {class_name} ({org_type}) - Güven: {confidence:.2f} - Virüs Olasılığı: {virus_prob}%")
        
        # İşlenmiş görüntüyü oluştur (YOLO detection boxes ile)
        annotated_img = results[0].plot()  # Kutucukları çizilmiş görüntü
        
        # Görüntüyü base64'e çevir
        _, buffer = cv2.imencode('.jpg', annotated_img)
        img_base64 = base64.b64encode(buffer).decode('utf-8')
        processed_image = f"data:image/jpeg;base64,{img_base64}"
        
        # Yüzdelikleri hesapla
        total_organisms = bacteria_count + algae_count
        
        if total_organisms == 0:
            # Hiçbir şey tespit edilmediyse
            return jsonify({
                'bacteria_percentage': 0,
                'algae_percentage': 0,
                'virus_probability': 0,
                'processed_image': processed_image,
                'message': 'Hiçbir mikroorganizma tespit edilemedi'
            })
        
        bacteria_pct = bacteria_count
        algae_pct = algae_count
        
        # Virüs olasılığını hesapla (ortalama)
        avg_virus_prob = int(np.mean(virus_probabilities)) if virus_probabilities else 0
        
        print(f"\n=== SONUÇ ===")
        print(f"Bakteri: {bacteria_count} adet ({bacteria_pct}%)")
        print(f"Alg: {algae_count} adet ({algae_pct}%)")
        print(f"Ortalama Virüs Olasılığı: {avg_virus_prob}%")
        
        return jsonify({
            'bacteria_percentage': bacteria_pct,
            'algae_percentage': algae_pct,
            'virus_probability': avg_virus_prob,
            'processed_image': processed_image,
            'bacteria_count': bacteria_count,
            'algae_count': algae_count,
            'total_detected': total_organisms
        })
        
    except Exception as e:
        print(f"HATA: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/test', methods=['GET'])
def test():
    """Sunucunun çalıştığını test et"""
    return jsonify({
        'status': 'OK',
        'model_loaded': model is not None,
        'alg_classes': len(alg_virus_data),
        'bacteria_classes': len(bakteri_virus_data)
    })

if __name__ == '__main__':
    print("🚀 Sunucu başlatılıyor...")
    print(f"📊 Yüklenen Alg sınıfları: {len(alg_virus_data)}")
    print(f"🦠 Yüklenen Bakteri sınıfları: {len(bakteri_virus_data)}")
    print(f"🤖 YOLO Model: {model.names}")
    app.run(debug=True, port=5000, host='0.0.0.0')