(()=>{"use strict";var e,n,t=0,r=document.getElementById("headers"),u=(document.getElementById("results"),document.getElementById("loader")),o=function(e){return e.trim()},c=function(){!function(){e=[];var t=document.getElementById("instances").value.split("\n").map(o).map((function(e){return e.replace(/^(https?:\/\/)?/,"http://").replace(/\/?$/,"/")})),r=document.getElementById("min_year").value.split("\n").map(o).map((function(e){return parseInt(e)})),u=document.getElementById("thresholds").value.split("\n").map(o).map((function(e){return parseFloat(e)})),c=[];document.querySelectorAll('#metrics input[type="checkbox"]').forEach((function(e){e.checked&&c.push(e.value)})),t.forEach((function(n){return r.forEach((function(t){return u.forEach((function(r){return c.forEach((function(u){return e.push({name:[n.replace(/^.*\/([^\/]+)\/$/,"$1"),t,r,u].join(" | "),instance:n,min_year:t,threshold:r,metric:u})}))}))}))})),n=parseInt(document.getElementById("nb_results").value),console.log(e,n)}();for(var t=["Config"],u=0;u<n;u++)t.push("#&nbsp;"+(u+1));r.innerHTML=t.map((function(e){return"<th>"+e+"</th>"})).join("");for(var c=[],a=0;a<e.length;a++){var i=[];i.push(e[a].name);for(var l=0;l<n;l++)i.push("");c.push(i.map((function(e){return"<td>"+e+"</td>"})).join(""))}values.innerHTML=c.map((function(e,n){return'<tr id="config-'+n+'">'+e+"</tr>"})).join("")};document.getElementById("submit").addEventListener("click",(function(){c(),t=e.length,u.style.display="block";var n=document.getElementById("query").value;e.forEach((function(e,t){if(!(t>1)){var r=e.instance+"authors/query?query="+n+"&score_threshold="+e.threshold+"&min_year="+e.min_year+"&rank_metric="+e.metric;console.log("Call #"+t+": "+r),fetch(r).then((function(e){return e.json().then((function(n){return{status:e.status,body:n}}))})).then((function(e){return console.log(e)}))}}))})),c(),setInterval((function(){t||(u.style.display="none")}),100)})();
//# sourceMappingURL=bundle.js.map