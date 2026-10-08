const DATA = /*__DATA__*/null;

const esc = s => String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
const fmtM = v => v>=1000 ? '$'+(v/1000).toFixed(1)+'B' : '$'+Math.round(v)+'M';
const $ = id => document.getElementById(id);

/* ================= Timelines — horizontal navigation (markup is pre-rendered by the build) ================= */
function initTimelines(){
  const reduce=window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  document.querySelectorAll('[data-tl]').forEach(tl=>{
    const vp=tl.querySelector('.tl__viewport'), prev=tl.querySelector('[data-dir="-1"]'), next=tl.querySelector('[data-dir="1"]');
    const prog=tl.querySelector('.tl__progress'), track=prog.querySelector('.tl__bar-track'), thumb=prog.querySelector('.tl__bar-thumb'), first=tl.querySelector('.tyear');
    const max=()=>Math.max(vp.scrollWidth-vp.clientWidth,0);
    const colW=()=>first.getBoundingClientRect().width;
    const step=()=>colW()*Math.max(1,Math.floor(vp.clientWidth/colW())-1);
    const behavior=()=>reduce?'auto':'smooth';
    const update=()=>{
      const m=max(), x=vp.scrollLeft, ratio=m?vp.clientWidth/vp.scrollWidth:1;
      tl.classList.toggle('is-start',x<=2); tl.classList.toggle('is-end',x>=m-2);
      prev.disabled=x<=2; next.disabled=x>=m-2;
      const trackW=track.clientWidth, thumbW=Math.max(trackW*ratio,36);
      thumb.style.width=thumbW+'px'; thumb.style.transform='translateX('+(m?(x/m)*(trackW-thumbW):0)+'px)';
      prog.setAttribute('aria-valuenow',m?Math.round(x/m*100):100);
    };
    prev.addEventListener('click',()=>vp.scrollBy({left:-step(),behavior:behavior()}));
    next.addEventListener('click',()=>vp.scrollBy({left:step(),behavior:behavior()}));
    vp.addEventListener('scroll',update,{passive:true});
    window.addEventListener('resize',update);
    // drag / click on the progress bar to scrub the timeline
    let dragging=false;
    const scrub=e=>{ const r=track.getBoundingClientRect(); vp.scrollLeft=Math.min(1,Math.max(0,(e.clientX-r.left)/r.width))*max(); };
    prog.addEventListener('pointerdown',e=>{ dragging=true; prog.setPointerCapture(e.pointerId); vp.style.scrollSnapType='none'; scrub(e); });
    prog.addEventListener('pointermove',e=>{ if(dragging) scrub(e); });
    const end=()=>{ dragging=false; vp.style.scrollSnapType=''; };
    prog.addEventListener('pointerup',end); prog.addEventListener('pointercancel',end);
    update();
  });
}

