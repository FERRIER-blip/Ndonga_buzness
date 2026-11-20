import { useEffect, useState } from 'react'
import { LayoutDashboard, Package, ShoppingBag, Users, MessageCircle, Plus, Search, RefreshCw, X, Menu, ExternalLink } from 'lucide-react'
import { api } from './api'

const money = n => new Intl.NumberFormat('fr-FR').format(Number(n || 0)) + ' FCFA'

export default function App() {
  const [page, setPage] = useState('dashboard')
  const [stats, setStats] = useState(null)
  const [products, setProducts] = useState([])
  const [orders, setOrders] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [showForm, setShowForm] = useState(false)
  const [form, setForm] = useState({ name: '', category: 'Autres', description: '', price: '', stock: '' })
  const [search, setSearch] = useState('')
  const [mobileNav, setMobileNav] = useState(false)
  const [chatInput, setChatInput] = useState('')
  const [chatBusy, setChatBusy] = useState(false)
  const [chatMessages, setChatMessages] = useState([{ role: 'bot', text: 'Bonjour ! Je suis l’assistant Ndonga_buzness. Écrivez MENU pour commencer.' }])
  const [chatSession] = useState(() => `demo-${Date.now()}`)

  async function load() {
    setLoading(true); setError('')
    try {
      const [s, p, o] = await Promise.all([api.stats(), api.products(), api.orders()])
      setStats(s); setProducts(p); setOrders(o)
    } catch (e) { setError(e.message) }
    finally { setLoading(false) }
  }
  useEffect(() => { load() }, [])

  async function saveProduct(e) {
    e.preventDefault()
    try {
      await api.addProduct({ ...form, price: Number(form.price), stock: Number(form.stock), active: true })
      setForm({ name: '', category: 'Autres', description: '', price: '', stock: '' })
      setShowForm(false); await load()
    } catch (e) { setError(e.message) }
  }

  async function sendChat(e) {
    e?.preventDefault()
    const message = chatInput.trim()
    if (!message || chatBusy) return
    setChatMessages(prev => [...prev, { role: 'user', text: message }])
    setChatInput(''); setChatBusy(true)
    try { const result = await api.chat(chatSession, message); setChatMessages(prev => [...prev, { role: 'bot', text: result.reply }]) }
    catch (err) { setChatMessages(prev => [...prev, { role: 'bot', text: `Erreur : ${err.message}` }]) }
    finally { setChatBusy(false) }
  }

  async function changeStatus(order, status) {
    try { await api.updateOrder(order.id, status); await load() }
    catch (e) { setError(e.message) }
  }

  const nav = [
    ['dashboard', 'Vue générale', LayoutDashboard],
    ['products', 'Produits', Package],
    ['orders', 'Commandes', ShoppingBag],
    ['customers', 'Clients', Users],
    ['assistant', 'Tester le BOT', MessageCircle],
    ['messages', 'WhatsApp', MessageCircle],
  ]

  const filteredProducts = products.filter(p => `${p.name} ${p.category}`.toLowerCase().includes(search.toLowerCase()))
  const filteredOrders = orders.filter(o => `${o.order_number} ${o.customer_name} ${o.phone}`.toLowerCase().includes(search.toLowerCase()))

  return <div className="app-shell">
    <aside className={`sidebar ${mobileNav ? 'open' : ''}`}>
      <div className="brand"><div className="brand-mark">N</div><div><b>Ndonga_buzness</b><small>ESPACE COMMERCE</small></div><button className="icon-btn mobile-close" onClick={() => setMobileNav(false)}><X size={18}/></button></div>
      <div className="workspace"><span className="status-dot"/> Boutique principale <span className="chevron">⌄</span></div>
      <p className="nav-label">MENU PRINCIPAL</p>
      <nav>{nav.map(([id, label, Icon]) => <button key={id} className={`nav-item ${page === id ? 'active' : ''}`} onClick={() => {setPage(id);setMobileNav(false)}}><Icon size={18}/><span>{label}</span>{id === 'orders' && orders.length > 0 && <em>{orders.length}</em>}</button>)}</nav>
      <div className="sidebar-bottom"><div className="help-card"><div className="help-icon"><MessageCircle size={18}/></div><b>Besoin d'aide ?</b><p>Consultez la documentation de votre espace.</p><a href="http://127.0.0.1:8000/docs" target="_blank" rel="noreferrer">Documentation API <ExternalLink size={12}/></a></div><div className="profile"><div className="avatar">A</div><div><b>Administrateur</b><small>Compte boutique</small></div><span>•••</span></div></div>
    </aside>

    <main className="main">
      <header className="topbar"><button className="icon-btn mobile-menu" onClick={() => setMobileNav(true)}><Menu/></button><div className="breadcrumb">Ndonga_buzness <span>/</span> <b>{nav.find(n => n[0] === page)?.[1] || 'Vue générale'}</b></div><div className="top-actions"><span className="demo-pill"><i/> Mode local</span><button className="icon-btn" onClick={load} title="Actualiser"><RefreshCw size={17}/></button><div className="top-avatar">A</div></div></header>
      <section className="content">
        <div className="page-heading"><div><p className="eyebrow">ESPACE DE GESTION</p><h1>{page === 'dashboard' ? 'Vue générale' : nav.find(n => n[0] === page)?.[1]}</h1><p className="subheading">{page === 'dashboard' ? 'Suivez l’activité de votre boutique en un seul endroit.' : 'Gérez votre activité commerciale Ndonga_buzness.'}</p></div>{page === 'products' && <button className="primary-btn" onClick={() => setShowForm(true)}><Plus size={17}/> Ajouter un produit</button>}</div>

        {error && <div className="alert"><span>{error}</span><button onClick={() => setError('')}><X size={16}/></button></div>}
        {loading && <div className="loading">Chargement des données…</div>}

        {!loading && page === 'dashboard' && <>
          <div className="welcome-panel"><div><span className="welcome-tag">VOTRE ACTIVITÉ</span><h2>Bonjour, Administrateur <span>👋</span></h2><p>Voici le résumé de votre boutique aujourd’hui.</p></div><div className="welcome-art">N<span>+</span></div></div>
          <div className="stats-grid">
            <Stat title="Produits actifs" value={stats?.products ?? 0} icon={<Package/>} note="Dans votre catalogue"/>
            <Stat title="Commandes reçues" value={stats?.orders ?? 0} icon={<ShoppingBag/>} note="Toutes périodes"/>
            <Stat title="Clients" value={stats?.customers ?? 0} icon={<Users/>} note="Clients enregistrés"/>
            <Stat title="Chiffre d’affaires" value={money(stats?.revenue)} icon={<span className="fcfa">F</span>} note="Hors commandes annulées"/>
          </div>
          <div className="section-grid"><div className="panel"><div className="panel-head"><div><h3>Commandes récentes</h3><p>Dernières commandes enregistrées</p></div><button className="text-btn" onClick={() => setPage('orders')}>Tout voir →</button></div><OrdersTable orders={orders.slice(0,5)} onStatus={changeStatus}/></div><div className="panel quick-panel"><div className="panel-head"><div><h3>Actions rapides</h3><p>Accès direct aux outils</p></div></div><button onClick={() => {setPage('products');setShowForm(true)}}><span className="quick-icon green"><Plus/></span><span><b>Ajouter un produit</b><small>Enrichir votre catalogue</small></span><b>→</b></button><button onClick={() => setPage('orders')}><span className="quick-icon blue"><ShoppingBag/></span><span><b>Gérer les commandes</b><small>Consulter les achats clients</small></span><b>→</b></button><button onClick={() => setPage('messages')}><span className="quick-icon gold"><MessageCircle/></span><span><b>Configurer WhatsApp</b><small>Préparer la messagerie</small></span><b>→</b></button></div></div>
          <div className="notice"><MessageCircle size={18}/><div><b>Connexion WhatsApp à configurer</b><p>Le tableau de bord fonctionne en mode local. Ajoutez vos identifiants Meta dans le fichier backend/.env avant de configurer le webhook public.</p></div><button onClick={() => setPage('messages')}>Voir les étapes</button></div>
        </>}

        {!loading && page === 'products' && <div className="panel"><div className="toolbar"><div><h3>Catalogue des produits</h3><p>{products.length} produit(s) enregistré(s)</p></div><div className="searchbox"><Search size={16}/><input placeholder="Rechercher un produit…" value={search} onChange={e=>setSearch(e.target.value)}/></div></div><div className="table-wrap"><table><thead><tr><th>PRODUIT</th><th>CATÉGORIE</th><th>PRIX</th><th>STOCK</th><th>ÉTAT</th></tr></thead><tbody>{filteredProducts.map(p=><tr key={p.id}><td><b>{p.name}</b><small className="cell-sub">{p.description}</small></td><td>{p.category}</td><td className="price">{money(p.price)}</td><td>{p.stock}</td><td><span className={`status ${p.active?'ok':'off'}`}>{p.active?'Actif':'Inactif'}</span></td></tr>)}</tbody></table>{filteredProducts.length===0 && <Empty text="Aucun produit trouvé."/>}</div></div>}

        {!loading && page === 'orders' && <div className="panel"><div className="toolbar"><div><h3>Toutes les commandes</h3><p>{orders.length} commande(s) enregistrée(s)</p></div><div className="searchbox"><Search size={16}/><input placeholder="Rechercher une commande…" value={search} onChange={e=>setSearch(e.target.value)}/></div></div><OrdersTable orders={filteredOrders} onStatus={changeStatus}/></div>}

        {!loading && page === 'customers' && <div className="panel"><div className="panel-head"><div><h3>Clients enregistrés</h3><p>Les clients sont créés automatiquement à la première commande.</p></div></div><div className="table-wrap"><table><thead><tr><th>NOM</th><th>TÉLÉPHONE</th><th>COMMANDES</th></tr></thead><tbody>{[...new Map(orders.map(o=>[o.phone,o])).values()].map(o=><tr key={o.phone}><td><b>{o.customer_name}</b></td><td>{o.phone}</td><td>{orders.filter(x=>x.phone===o.phone).length}</td></tr>)}</tbody></table></div></div>}

        {!loading && page === 'assistant' && <div className="assistant-layout"><div className="panel assistant-panel"><div className="panel-head"><div><h3>Simulateur de conversation</h3><p>Testez les réponses du bot avec les produits et stocks de votre base de données.</p></div><span className="status ok">Simulation locale</span></div><div className="chat-window">{chatMessages.map((m,i)=><div key={i} className={`chat-line ${m.role}`}><div className="chat-bubble">{m.text.split("\n").map((line,j)=><span key={j}>{line}{j < m.text.split("\n").length-1 && <br/>}</span>)}</div></div>)}{chatBusy && <div className="chat-line bot"><div className="chat-bubble muted">Le bot réfléchit…</div></div>}</div><form className="chat-compose" onSubmit={sendChat}><input value={chatInput} onChange={e=>setChatInput(e.target.value)} placeholder="Écrivez un message…"/><button className="primary-btn" disabled={chatBusy || !chatInput.trim()}>Envoyer</button></form><div className="chat-hints"><button onClick={()=>setChatInput('MENU')} type="button">MENU</button><button onClick={()=>setChatInput('PRODUITS')} type="button">PRODUITS</button><button onClick={()=>setChatInput('COMMANDER')} type="button">COMMANDER</button></div></div><div className="panel assistant-info"><h3>Scénarios à tester</h3><ol><li>Écrivez <b>Bonjour</b> pour afficher le menu.</li><li>Écrivez <b>Produits</b> pour consulter le catalogue.</li><li>Écrivez <b>Commander</b>, puis suivez les questions du bot.</li><li>Terminez avec un nom et un numéro de téléphone de test.</li></ol><div className="notice"><div><b>Important</b><p>Cette simulation crée de vraies commandes dans la base locale et diminue le stock. Utilisez des données de test.</p></div></div></div></div>}

        {!loading && page === 'messages' && <div className="panel whatsapp-panel"><div className="wa-heading"><div className="wa-logo"><MessageCircle/></div><div><h3>WhatsApp Cloud API</h3><p>Préparation de la connexion officielle Meta</p></div><span className="status off">Non connecté</span></div><div className="steps"><div><b>01</b><span><strong>Créer une application Meta</strong><small>Depuis Meta for Developers, créez une application de type Business.</small><a href="https://developers.facebook.com/" target="_blank" rel="noreferrer">Ouvrir Meta for Developers ↗</a></span></div><div><b>02</b><span><strong>Activer WhatsApp</strong><small>Ajoutez le produit WhatsApp et utilisez d'abord le numéro de test fourni.</small></span></div><div><b>03</b><span><strong>Configurer les variables secrètes</strong><small>Renseignez WHATSAPP_TOKEN, WHATSAPP_PHONE_NUMBER_ID et WHATSAPP_VERIFY_TOKEN dans backend/.env.</small></span></div><div><b>04</b><span><strong>Publier le webhook HTTPS</strong><small>Le webhook local doit être exposé par une URL HTTPS publique pour recevoir les événements Meta.</small></span></div></div><div className="notice"><b>Mode démonstration</b><p>Les menus, produits et commandes sont gérés localement. Aucun message n'est envoyé à WhatsApp dans cette version.</p></div></div>}

        {showForm && <div className="modal-backdrop" onMouseDown={e=>{if(e.target===e.currentTarget)setShowForm(false)}}><form className="modal" onSubmit={saveProduct}><div className="modal-head"><div><h2>Nouveau produit</h2><p>Ajoutez un article au catalogue.</p></div><button type="button" className="icon-btn" onClick={()=>setShowForm(false)}><X/></button></div><label>Nom du produit<input required minLength="2" value={form.name} onChange={e=>setForm({...form,name:e.target.value})}/></label><label>Catégorie<input value={form.category} onChange={e=>setForm({...form,category:e.target.value})}/></label><label>Description<textarea value={form.description} onChange={e=>setForm({...form,description:e.target.value})}/></label><div className="form-row"><label>Prix (FCFA)<input required type="number" min="0" value={form.price} onChange={e=>setForm({...form,price:e.target.value})}/></label><label>Stock<input required type="number" min="0" value={form.stock} onChange={e=>setForm({...form,stock:e.target.value})}/></label></div><button className="primary-btn full" type="submit">Enregistrer le produit</button></form></div>}
      </section>
      <footer>© {new Date().getFullYear()} Ndonga_buzness <span>•</span> Version initiale 1.0.0</footer>
    </main>
  </div>
}

