import React, { useMemo, useState } from 'react';
import { createRoot } from 'react-dom/client';
import { Download, Gem, LineChart, Search, Sparkles, Store } from 'lucide-react';
import './styles.css';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const PLATFORMS = ['Etsy', 'Amazon Handmade', 'TikTok Shop', 'eBay', 'Pinterest', 'Google Trends', 'Shopify'];
const CATEGORIES = ['All', 'Handmade jewelry', 'Personalized gifts', 'Keepsake jewelry', 'Spiritual / symbolic jewelry', 'Trend handmade accessories'];

function Badge({ children, tone = 'neutral' }) {
  return <span className={`badge ${tone}`}>{children}</span>;
}

function ScoreBar({ score }) {
  return (
    <div className="score-wrap" aria-label={`Satış potansiyeli ${score}`}>
      <div className="score-bar" style={{ width: `${score}%` }} />
      <strong>{score}</strong>
    </div>
  );
}

function App() {
  const [query, setQuery] = useState('personalized handmade jewelry gift');
  const [category, setCategory] = useState('All');
  const [platforms, setPlatforms] = useState(['Etsy', 'Amazon Handmade', 'TikTok Shop', 'Pinterest']);
  const [data, setData] = useState(null);
  const [selected, setSelected] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const selectedOpportunity = useMemo(() => selected || data?.opportunities?.[0], [selected, data]);

  async function runResearch() {
    setLoading(true);
    setError('');
    try {
      const response = await fetch(`${API_URL}/api/research`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, platforms, category, limit: 10 }),
      });
      if (!response.ok) throw new Error('Araştırma isteği başarısız oldu.');
      const payload = await response.json();
      setData(payload);
      setSelected(payload.opportunities?.[0] || null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function exportCsv() {
    const response = await fetch(`${API_URL}/api/export.csv`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query, platforms, category, limit: 50 }),
    });
    const blob = await response.blob();
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'edel-luxe-product-research.csv';
    link.click();
    URL.revokeObjectURL(url);
  }

  function togglePlatform(platform) {
    setPlatforms((current) => (current.includes(platform) ? current.filter((item) => item !== platform) : [...current, platform]));
  }

  return (
    <main>
      <section className="hero">
        <div>
          <Badge tone="gold"><Sparkles size={14} /> Edel Luxe AI Agent MVP</Badge>
          <h1>Viral Product Research Dashboard</h1>
          <p>
            Etsy, Amazon Handmade, TikTok Shop, eBay, Pinterest, Google Trends ve Shopify odaklı premium handmade ürün fırsatlarını skorlar.
          </p>
        </div>
        <div className="hero-card">
          <Gem size={34} />
          <strong>Brand Lens</strong>
          <span>Premium • Handmade • Giftable • SEO-ready</span>
        </div>
      </section>

      <section className="panel search-panel">
        <label>
          Search input
          <div className="search-box">
            <Search size={18} />
            <input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="örn. birth flower necklace" />
          </div>
        </label>
        <label>
          Kategori seçimi
          <select value={category} onChange={(event) => setCategory(event.target.value)}>
            {CATEGORIES.map((item) => <option key={item}>{item}</option>)}
          </select>
        </label>
        <button className="primary" onClick={runResearch} disabled={loading}>{loading ? 'Araştırılıyor...' : 'Araştırmayı Başlat'}</button>
      </section>

      <section className="platforms panel">
        <h2>Platform seçimi</h2>
        <div className="chips">
          {PLATFORMS.map((platform) => (
            <button key={platform} className={platforms.includes(platform) ? 'chip active' : 'chip'} onClick={() => togglePlatform(platform)}>{platform}</button>
          ))}
        </div>
      </section>

      {error && <div className="error">{error}</div>}
      {data?.disclaimer && <div className="notice">{data.disclaimer}</div>}

      <section className="grid">
        <div className="panel list-panel">
          <div className="section-head">
            <h2><LineChart size={20} /> Trend ürün listesi</h2>
            <button className="secondary" onClick={exportCsv}><Download size={16} /> Export CSV</button>
          </div>
          <div className="table">
            <div className="row header"><span>Ürün</span><span>Platform</span><span>Rekabet</span><span>Skor</span></div>
            {(data?.opportunities || []).map((item) => (
              <button className="row clickable" key={item.id} onClick={() => setSelected(item)}>
                <span>{item.product_name}</span><span>{item.platform}</span><span>{item.competition_level}</span><ScoreBar score={item.sales_potential_score} />
              </button>
            ))}
          </div>
        </div>

        <div className="panel detail-panel">
          <div className="section-head"><h2>ÜRÜN FIRSATI RAPORU</h2><button className="primary small">Edel Luxe için listeleme oluştur</button></div>
          {selectedOpportunity ? <OpportunityReport item={selectedOpportunity} /> : <p className="empty">Araştırma başlatınca rapor burada görünür.</p>}
        </div>
      </section>

      <section className="grid lower">
        <div className="panel">
          <h2><Store size={20} /> Rakip mağaza analizi</h2>
          {(data?.competitors || []).map((competitor) => (
            <article className="competitor" key={competitor.id}>
              <h3>{competitor.shop_name}</h3>
              <Badge>{competitor.platform}</Badge>
              <p><strong>En çok satanlar:</strong> {competitor.best_selling_products}</p>
              <p><strong>SEO:</strong> {competitor.seo_patterns}</p>
              <p><strong>Fırsat boşluğu:</strong> {competitor.opportunity_gap}</p>
            </article>
          ))}
        </div>
        <div className="panel">
          <h2>Keyword analizi</h2>
          <div className="keyword-list">
            {(data?.keywords || []).map((keyword) => (
              <article key={keyword.keyword}>
                <strong>{keyword.keyword}</strong>
                <span>{keyword.intent}</span>
                <small>{keyword.suggested_use} • {keyword.competition_hint}</small>
              </article>
            ))}
          </div>
        </div>
      </section>
    </main>
  );
}

function OpportunityReport({ item }) {
  const fields = [
    ['1. Ürün Adı', item.product_name],
    ['2. Platform', `${item.platform} — ${item.source_url}`],
    ['3. Trend Durumu', item.trend_status],
    ['4. Rekabet Seviyesi', item.competition_level],
    ['5. Ortalama Fiyat', item.average_price],
    ['6. Hedef Müşteri', item.target_customer],
    ['7. Ana Keywordler', item.primary_keywords],
    ['8. Long-tail Keywordler', item.long_tail_keywords],
    ['9. Rakip Ürünlerden Öğrenilenler', item.competitor_learnings],
    ['10. Viral Olma Sebebi', item.viral_reason],
    ['11. Edel Luxe İçin Uygunluk', item.edel_luxe_fit],
    ['12. Önerilen Etsy Başlığı', item.suggested_etsy_title],
    ['13. SEO Uyumlu Açıklama', item.seo_description],
    ['14. 13 Etsy Tag', item.etsy_tags],
    ['15. Görsel Çekim Tavsiyesi', item.photo_advice],
    ['16. Ürün Geliştirme Fikri', item.product_development_idea],
    ['17. Satış Potansiyeli Puanı', `${item.sales_potential_score}/100 (${item.estimated_sales_potential})`],
    ['18. İlk Aksiyon Planı', item.first_action_plan],
  ];
  return (
    <div className="report">
      <div className="report-top"><Badge tone="gold">{item.data_confidence}</Badge><ScoreBar score={item.sales_potential_score} /></div>
      {fields.map(([label, value]) => <p key={label}><strong>{label}:</strong> {value}</p>)}
    </div>
  );
}

createRoot(document.getElementById('root')).render(<App />);
