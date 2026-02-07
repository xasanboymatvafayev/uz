const tg = window.Telegram?.WebApp;
if (tg) tg.expand();

const API_BASE = (tg?.initDataUnsafe?.start_param && tg.initDataUnsafe.start_param) ? "" : ""; // not used
const apiBaseUrl = (new URLSearchParams(location.search).get("api")) || "http://localhost:8001";

let categories = [];
let foods = [];
let activeCategoryId = null;
let activeSort = "";
let searchValue = "";

let cart = {}; // food_id -> {food, qty}
let geo = { lat: null, lng: null };
let promo = { code: "", valid: false, discount_percent: 0 };

const $ = (id) => document.getElementById(id);

function money(x){ return `${x} сум`; }

async function apiGet(path){
  const initData = tg?.initData || "";
  const res = await fetch(`${apiBaseUrl}${path}`, {
    headers: {
      "X-Telegram-InitData": initData
    }
  });
  if(!res.ok) throw new Error("API error");
  return res.json();
}

function setModal(id, show){
  const el = $(id);
  el.classList.toggle("show", !!show);
}

function cartTotal(){
  let sum = 0;
  for(const k in cart){
    sum += cart[k].food.price * cart[k].qty;
  }
  // apply promo
  if (promo.valid && promo.discount_percent > 0){
    sum = sum - Math.floor(sum * promo.discount_percent / 100);
  }
  return sum;
}

function cartCount(){
  let c = 0;
  for(const k in cart) c += cart[k].qty;
  return c;
}

function renderCategories(){
  const wrap = $("categoryChips");
  wrap.innerHTML = "";

  const all = document.createElement("div");
  all.className = "chip " + (activeCategoryId === null ? "active": "");
  all.textContent = "All";
  all.onclick = ()=>{ activeCategoryId=null; loadFoods(); };
  wrap.appendChild(all);

  const fixed = ["Lavash","Burger","Xaggi","Shaurma","Hotdog","Combo","Sneki","Sous","Napitki"];
  // show fixed first if exist
  const byName = new Map(categories.map(c=>[c.name.toLowerCase(), c]));
  fixed.forEach(name=>{
    const c = byName.get(name.toLowerCase());
    if (c) wrap.appendChild(makeChip(c));
  });

  categories.forEach(c=>{
    if (fixed.map(x=>x.toLowerCase()).includes(c.name.toLowerCase())) return;
    wrap.appendChild(makeChip(c));
  });

  function makeChip(c){
    const el = document.createElement("div");
    el.className = "chip " + (activeCategoryId === c.id ? "active": "");
    el.textContent = c.name;
    el.onclick = ()=>{ activeCategoryId=c.id; loadFoods(); };
    return el;
  }
}

function renderFoods(){
  const grid = $("foodGrid");
  grid.innerHTML = "";
  foods.forEach(f=>{
    const card = document.createElement("div");
    card.className = "card";
    const img = document.createElement("div");
    img.className = "cardImg";
    img.textContent = f.image_url ? "IMG" : "FIESTA";
    const body = document.createElement("div");
    body.className = "cardBody";

    const t = document.createElement("div");
    t.className = "cardTitle";
    t.textContent = f.name;

    const d = document.createElement("div");
    d.className = "cardDesc";
    d.textContent = f.description || "";

    const meta = document.createElement("div");
    meta.className = "meta";
    meta.innerHTML = `<div>⭐ ${f.rating}</div><div class="price">${money(f.price)}</div>`;

    const btn = document.createElement("button");
    btn.className = "btn primary";
    btn.textContent = "Add";
    btn.onclick = ()=>addToCart(f);

    body.appendChild(t);
    body.appendChild(d);
    body.appendChild(meta);
    body.appendChild(btn);

    card.appendChild(img);
    card.appendChild(body);
    grid.appendChild(card);
  });
}

function addToCart(food){
  if(!cart[food.id]) cart[food.id] = { food, qty: 0 };
  cart[food.id].qty += 1;
  renderCartFab();
}

function removeFromCart(foodId){
  if(!cart[foodId]) return;
  cart[foodId].qty -= 1;
  if(cart[foodId].qty <= 0) delete cart[foodId];
  renderCartFab();
  renderCartModal();
}

function addQty(foodId){
  cart[foodId].qty += 1;
  renderCartFab();
  renderCartModal();
}

function renderCartFab(){
  $("cartSub").textContent = `${cartCount()} items`;
  $("cartTotal").textContent = money(cartTotal());
}

