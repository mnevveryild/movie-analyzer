# Movie Analyzer

Film kataloglarını analiz eden Streamlit tabanlı bir uygulama. Proje, TMDB veri setini kullanarak katalog ozeti, tur dagilimi, eksiklik analizi ve yonetici raporu uretir. Raporlar arayuzde incelenebilir ve PDF olarak indirilebilir.

## Ozellikler

- Film katalog ozeti ve temel metrikler
- Tur, dil, yil, populerlik ve puan dagilimi analizi
- Katalog eksiklikleri ve onceliklendirilmis oneriler
- LLM destekli yonetici raporu
- PDF raporu olusturma
- Groq, Anthropic veya OpenAI saglayicisiyle calisma

## Proje Yapisi

```text
movie-analyzer/
├── app.py
├── requirements.txt
├── .env.example
├── data/
│   ├── tmdb_5000_movies.csv
│   └── tmdb_5000_credits.csv
├── src/
│   ├── agents/
│   ├── tools/
│   ├── utils/
│   ├── config.py
│   ├── orchestrator.py
│   ├── prompts.py
│   └── schemas.py
└── tests/
```

## Kurulum

1. Depoyu klonlayin veya proje klasorune girin:

```bash
cd movie-analyzer
```

2. Sanal ortam olusturun ve etkinlestirin:

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
source .venv/bin/activate
```

3. Bagimliliklari yukleyin:

```bash
pip install -r requirements.txt
```

4. Ortam degiskenlerini hazirlayin:

```bash
cp .env.example .env
```

Windows PowerShell kullanirken:

```powershell
Copy-Item .env.example .env
```

Ardindan `.env` dosyasina kullanmak istediginiz LLM saglayicisinin API anahtarini ekleyin.

## Ortam Degiskenleri

```env
LLM_PROVIDER=groq
GROQ_API_KEY=your_key_here
# ANTHROPIC_API_KEY=your_key_here
# OPENAI_API_KEY=your_key_here
# TMDB_API_KEY=your_key_here
```

Desteklenen `LLM_PROVIDER` degerleri:

- `groq`
- `anthropic`
- `openai`

Secilen saglayici icin ilgili API anahtarinin tanimli olmasi gerekir.

## Calistirma

```bash
streamlit run app.py
```

Komut calistiktan sonra Streamlit uygulamasi tarayicida acilir. Arayuzde `Analizi Baslat` dugmesine tiklayarak katalog analizi uretebilirsiniz.

## Veri Dosyalari

Varsayilan katalog yolu `data/tmdb_5000_movies.csv` olarak ayarlanmistir. Projede ayrica TMDB kredi verisi de bulunur:

- `data/tmdb_5000_movies.csv`
- `data/tmdb_5000_credits.csv`

Kok dizinde bulunan CSV dosyalari da orijinal veri seti kopyalari olarak yer alabilir.

## Gelistirme Notlari

- Uygulama giris noktasi: `app.py`
- Analiz akisi: `src/orchestrator.py`
- Ayarlar: `src/config.py`
- Veri modelleri: `src/schemas.py`
- LLM ajanlari: `src/agents/`
- Analiz ve katalog yardimcilari: `src/tools/`

## Test

Test klasoru proje icinde hazir bulunur. Testleri calistirmak icin:

```bash
pytest
```

`pytest` kurulu degilse once gelistirme bagimliligi olarak ekleyebilirsiniz:

```bash
pip install pytest
```