/* ================= Aurora scale (one square = one truck, drawn to scale) ================= */
function renderScale(){
  const c=3.1, cols=200, rows=150, x0=6, gy=34;
  const gw=cols*c, gh=rows*c, W=Math.round(gw+12);
  const z=15, zc=20, zr=10, zy=Math.round(gy+gh+74), zw=zc*z, zh=zr*z, H=zy+zh+24;
  let s=`<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="Unit chart drawn to scale: one square is one truck. About 20 trucks operate today; Aurora targets more than 200 by year-end 2026 and 30,000 by 2030.">`;
  s+=`<defs><pattern id="u30k" width="${c}" height="${c}" patternUnits="userSpaceOnUse" x="${x0}" y="${gy}"><rect width="2.2" height="2.2" fill="#8BCDFF" opacity=".24"/></pattern></defs>`;
  s+=`<text x="${x0}" y="20" style="font-size:12px;font-weight:700;letter-spacing:.14em;fill:#89A1B4;">ONE SQUARE = ONE TRUCK · 30,000 SQUARES</text>`;
  s+=`<rect x="${x0}" y="${gy}" width="${gw}" height="${gh}" fill="url(#u30k)" stroke="#8BCDFF" stroke-opacity=".5" stroke-dasharray="5 4"/>`;
  s+=`<rect x="${x0}" y="${gy}" width="${20*c}" height="${10*c}" fill="none" stroke="#DCE5ED" stroke-width="1.2" stroke-dasharray="3 2"/>`;
  s+=`<rect x="${x0}" y="${gy}" width="${20*c}" height="${c}" fill="#8BCDFF"/>`;
  s+=`<text x="${W-14}" y="${gy+gh-16}" text-anchor="end" style="font-size:30px;font-weight:700;letter-spacing:-.5px;fill:#8BCDFF;paint-order:stroke;stroke:#292A4E;stroke-width:7px;">30,000 · 2030 target</text>`;
  // funnel to zoom
  s+=`<path d="M${x0},${gy+10*c} L${x0},${zy-26} M${x0+20*c},${gy+10*c} L${x0+zw},${zy-26}" stroke="#5A7A94" stroke-width="1.2" stroke-dasharray="2 4" fill="none"/>`;
  s+=`<text x="${x0}" y="${zy-8}" style="font-size:12px;font-weight:700;letter-spacing:.14em;fill:#89A1B4;">ZOOM · THE FIRST 200 SQUARES</text>`;
  for(let r=0;r<zr;r++)for(let k=0;k<zc;k++){
    const x=x0+k*z, y=zy+r*z, act=r===0;
    s+= act ? `<rect x="${x}" y="${y}" width="${z-3}" height="${z-3}" rx="2" fill="#8BCDFF"/>`
            : `<rect x="${x+.5}" y="${y+.5}" width="${z-4}" height="${z-4}" rx="2" fill="rgba(220,229,237,.06)" stroke="#DCE5ED" stroke-opacity=".6" stroke-dasharray="3 2"/>`;
  }
  const lx=x0+zw+16;
  s+=`<text x="${lx}" y="${zy+11}" style="font-size:17px;font-weight:700;fill:#8BCDFF;">~20 today</text><text x="${lx}" y="${zy+29}" style="font-size:12.5px;font-weight:600;fill:#DCE5ED;">Actual · in operation</text>`;
  s+=`<text x="${lx}" y="${zy+z*4+8}" style="font-size:17px;font-weight:700;fill:#FFFFFF;">&gt;200</text><text x="${lx}" y="${zy+z*4+26}" style="font-size:12.5px;font-weight:600;fill:#DCE5ED;">Target · year-end 2026</text>`;
  s+='</svg>';
  $('scale-viz').innerHTML=s;
}

/* ================= V5 — capital ================= */
function renderCapital(){
  const F=DATA.funding, av=F.totalAV, ev=F.totalEV, tot=F.total, pAV=av/tot*100;
  $('split').innerHTML=
    `<div class="split-bar__total">Disclosed capital 2021–2026: <b>${fmtM(tot)}</b></div>`+
    `<div class="split-bar__bar" role="img" aria-label="Autonomous trucks ${fmtM(av)}, ${Math.round(pAV)} percent; electric trucks ${fmtM(ev)}, ${Math.round(100-pAV)} percent">`+
    `<div class="split-bar__seg" style="width:${pAV}%;background:var(--col-av);"><b>${fmtM(av)}</b><small>Autonomous · ${Math.round(pAV)}%</small></div>`+
    `<div class="split-bar__seg split-bar__seg--ev" style="width:${100-pAV}%;background:var(--col-ev);"><b>${fmtM(ev)}</b><small>Electric · ${Math.round(100-pAV)}%</small></div></div>`;
  const ys=F.years, maxV=4400, H=250;
  const segs=[['avPub','var(--col-av)','AV SPACs & public offerings'],['avVen','#528DBC','AV venture'],['evVen','var(--col-ev)','EV venture']];
  let h='<div class="ybars__plot" role="img" aria-label="'+ys.map(d=>`${d.y}: ${d.total?fmtM(d.total):'no disclosed deals'}`).join('; ')+'">';
  ys.forEach((d,i)=>{
    h+='<div class="ybar">';
    if(d.total>0){
      h+=`<div class="ybar__tot${d.y===2021?' ybar__tot--hi':''}">${fmtM(d.total)}</div><div class="ybar__stack" style="--i:${i};height:${d.total/maxV*H}px">`;
      segs.forEach(([k,col,lab])=>{ const v=d[k]; if(!v) return; const px=v/maxV*H; h+=`<div class="ybar__seg" title="${lab}: ${fmtM(v)}" style="height:${px}px;background:${col};">${px>=56?fmtM(v):''}</div>`; });
      h+='</div>';
    } else h+='<div class="ybar__none">No disclosed deals</div>';
    h+='</div>';
  });
  h+='</div>';
  const later=ys.filter(d=>d.y>2021).reduce((s,d)=>s+d.total,0), y21=ys.find(d=>d.y===2021);
  h+=`<div class="ybars__x">`+ys.map(d=>`<span class="${d.y===2021?'hi':''}">${d.y}${d.y===2026?' YTD':''}</span>`).join('')+'</div>';
  h+=`<div class="ybars__sum"><b>2022–2026 combined: ${fmtM(later)}</b> across five years, against ${fmtM(y21.total)} in 2021 alone</div>`;
  h=`<div class="ybars__note"><b>2021 listing wave:</b> TuSimple IPO, Aurora and Embark SPACs — ${fmtM(y21.avPub)} of the year's ${fmtM(y21.total)}</div>`+h;
  $('ybars').innerHTML=h;
}

