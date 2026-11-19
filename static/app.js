let activeCase = null, progress = 0;
const $ = id => document.getElementById(id);
document.querySelectorAll(".case-card").forEach(card => card.addEventListener("click", () => openCase(card.dataset.case)));
async function api(url, body) {
  const options = body ? {method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify(body)} : {};
  const res = await fetch(url, options); const data = await res.json();
  if (!res.ok) throw new Error(data.error || "Something went wrong"); return data;
}
async function openCase(id) {
  try {
    const c = await api(`/api/case/${id}`); activeCase = id; progress = 0;
    $("caseTitle").textContent=c.title; $("caseIntro").textContent=c.intro; $("puzzleQuestion").textContent=c.puzzle.question;
    $("suspects").innerHTML=c.suspects.map(s=>`<div class="suspect"><strong>${escapeHtml(s.name)} · ${escapeHtml(s.role)}</strong><small><b>Motive:</b> ${escapeHtml(s.motive)}<br><b>Alibi:</b> ${escapeHtml(s.alibi)}</small></div>`).join("");
    $("clues").innerHTML=c.clues.map(x=>`<div class="clue"><strong>${escapeHtml(x.title)}</strong><p>${escapeHtml(x.detail)}</p></div>`).join("");
    $("result").textContent=""; $("guess").value=""; $("hintReply").textContent=""; $("chatLog").innerHTML='<p class="muted">Ask me about the evidence, timeline, or suspects.</p>';
    $("game").classList.remove("hidden"); $("caseGrid").classList.add("hidden"); updateProgress(20);
    $("game").scrollIntoView({behavior:"smooth"}); 
  } catch(e){alert(e.message)}
}
function escapeHtml(s){return String(s).replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));}
function updateProgress(n){progress=Math.max(progress,n);$("progressText").textContent=progress+"%";$("progressBar").style.width=progress+"%";}
$("backBtn").onclick=()=>{$("game").classList.add("hidden");$("caseGrid").classList.remove("hidden");activeCase=null;};
$("hintBtn").onclick=async()=>{if(!activeCase)return; $("hintBtn").disabled=true;try{const d=await api("/api/hint",{case_id:activeCase,progress:progress+"%"});$("hintReply").textContent=d.reply+" ("+d.mode+" mode)";updateProgress(40);}catch(e){$("hintReply").textContent=e.message;}finally{$("hintBtn").disabled=false;}};
$("solveBtn").onclick=async()=>{if(!activeCase)return;try{const d=await api("/api/solve",{case_id:activeCase,guess:$("guess").value});$("result").textContent=d.correct?`Case solved! ${d.solution}. +${d.score} points. ${d.explanation}`:d.explanation;if(d.correct){updateProgress(100);loadHistory();}else updateProgress(55);}catch(e){$("result").textContent=e.message;}};
$("guess").addEventListener("keydown",e=>{if(e.key==="Enter")$("solveBtn").click();});
$("chatForm").onsubmit=async e=>{e.preventDefault();const msg=$("chatInput").value.trim();if(!msg||!activeCase)return;appendChat("You",msg,"user");$("chatInput").value="";try{const d=await api("/api/chat",{case_id:activeCase,message:msg});appendChat("Detective AI",d.reply+" ("+d.mode+" mode)","bot");updateProgress(Math.max(progress,35));}catch(err){appendChat("Detective AI",err.message,"bot");}};
function appendChat(who,msg,cls){const p=document.createElement("p");p.className=cls;p.textContent=who+": "+msg;$("chatLog").appendChild(p);$("chatLog").scrollTop=$("chatLog").scrollHeight;}
async function loadHistory(){try{const d=await api("/api/history");$("historyList").innerHTML=d.history.length?d.history.map(h=>`<div class="history-item"><span>${escapeHtml(h.case)} · ${escapeHtml(h.result)}</span><span>${h.score} pts · ${escapeHtml(h.date)}</span></div>`).join(""):"No solved cases yet. Your completed cases will appear here.";}catch(e){$("historyList").textContent="Could not load history.";}}
$("refreshHistory").onclick=loadHistory;loadHistory();
