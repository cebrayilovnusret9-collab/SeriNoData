from flask import Flask, jsonify, request
import csv, os

app = Flask(__name__)

def search_in_all_parts(tc=None, ad=None, soyad=None, il=None, ilce=None, seri_no=None, limit=50):
    """Tüm parça dosyalarında detaylı arama"""
    results = []
    
    # Tüm part dosyalarını bul
    for i in range(1, 100):
        for filename in [f"serino_part_{i}.csv", f"serino_part_{i:02d}.csv"]:
            if os.path.exists(filename):
                with open(filename, 'r', encoding='utf-8') as f:
                    reader = csv.reader(f)
                    
                    for row in reader:
                        if len(row) >= 14:
                            match = True
                            
                            # TC NO ile arama
                            if tc and tc not in row[1]:
                                match = False
                                
                            # AD ile arama
                            if ad and ad.upper() not in row[2].upper():
                                match = False
                                
                            # SOYAD ile arama
                            if soyad and soyad.upper() not in row[3].upper():
                                match = False
                            
                            # İL ile arama
                            if il and il.upper() not in row[6].upper():
                                match = False
                            
                            # İLÇE ile arama
                            if ilce and len(row) > 9 and ilce.upper() not in row[9].upper():
                                match = False
                            
                            # SERİ NO ile arama
                            if seri_no and len(row) > 13 and seri_no.upper() not in row[13].upper():
                                match = False
                            
                            if match:
                                results.append({
                                    'id': row[0],
                                    'tc': row[1],  # Burada tc
                                    'ad': row[2],
                                    'soyad': row[3],
                                    'cinsiyet': row[4] if len(row) > 4 else '',
                                    'dogum_tarihi': row[5] if len(row) > 5 else '',
                                    'dogum_yeri': row[6] if len(row) > 6 else '',
                                    'medeni_durum': row[7] if len(row) > 7 else '',
                                    'il': row[8] if len(row) > 8 else '',
                                    'ilce': row[9] if len(row) > 9 else '',
                                    'durum': row[10] if len(row) > 10 else '',
                                    'anne_adi': row[11] if len(row) > 11 else '',
                                    'baba_adi': row[12] if len(row) > 12 else '',
                                    'seri_no': row[13] if len(row) > 13 else ''
                                })
                                
                                if len(results) >= limit:
                                    return results
                break
    
    return results

@app.route('/')
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head><title>186K Seri No API</title><meta charset="utf-8"></head>
    <body>
        <h1>🪖 186K Seri No Veritabanı API</h1>
        <p><strong>Kurucu:</strong> @sukazatkinis</p>
        <p><strong>Telegram:</strong> @f3system</p>
        <p><strong>API Endpoint'leri (tc parametresi ile):</strong></p>
        <ul>
            <li><code>/serino?tc=31702753468</code></li>
            <li><code>/serino?ad=GENCAY&soyad=EROL</code></li>
            <li><code>/serino?ad=GENCAY</code></li>
            <li><code>/serino?soyad=EROL</code></li>
            <li><code>/serino?il=TEKİRDAĞ&ilce=SÜLEYMANPAŞA</code></li>
            <li><code>/serino?seri_no=A30T00779</code></li>
            <li><code>/serino?ad=GENCAY&il=TOKAT&limit=10</code></li>
        </ul>
    </body>
    </html>
    """

@app.route('/serino')
def serino_api():
    # Tüm arama parametreleri - tc parametresi var
    tc = request.args.get('tc', '')
    ad = request.args.get('ad', '')
    soyad = request.args.get('soyad', '')
    il = request.args.get('il', '')
    ilce = request.args.get('ilce', '')
    seri_no = request.args.get('seri_no', '')
    cinsiyet = request.args.get('cinsiyet', '')
    limit = min(int(request.args.get('limit', 50)), 100)
    
    results = search_in_all_parts(
        tc=tc, ad=ad, soyad=soyad, il=il, ilce=ilce, seri_no=seri_no, limit=limit
    )
    
    # Cinsiyet filtresi
    if cinsiyet:
        filtered = []
        for kayit in results:
            if cinsiyet.upper() in kayit['cinsiyet'].upper():
                filtered.append(kayit)
        results = filtered
    
    return jsonify({
        'sorgu': {
            'tc': tc,
            'ad': ad,
            'soyad': soyad,
            'il': il,
            'ilce': ilce,
            'seri_no': seri_no,
            'cinsiyet': cinsiyet
        },
        'bulunan': len(results),
        'sonuclar': results,
        'kurucu': '@sukazatkinis',
        'telegram': '@f3system'
    })

# Direkt TC ile arama (alternatif endpoint)
@app.route('/serino/tc/<tc_no>')
def serino_by_tc(tc_no):
    results = search_in_all_parts(tc=tc_no, limit=1)
    
    if results:
        return jsonify({
            'sonuc': results[0],
            'kurucu': '@sukazatkinis',
            'telegram': '@f3system'
        })
    
    return jsonify({'error': 'Kayıt bulunamadı'}), 404

# Direkt Seri No ile arama
@app.route('/serino/seri/<seri_no>')
def serino_by_serial(seri_no):
    results = search_in_all_parts(seri_no=seri_no, limit=10)
    
    return jsonify({
        'seri_no': seri_no,
        'bulunan': len(results),
        'sonuclar': results,
        'kurucu': '@sukazatkinis',
        'telegram': '@f3system'
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