/* ================= V3 — ambition vs outcome ================= */
const AO = [
  {co:'Nikola',kind:'Peak market value · 2020',amb:'~$26–30B',st:'closed',stL:'Chapter 11',out:'Chapter 11, 2025',note:'About $47M cash at filing'},
  {co:'Embark',kind:'SPAC valuation · 2021',amb:'$5.2B',st:'closed',stL:'Sold',outKind:'Acquisition price',out:'Sold for ~$71M, Aug 2023',note:'Acquired by Applied Intuition — about 1% of the SPAC valuation',contrast:[5200,71]},
  {co:'TuSimple',kind:'IPO proceeds · April 2021',amb:'$1.35B',st:'other',stL:'Exited US',out:'US wind-down, Dec 2023',note:'Exit from the US market'},
  {co:'Volta Trucks',kind:'Capital raised in total',amb:'$390.9M',st:'closed',stL:'Bankrupt',out:'Bankruptcy, Oct 2023',note:'Assets bought by Luxor Capital, its largest creditor'},
  {co:'Windrose',kind:'Series B raised · April 2024',amb:'$110M',st:'other',stL:'Distress reported',out:'Distress reported, Jul 2026',note:'WSJ: missing paychecks and a truck'}
];
function renderExits(){
  const byCo=new Map(DATA.exits.map(d=>[d.co,d]));
  $('ao').innerHTML=AO.map(a=>{
    const d=byCo.get(a.co); if(!d) throw new Error('exit row missing: '+a.co);
    const contrast=a.contrast?`<div class="contrast" role="img" aria-label="$5.2 billion SPAC valuation versus $71 million sale price"><div style="width:100%;background:var(--col-av);opacity:.85"></div><div style="width:${Math.max(a.contrast[1]/a.contrast[0]*100,0.8)}%;background:var(--col-fail)"></div></div>`:'';
    return `<div class="ao__row"><div class="ao__co">${esc(a.co)}<small><span class="chip chip--${d.seg.toLowerCase()}">${d.seg}</span>${esc(d.region)}</small></div>`+
      `<div class="ao__amb"><div class="ao__kind">${a.kind}</div><b>${a.amb}</b>${contrast}</div><div class="ao__arrow" aria-hidden="true">→</div>`+
      `<div class="ao__out"><span class="st st--${a.st}">${a.stL}</span>${a.outKind?`<div class="ao__kind">${a.outKind}</div>`:''}<b>${a.out}</b><div class="ao__note">${a.note}</div></div></div>`;
  }).join('');
  const main=new Set(AO.map(a=>a.co));
  $('ao-minor').innerHTML=DATA.exits.filter(d=>!main.has(d.co)).map(d=>
    `<li><div><b>${esc(d.co)}</b> <span class="chip chip--${d.seg.toLowerCase()}">${d.seg}</span></div><span><b>${d.y} · ${esc(d.out)}</b> — ${esc(d.ctx)}</span></li>`).join('');
}