function renderCartModal(){
  const box = $("cartItems");
  box.innerHTML = "";

  const keys = Object.keys(cart);
  keys.forEach(k=>{
    const it = cart[k];
    const row = document.createElement("div");
    row.className = "cartItem";
    row.innerHTML = `
      <div>
        <div class="ciTitle">${it.food.name}</div>
        <div class="ciMeta">${money(it.food.price)} • x${it.qty}</div>
      </div>
      <div class="qtyBox">
        <button class="btn ghost qtyBtn">−</button>
        <div style="min-width:20px;text-align:center;font-weight:900">${it.qty}</div>
        <button class="btn ghost qtyBtn">+</button>
      </div>
    `;
    const minus = row.querySelectorAll("button")[0];
    const plus = row.querySelectorAll("button")[1];
    minus.onclick = ()=>removeFromCart(it.food.id);
    plus.onclick = ()=>addQty(it.food.id);
    box.appendChild(row);
  });

  const total = cartTotal();
  $("checkoutTotal").textContent = money(total);
  $("checkoutBtn").disabled = !(total >= 50000 && geo.lat !== null && geo.lng !== null && keys.length > 0);
}

async function loadCategories(){
  categories = await apiGet("/api/categories");
  renderCategories();
}

async function loadFoods(){
  const params = new URLSearchParams();
  if(activeCategoryId) params.set("category_id", activeCategoryId);
  if(activeSort) params.set("sort", activeSort);
  if(searchValue) params.set("search", searchValue);

  foods = await apiGet("/api/foods?" + params.toString());
  renderCategories();
  renderFoods();
}

function initDefaults(){
  const u = tg?.initDataUnsafe?.user;
  if(u){
    $("nameInput").value = u.first_name + (u.last_name ? (" " + u.last_name) : "");
  }
  renderCartFab();
  renderCartModal();
}

async function promoCheck(){
  const code = ($("promoInput").value || "").trim();
  if(!code){
    promo = { code:"", valid:false, discount_percent:0 };
    $("promoHint").textContent = "";
    renderCartModal();
    return;
  }
  const res = await apiGet("/api/promo/validate?code=" + encodeURIComponent(code));
  if(res.valid){
    promo = { code, valid:true, discount_percent: res.discount_percent || 0 };
    $("promoHint").textContent = `✅ Скидка: ${promo.discount_percent}%`;
  }else{
    promo = { code, valid:false, discount_percent:0 };
    $("promoHint").textContent = "❌ Промокод недействителен";
  }
  renderCartModal();
}

function askGeo(){
  if(!navigator.geolocation){
    $("geoHint").textContent = "Геолокация недоступна";
    return;
  }
  $("geoHint").textContent = "Определяем локацию...";
  navigator.geolocation.getCurrentPosition(
    (pos)=>{
      geo.lat = pos.coords.latitude;
      geo.lng = pos.coords.longitude;
      $("geoHint").textContent = `✅ ${geo.lat.toFixed(6)}, ${geo.lng.toFixed(6)}`;
      renderCartModal();
    },
    ()=>{
      $("geoHint").textContent = "❌ Не удалось получить локацию";
      renderCartModal();
    },
    { enableHighAccuracy:true, timeout:15000 }
  );
}

function checkout(){
  const items = Object.values(cart).map(it=>({
    food_id: it.food.id,
    name: it.food.name,
    qty: it.qty,
    price: it.food.price
  }));
  const total = cartTotal();

  const payload = {
    type: "order_create",
    items,
    total,
    promo: promo.valid ? promo.code : "",
    customer_name: $("nameInput").value || "",
    phone: $("phoneInput").value || "",
    comment: $("commentInput").value || "",
    location: { lat: geo.lat, lng: geo.lng },
    created_at_client: new Date().toISOString()
  };

  tg.sendData(JSON.stringify(payload));
  tg.close();
}

function wire(){
  $("cartFab").onclick = ()=>{ setModal("cartModal", true); renderCartModal(); };
  $("closeCart").onclick = ()=>setModal("cartModal", false);

  $("filterBtn").onclick = ()=>setModal("filterModal", true);
  $("closeFilter").onclick = ()=>setModal("filterModal", false);

  document.querySelectorAll(".filter").forEach(btn=>{
    btn.onclick = ()=>{
      activeSort = btn.dataset.sort || "";
      setModal("filterModal", false);
      loadFoods();
    };
  });

  $("searchInput").addEventListener("input", (e)=>{
    searchValue = e.target.value.trim();
    loadFoods();
  });

  $("geoBtn").onclick = askGeo;
  $("promoCheckBtn").onclick = promoCheck;
  $("checkoutBtn").onclick = checkout;

  // close on backdrop
  ["cartModal","filterModal"].forEach(id=>{
    $(id).addEventListener("click", (e)=>{
      if(e.target.id === id) setModal(id, false);
    });
  });
}

(async function bootstrap(){
  wire();
  initDefaults();
  await loadCategories();
  await loadFoods();
})();
