import subprocess
import sys

# Flask yüklü değilse yükle
try:
    import flask
except ImportError:
    print("[*] Flask yüklü değil, yükleniyor...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "flask"])
    import flask

from flask import Flask, render_template_string, request, jsonify
import requests
import json

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html lang="tr">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>CAPPYBEAMSERVİCES! (CBS) - Panel</title>
  <style>
    *{box-sizing:border-box;margin:0;padding:0;font-family:'Segoe UI',Tahoma,Geneva,Verdana,sans-serif;}
    body{background:#121212;color:#eee;min-height:100vh;display:flex;flex-direction:column;}
    header{background:#1f1f1f;padding:1rem 2rem;position:fixed;top:0;left:0;right:0;display:flex;align-items:center;justify-content:space-between;border-bottom:2px solid #0af;z-index:1000;}
    header h1{font-weight:900;font-size:1.8rem;letter-spacing:2px;color:#0af;user-select:none;}
    #hamburger{width:30px;height:24px;cursor:pointer;display:flex;flex-direction:column;justify-content:space-between;}
    #hamburger div{background:#0af;height:4px;border-radius:2px;transition:0.3s ease;}
    #hamburger.active div:nth-child(1){transform:translateY(10px) rotate(45deg);}
    #hamburger.active div:nth-child(2){opacity:0;}
    #hamburger.active div:nth-child(3){transform:translateY(-10px) rotate(-45deg);}
    main{margin-top:72px;display:flex;height:calc(100vh - 72px);overflow:hidden;}
    nav{background:#181818;width:280px;padding:1rem 1.5rem 2rem;border-right:2px solid #0af;transition:transform 0.3s ease;overflow-y:auto;position:fixed;top:72px;bottom:0;left:0;z-index:999;}
    nav.hide{transform:translateX(-100%);}
    nav h2{margin-bottom:1rem;font-size:1.4rem;color:#0af;user-select:none;border-bottom:1px solid #0af;padding-bottom:0.3rem;}
    nav ul{list-style:none;}
    nav ul li{margin-bottom:0.6rem;}
    nav ul li button{width:100%;background:transparent;border:none;color:#eee;font-size:1rem;padding:0.4rem 0.7rem;text-align:left;border-radius:4px;cursor:pointer;transition:background 0.2s ease;}
    nav ul li button:hover,nav ul li button.active{background:#0af;color:#121212;}
    section#content{flex-grow:1;margin-left:280px;background:#222;padding:2rem 3rem;overflow-y:auto;}
    @media (max-width:768px){nav{position:fixed;height:calc(100vh - 72px);width:240px;z-index:1100;}section#content{margin-left:0;padding:2rem 1.5rem;}}
    form{margin-top:1rem;max-width:420px;}
    label{display:block;margin-bottom:0.4rem;font-weight:600;color:#0af;}
    input[type="text"],input[type="tel"]{width:100%;padding:0.5rem 0.7rem;font-size:1rem;border-radius:4px;border:none;outline:none;margin-bottom:1rem;background:#333;color:#eee;transition:box-shadow 0.3s ease;}
    input[type="text"]:focus,input[type="tel"]:focus{box-shadow:0 0 6px #0af;}
    button.submit-btn{background:#0af;border:none;padding:0.7rem 1.2rem;color:#121212;font-weight:700;border-radius:5px;cursor:pointer;transition:background 0.25s ease;}
    button.submit-btn:hover{background:#08a;}
    .result-container {
      margin-top: 1rem;
      border: 1px solid #666;
      padding: 10px;
      overflow-x: auto;
      white-space: nowrap;
      font-size: 0.95rem;
      color: #eee;
      background: #222;
      border-radius: 4px;
      margin-bottom: 15px;
    }
    .result-key {
      font-weight: 700;
      border-right: 1px solid #555;
      padding: 0 10px;
      display: inline-block;
      color: #0af;
      user-select:none;
      min-width: 120px;
    }
    .result-value {
      display: inline-block;
      padding: 0 10px;
      max-width: 350px;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: normal;
      vertical-align: top;
      color: #ccc;
    }
    #welcome{text-align:center;margin-top:50px;font-size:2rem;font-weight:700;color:#0af;user-select:none;}
  </style>
</head>
<body>

<header>
  <h1>CAPPYBEAMSERVİCES!(CBS)</h1>
  <div id="hamburger" aria-label="Toggle menu" role="button" tabindex="0">
    <div></div><div></div><div></div>
  </div>
</header>

<main>
  <nav id="menu">
    <h2>Menü</h2>
    <ul>
      <li><button data-api="welcome" class="active">Hoşgeldiniz</button></li>
      <li><button data-api="adsoyad">Ad Soyad Sorgu</button></li>
      <li><button data-api="tcpro">TC Pro</button></li>
      <li><button data-api="adsoyadilice">Ad Soyad İlçe</button></li>
      <li><button data-api="tcgsm">TC GSM</button></li>
      <li><button data-api="tapu">Tapu Bilgisi</button></li>
      <li><button data-api="sulale">Sülale Sorgu</button></li>
      <li><button data-api="okulno">Okul No</button></li>
      <li><button data-api="isyeriyetkili">İşyeri Yetkili</button></li>
      <li><button data-api="gsmdetay">GSM Detay</button></li>
      <li><button data-api="gsm">GSM</button></li>
      <li><button data-api="adres">Adres Sorgu</button></li>
    </ul>
  </nav>

  <section id="content">
    <div id="welcome" style="background-image: url('https://pbs.twimg.com/media/C5INwPSWQAUuQAI.jpg:large'); background-size: cover; background-position: center; background-repeat: no-repeat; height: 100vh; display: flex; justify-content: center; align-items: center; text-align: center; color: white;">
      <h1>Hoş Geldiniz</h1>
    </div>
  </section>
</main>

<script>
const hamburger = document.getElementById('hamburger');
const menu = document.getElementById('menu');
const buttons = menu.querySelectorAll('button');
const content = document.getElementById('content');
let activeBtn = buttons[0];

// Toggle burger menu
hamburger.addEventListener('click', () => {
  hamburger.classList.toggle('active');
  menu.classList.toggle('hide');
});

hamburger.addEventListener('keydown', (e) => {
  if (e.key === "Enter" || e.key === " ") {
    e.preventDefault();
    hamburger.click();
  }
});

// Menu button click handler
buttons.forEach(btn => {
  btn.addEventListener('click', () => {
    if (btn === activeBtn) return;
    activeBtn.classList.remove('active');
    btn.classList.add('active');
    activeBtn = btn;
    loadContent(btn.dataset.api);
    if (window.innerWidth <= 768) {
      hamburger.classList.remove('active');
      menu.classList.add('hide');
    }
  });
});

// Load form or welcome
function loadContent(apiKey) {
  if (apiKey === 'welcome') {
    content.innerHTML = `
      <div id="welcome" style="background-image: url('https://pbs.twimg.com/media/C5INwPSWQAUuQAI.jpg:large'); background-size: cover; background-position: center; background-repeat: no-repeat; height: 100vh; display: flex; justify-content: center; align-items: center; text-align: center; color: white;">
        <h1>CAPPYBEAMSERVİCES PREMİUM PNL'E HOŞGELDİNİZ.<br><br>BOL ŞANS, KOLAY GELSİN!</h1>
      </div>`;
    return;
  }

  const apiMap = {
    adsoyad: {label1:'Ad', label2:'Soyad', input1type:'text', input2type:'text'},
    tcpro: {label1:'TC Kimlik No', label2:null, input1type:'text', input2type:null},
    tcgsm: {label1:'TC Kimlik No', label2:null, input1type:'text', input2type:null},
    tapu: {label1:'TC Kimlik No', label2:null, input1type:'text', input2type:null},
    sulale: {label1:'TC Kimlik No', label2:null, input1type:'text', input2type:null},
    okulno: {label1:'TC Kimlik No', label2:null, input1type:'text', input2type:null},
    isyeriyetkili: {label1:'TC Kimlik No', label2:null, input1type:'text', input2type:null},
    gsmdetay: {label1:'GSM Numarası', label2:null, input1type:'tel', input2type:null},
    gsm: {label1:'GSM Numarası', label2:null, input1type:'tel', input2type:null},
    adres: {label1:'TC Kimlik No', label2:null, input1type:'text', input2type:null},
    adsoyadilice: {label1:'Ad', label2:'Soyad', input1type:'text', input2type:'text'},
  };

  const api = apiMap[apiKey];
  if (!api) {
    content.innerHTML = '<p>API bulunamadı!</p>';
    return;
  }

  let formHTML = `
    <form id="apiForm">
      <label for="input1">${api.label1}:</label>
      <input type="${api.input1type}" id="input1" name="input1" required autocomplete="off" />`;

  if (api.label2) {
    formHTML += `
      <label for="input2">${api.label2}:</label>
      <input type="${api.input2type}" id="input2" name="input2" required autocomplete="off" />`;
  }

  formHTML += `<button class="submit-btn" type="submit">Sorgula</button></form>
    <div id="results"></div>`;

  content.innerHTML = formHTML;

  const form = document.getElementById('apiForm');
  const results = document.getElementById('results');

  form.addEventListener('submit', async e => {
    e.preventDefault();
    results.innerHTML = '<p>Sorgulanıyor...</p>';
    const input1 = form.input1.value.trim();
    const input2 = api.label2 ? form.input2.value.trim() : null;

    if (!input1 || (api.label2 && !input2)) {
      results.innerHTML = '<p>Lütfen gerekli alanları doldurun.</p>';
      return;
    }

    try {
      const res = await fetch('/api/query', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({api: apiKey, input1, input2})
      });

      const data = await res.json();
      if (data.error) {
        results.innerHTML = `<p>Hata: ${data.error}</p>`;
        return;
      }
      if (!data.result || !data.result.data) {
        results.innerHTML = '<p>Geçerli veri bulunamadı.</p>';
        return;
      }
      // Eğer data tek obje ise diziye al
      let dataArray = [];
      if (Array.isArray(data.result.data)) {
        dataArray = data.result.data;
      } else if (typeof data.result.data === 'object') {
        dataArray = [data.result.data];
      } else {
        results.innerHTML = '<p>Geçerli veri formatı değil.</p>';
        return;
      }

      // Her kişi için bir kutu oluştur
      const htmlBlocks = dataArray.map(person => {
        let innerHtml = '';
        for (const [key, value] of Object.entries(person)) {
          innerHtml += `
            <div class="result-key">${key}</div><div class="result-value" title="${value}">${value}</div>`;
        }
        return `<div class="result-container">${innerHtml}</div>`;
      });

      results.innerHTML += htmlBlocks.join('');
    } catch (err) {
      results.innerHTML = `<p>İstek sırasında hata: ${err.message}</p>`;
    }
  });
}

loadContent('welcome');

function checkWidth() {
  if (window.innerWidth > 768) {
    menu.classList.remove('hide');
    hamburger.classList.remove('active');
  } else {
    menu.classList.add('hide');
    hamburger.classList.remove('active');
  }
}
window.addEventListener('resize', checkWidth);
checkWidth();
</script>
</body>
</html>
"""

API_URLS = {
    "adsoyad": lambda ad, soyad: f"https://api.hexnox.pro/sowixapi/adsoyadilice.php?ad={ad}&soyad={soyad}",
    "tcpro": lambda tc, _: f"https://api.hexnox.pro/sowixapi/tcpro.php?tc={tc}",
    "tcgsm": lambda tc, _: f"https://api.hexnox.pro/sowixapi/tcgsm.php?tc={tc}",
    "tapu": lambda tc, _: f"https://api.hexnox.pro/sowixapi/tapu.php?tc={tc}",
    "sulale": lambda tc, _: f"https://api.hexnox.pro/sowixapi/sulale.php?tc={tc}",
    "okulno": lambda tc, _: f"https://api.hexnox.pro/sowixapi/okulno.php?tc={tc}",
    "isyeriyetkili": lambda tc, _: f"https://api.hexnox.pro/sowixapi/isyeriyetkili.php?tc={tc}",
    "gsmdetay": lambda gsm, _: f"https://api.hexnox.pro/sowixapi/gsmdetay.php?gsm={gsm}",
    "gsm": lambda gsm, _: f"https://api.hexnox.pro/sowixapi/gsm.php?gsm={gsm}",
    "adres": lambda tc, _: f"https://api.hexnox.pro/sowixapi/adres.php?tc={tc}",
    "adsoyadilice": lambda ad, soyad: f"https://api.hexnox.pro/sowixapi/adsoyadilice.php?ad={ad}&soyad={soyad}",
}

@app.route("/")
def index():
    return render_template_string(HTML)

@app.route("/api/query", methods=["POST"])
def api_query():
    data = request.json
    if not data:
        return jsonify(error="Geçersiz istek"), 400

    api_key = data.get("api")
    input1 = data.get("input1", "").strip()
    input2 = data.get("input2", "").strip() if data.get("input2") else None

    if not api_key or not input1:
        return jsonify(error="Gerekli parametreler eksik"), 400

    if api_key not in API_URLS:
        return jsonify(error="Bilinmeyen API anahtarı"), 400

    try:
        url = API_URLS[api_key](input1, input2)
    except Exception as e:
        return jsonify(error=f"URL oluşturulamadı: {str(e)}"), 400

    try:
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        try:
            res_json = r.json()
            # Sadece data kısmını dön, diğerleri görünmesin
            if 'data' in res_json:
                return jsonify(result={"data": res_json['data']})
            else:
                # Eğer data yoksa tüm json dön (olmazsa)
                return jsonify(result=res_json)
        except Exception:
            return jsonify(result=r.text)
    except Exception as e:
        return jsonify(error=f"API isteği başarısız: {str(e)}"), 500

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)