/* ================= V4 — map ================= */
const MAP_POS={'United States':[-98,39],'Canada':[-112,61],'China':[104,34],'India':[79,21],'Europe':[10,50],'Japan & Korea':[134,37]};
function renderMap(){
  const w=960,h=470;
  const proj=d3.geoNaturalEarth1().fitExtent([[10,10],[w-10,h-10]],{type:'MultiPoint',coordinates:[[-128,66],[150,66],[-128,8],[150,8]]});
  const path=d3.geoPath(proj);
  const colors={EV:'#3EC6C6',AV:'#8BCDFF',BOTH:'#B79CFF'};
  const pie=d3.pie().sort(null).value(d=>d.v);
  let s=`<svg viewBox="0 0 ${w} ${h}" class="map-svg" role="img" aria-label="${DATA.map.map(m=>`${m.region}: ${m.EV} EV, ${m.AV} AV${m.BOTH?`, ${m.BOTH} both`:''}`).join('; ')}. Circle size shows database coverage, not market size."><rect class="sphere" width="${w}" height="${h}" rx="12"/><g id="land"></g><g>`;
  DATA.map.forEach(m=>{
    const tot=m.EV+m.AV+m.BOTH, r=12+4.6*Math.sqrt(tot);
    const [x,y]=proj(MAP_POS[m.region]);
    const arc=d3.arc().innerRadius(r*0.5).outerRadius(r);
    s+=`<g transform="translate(${x},${y})"><circle r="${r+3}" fill="#221E41" opacity=".75"/>`;
    pie([{k:'EV',v:m.EV},{k:'AV',v:m.AV},{k:'BOTH',v:m.BOTH}].filter(p=>p.v>0)).forEach(p=>{ s+=`<path d="${arc(p)}" fill="${colors[p.data.k]}" stroke="#221E41" stroke-width="1.5"/>`; });
    s+=`<text y="${tot>=10?7:6}" text-anchor="middle" style="font-size:${tot>=10?20:16}px;font-weight:700;fill:#FFFFFF;">${tot}</text>`;
    s+=`<text class="map-lbl" y="${r+20}" text-anchor="middle">${m.region}</text></g>`;
  });
  s+='</g></svg>';
  $('map').innerHTML=s;
  const drawLand=topo=>{ const land=topojson.feature(topo,topo.objects.countries); $('land').innerHTML=land.features.map(f=>`<path class="land" d="${path(f)}"/>`).join(''); };
  if(window.WORLD_110M) drawLand(window.WORLD_110M);   // local copy: deploy/countries-110m.js
  else fetch('https://cdn.jsdelivr.net/npm/world-atlas@2.0.2/countries-110m.json').then(r=>r.json()).then(drawLand).catch(()=>{});
  const order=['United States','China','Europe','India','Canada','Japan & Korea'];
  const feat={'United States':'Aurora, Kodiak, Gatik, Waabi, Plus · Tesla, Nikola','China':'Pony.ai, TrunkTech, Inceptio · BYD, DeepWay, Sany','Europe':'Einride · Volvo, Daimler, MAN/Traton, Scania','India':'Delta X, EVage, Euler, Etrio','Canada':'Lion Electric, Edison Motors','Japan & Korea':'Robotruck (JP), Rideflux (KR)'};
  $('region-grid').innerHTML=order.map(k=>{
    const m=DATA.map.find(x=>x.region===k); if(!m) return '';
    return `<div class="region-card"><div class="region-card__name">${k}</div><div class="region-card__nums"><span><b style="color:var(--col-ev)">${m.EV}</b><small>EV</small></span><span><b style="color:var(--col-av)">${m.AV}</b><small>AV</small></span>${m.BOTH?`<span><b style="color:var(--col-cap)">${m.BOTH}</b><small>both</small></span>`:''}</div><div class="region-card__names">${feat[k]}</div></div>`;
  }).join('');
}