function Stat({title,value,icon,note}) { return <div className="stat-card"><div className="stat-top"><span>{title}</span><div>{icon}</div></div><strong>{value}</strong><small>{note}</small></div> }
function Empty({text}) { return <div className="empty">{text}</div> }
function OrdersTable({orders,onStatus}) {
  if (!orders.length) return <Empty text="Aucune commande pour le moment. Les commandes apparaîtront ici."/>
  return <div className="table-wrap"><table><thead><tr><th>COMMANDE</th><th>CLIENT</th><th>TOTAL</th><th>STATUT</th><th>MISE À JOUR</th></tr></thead><tbody>{orders.map(o=><tr key={o.id}><td><b>{o.order_number}</b><small className="cell-sub">{new Date(o.created_at).toLocaleDateString('fr-FR')}</small></td><td>{o.customer_name}<small className="cell-sub">{o.phone}</small></td><td className="price">{money(o.total)}</td><td><span className={`status ${o.status==='Terminée'?'ok':o.status==='Annulée'?'off':'pending'}`}>{o.status}</span></td><td><select value={o.status} onChange={e=>onStatus(o,e.target.value)}>{['En attente','Confirmée','En préparation','Expédiée','Terminée','Annulée'].map(s=><option key={s}>{s}</option>)}</select></td></tr>)}</tbody></table></div>
}
