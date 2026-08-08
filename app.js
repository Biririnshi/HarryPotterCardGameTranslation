let cards = [];

async function i() {
  cards = await fetch('translatedCards.json').then(r => r.json());
  type.innerHTML = '<option value="">All</option>' + [...new Set(cards.map(c => c.cardTypeName || ''))].filter(Boolean).map(t => `<option>${t}</option>`).join('');
  r();
  q.oninput = r;
  type.onchange = r;
}

function r() {
  grid.innerHTML = '';
  
  cards
    .filter((c) => (!type.value || (c.cardTypeName || '') == type.value) && ((c.cardName || '').toLowerCase().includes(q.value.toLowerCase())))
    .forEach((c) => {
      let d = document.createElement('div');
      d.className = 'card';
      d.innerHTML = `<img src="translated_proxies/${c.cardNumber}.png"><br>${c.cardNumber} </br> ${c.cardName}`;
      
      d.onclick = () => {
        detail.innerHTML =`
            <div class="card-info">

                <div class="card-image">
                    <img src="translated_proxies/${c.cardNumber}.png">
                </div>

                <div class="card-details">
                    <button onclick="dlg.close()">back</button>
                   <div class="card-header">
                        <strong>No.</strong>${c.cardNumber}
                        <h2>${c.cardName}</h2>
                        <span class="rarity rarity-${c.rarity.value}">
                            ${c.rarity.value}
                        </span>
                    </div>

                    <div class="stats">
                        <div><strong>Type</strong><span>${c.cardType.value}</span></div>
                        <div><strong>Cost</strong><span>${c.cost}</span></div>
                        <div><strong>MP</strong><span>${c.mp ?? "-"}</span></div>
                        <div><strong>AP / DP</strong><span>${c.ap ?? "-"} / ${c.dp ?? "-"}</span></div>
                        
                    </div>

                    <div class="tags">
                        <strong>${c.tags[0]?.value ?? "-"} / ${c.tags[1]?.value ?? "-"} / ${c.tags[2]?.value ?? "-"} / ${c.tags[3]?.value ?? "-"} </br></strong>
                    </div>

                    <div class="effect">
                        <p>${c.text.replace(/\\N/g, "<br>")}</p>
                    </div>

                </div>

            </div>

        `;
        dlg.showModal();
        
      };
        
        
      
      grid.appendChild(d);
    });
}

i();