/* ================= V6 — ecosystem ================= */
const NODE_COL={oem:'#FFFFFF',dev:'#8BCDFF',cust:'#FFB935',tech:'#5A7A94'};
const TYPE_LAB={oem:'OEM',dev:'Developer / operator',cust:'Shipper / carrier',tech:'Supplier'};
function ecosystem(){
  const nodes=DATA.alli.nodes.map(d=>({...d})), links=DATA.alli.links.map(d=>({...d}));
  const byId=new Map(nodes.map(n=>[n.id,n]));
  nodes.forEach(n=>{ n.ties=[]; });
  links.forEach(l=>{ byId.get(l.source).ties.push({id:l.target,seg:l.seg}); byId.get(l.target).ties.push({id:l.source,seg:l.seg}); });
  return {nodes,links,byId};
}
function renderNetwork(E){
  const {nodes,links,byId}=E;
  const w=900, top=50, bottom=24, rowH=31;
  const colOf=n=>n.type==='dev'?1:(n.type==='cust'||n.id==='McLeod Software'?2:0);
  nodes.forEach(n=>{ n.c=colOf(n); n.r=5+1.9*Math.sqrt(n.deg)+(n.both?2:0); n.nb=n.ties.map(t=>byId.get(t.id)); });
  const hubIds=new Set(nodes.filter(n=>n.both).map(n=>n.id));
  const touchesHub=n=>n.both||n.ties.some(t=>hubIds.has(t.id));
  const cols=[0,1,2].map(c=>nodes.filter(n=>n.c===c));
  cols.forEach(a=>a.sort((p,q)=>q.deg-p.deg||p.id.localeCompare(q.id)));
  const setPos=()=>cols.forEach(a=>a.forEach((n,i)=>{ n.p=a.length>1?i/(a.length-1):.5; }));
  setPos();
  for(let it=0;it<10;it++){ [1,0,2].forEach(c=>{ cols[c].forEach(n=>{ const o=n.nb.filter(m=>m.c!==c); n.bc=o.length?o.reduce((s,m)=>s+m.p,0)/o.length:n.p; }); cols[c].sort((p,q)=>p.bc-q.bc||q.deg-p.deg); setPos(); }); }
  const maxN=Math.max(...cols.map(a=>a.length)), h=top+bottom+(maxN-1)*rowH, X=[210,470,690];
  cols.forEach((a,c)=>a.forEach((n,i)=>{ n.x=X[c]; n.y=top+(a.length>1?i/(a.length-1):.5)*(maxN-1)*rowH; }));
  let s=`<svg viewBox="0 0 ${w} ${h}" class="net-svg" role="img" aria-label="Alliance network: ${nodes.length} companies and ${links.length} partnerships or orders, arranged as truck makers and suppliers, developers and operators, and customers. Six companies tie both electric and autonomous trucking together.">`;
  [['OEMs & suppliers',X[0]-70],['Developers & operators',X[1]],['Shippers, carriers & software',X[2]+60]].forEach(([t,x])=>{ s+=`<text x="${x}" y="16" text-anchor="middle" style="font-family:var(--font-d);font-size:10.5px;font-weight:700;letter-spacing:1.5px;fill:#89A1B4;">${t.toUpperCase()}</text>`; });
  s+='<g id="net-links">';
  links.forEach(l=>{
    const a=byId.get(l.source), b=byId.get(l.target); const [p,q]=a.x<=b.x?[a,b]:[b,a];
    const d=p.x===q.x?`M${p.x},${p.y} C${p.x-36},${p.y} ${p.x-36},${q.y} ${q.x},${q.y}`:`M${p.x},${p.y} C${(p.x+q.x)/2},${p.y} ${(p.x+q.x)/2},${q.y} ${q.x},${q.y}`;
    const ev=l.seg==='EV', both=l.seg==='BOTH', hub=hubIds.has(l.source)||hubIds.has(l.target);
    const col=both?'#B79CFF':(ev?'#3EC6C6':'#8BCDFF');
    s+=`<path data-a="${esc(a.id)}" data-b="${esc(b.id)}" data-hub="${hub?1:0}" d="${d}" fill="none" stroke="${col}" stroke-opacity="${hub?.95:.3}" stroke-width="${hub?(both?2.8:2.2):1.1}" ${ev?'stroke-dasharray="5 4"':''}/>`;
  });
  s+='</g><g id="net-nodes">';
  nodes.forEach(n=>{
    const lvl=n.both?2:(touchesHub(n)?1:0);
    const lx=n.c===0?-(n.r+8):(n.c===1?0:n.r+8), anchor=n.c===0?'end':(n.c===1?'middle':'start'), ly=n.c===1?-(n.r+7):4.5;
    const fs=[11.5,12.5,14][lvl], fw=[500,600,700][lvl], fill=['#89A1B4','#F2F4F6','#FFFFFF'][lvl];
    s+=`<g class="node" tabindex="0" role="button" aria-label="${esc(n.id)}: ${n.deg} ties" data-id="${esc(n.id)}" transform="translate(${n.x},${n.y})"><circle r="${n.r}" fill="${NODE_COL[n.type]}" stroke="${n.both?'#B79CFF':'#292A4E'}" stroke-width="${n.both?3.5:1.5}"/>`+
       `<text x="${lx}" y="${ly}" text-anchor="${anchor}" style="font-size:${fs}px;font-weight:${fw};fill:${fill};paint-order:stroke;stroke:#292A4E;stroke-width:4px;stroke-linejoin:round;">${esc(n.id)}</text></g>`;
  });
  s+='</g></svg>';
  const root=$('net'); root.innerHTML=s;
  const svg=root.querySelector('svg');
  const adj=new Map(nodes.map(n=>[n.id,new Set([n.id,...n.ties.map(t=>t.id)])]));
  let pinned=null;
  const focus=idv=>{
    svg.querySelectorAll('g.node').forEach(g=>g.classList.toggle('dim',idv!==null&&!adj.get(idv).has(g.dataset.id)));
    svg.querySelectorAll('#net-links path').forEach(p=>{
      const on=idv!==null&&(p.dataset.a===idv||p.dataset.b===idv);
      p.classList.toggle('dim',idv!==null&&!on);
      if(on){ p.setAttribute('stroke-opacity','.95'); p.setAttribute('stroke-width','2.4'); }
      else { const hub=p.dataset.hub==='1'; p.setAttribute('stroke-opacity',hub?'.95':'.3'); p.setAttribute('stroke-width',hub?(p.getAttribute('stroke')==='#B79CFF'?'2.8':'2.2'):'1.1'); }
    });
  };
  svg.querySelectorAll('g.node').forEach(g=>{
    g.addEventListener('mouseenter',()=>{ if(pinned===null) focus(g.dataset.id); });
    g.addEventListener('mouseleave',()=>{ if(pinned===null) focus(null); });
    g.addEventListener('focus',()=>{ if(pinned===null) focus(g.dataset.id); });
    g.addEventListener('blur',()=>{ if(pinned===null) focus(null); });
    g.addEventListener('click',e=>{ e.stopPropagation(); pinned=pinned===g.dataset.id?null:g.dataset.id; focus(pinned); });
    g.addEventListener('keydown',e=>{ if(e.key==='Enter'||e.key===' '){ e.preventDefault(); g.dispatchEvent(new MouseEvent('click',{bubbles:true})); } });
  });
  svg.addEventListener('click',()=>{ pinned=null; focus(null); });
}
function renderBridges(E){
  const both=E.nodes.filter(n=>n.both).sort((a,b)=>b.deg-a.deg);
  $('bridges').innerHTML='<div class="bridges__h">Operating across both revolutions</div>'+both.map(n=>{
    const ev=n.ties.filter(t=>t.seg!=='AV').map(t=>t.id), av=n.ties.filter(t=>t.seg!=='EV').map(t=>t.id);
    return `<div class="bridge"><b>${esc(n.id)}</b><small>${TYPE_LAB[n.type]}</small><p><em style="color:var(--col-ev)">EV</em> ${ev.map(esc).join(', ')}<br><em style="color:var(--col-av)">AV</em> ${av.map(esc).join(', ')}</p></div>`;
  }).join('');
}
function renderHubs(E){
  const hubs=E.nodes.filter(n=>n.deg>=2).sort((a,b)=>b.deg-a.deg||a.id.localeCompare(b.id));
  $('hubs').innerHTML='<div class="bridges__h" style="margin-top:6px;">Main actors and their ties</div>'+hubs.map(n=>
    `<div class="hub"><div class="hub__h"><i style="background:${NODE_COL[n.type]};${n.both?'box-shadow:0 0 0 2px #B79CFF;':''}"></i><b>${esc(n.id)}</b><small>${TYPE_LAB[n.type]}</small></div><div class="hub__ties">${n.ties.map(t=>`<span class="tie${t.seg==='EV'?' tie--ev':(t.seg==='BOTH'?' tie--both':'')}">${esc(t.id)}</span>`).join('')}</div></div>`).join('');
}

/* ================= boot ================= */
initTimelines();
renderScale();
renderCapital();
renderExits();
renderMap();
const ECO=ecosystem();
renderNetwork(ECO); renderBridges(ECO); renderHubs(ECO);

const reduce=window.matchMedia('(prefers-reduced-motion: reduce)').matches;
if(reduce||!('IntersectionObserver' in window)){ document.querySelectorAll('.reveal').forEach(el=>el.classList.add('visible')); }
else{
  const obs=new IntersectionObserver(e=>{e.forEach(x=>{if(x.isIntersecting){x.target.classList.add('visible');obs.unobserve(x.target);}});},{threshold:0.06});
  document.querySelectorAll('.reveal').forEach(el=>obs.observe(el));
}
