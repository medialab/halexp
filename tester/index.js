/* TODO:
 * - allow sorting of results
*/

let configs, query_type, query, nb_results;
let details = {};
let queries_awaited = 0;

const headers = document.getElementById("headers");
const results = document.getElementById("results");
const loader = document.getElementById("loader");
const tooltip = document.getElementById("tooltip");

const trim = (text) => text.trim();

const readInputs = () => {
  configs = [];

  const instances = document.getElementById("instances").value
    .split('\n').map(trim).filter((x) => x)
    .map((url) => url.replace(/^(https?:\/\/)?/, "//").replace(/\/?$/, "/"));

  const min_years = document.getElementById("min_year").value
    .split('\n').map(trim).filter((x) => x)
    .map((year) => parseInt(year));

  const thresholds = document.getElementById("thresholds").value
    .split('\n').map(trim).filter((x) => x)
    .map((val) => parseFloat(val));

  const metrics = [];
  document.querySelectorAll('#metrics input[type="checkbox"]').forEach(
    (metric) => {
      if (metric.checked)
        metrics.push(metric.value);
    });

  instances.forEach((i) =>
    min_years.forEach((y) =>
      thresholds.forEach((t) =>
        metrics.forEach((m) =>
          configs.push(
            {
              name: [i.replace(/^.*\/([^\/]+)\/$/, "$1"), y, t, m].join(" | "),
              instance: i,
              min_year: y,
              threshold: t,
              metric: m
            }
          )
        )
      )
    )
  );

  query_type = document.querySelector('input[name="query_type"]:checked').value;
  query = document.getElementById("query").value;
  nb_results = parseInt(document.getElementById("nb_results").value);

  console.log(configs, nb_results);
}

const forgeQueryUrl = (conf) => conf.instance + query_type + "/query?query=" + query + "&hits=" + nb_results + "&score_threshold=" + conf.threshold + "&min_year=" + conf.min_year + "&rank_metric=" + conf.metric;

const prepareTable = () => {
  readInputs();

  let cols = ["Config"];
  for (let i = 0; i < nb_results; i++) {
    cols.push("#&nbsp;" + (i + 1))
  };
  headers.innerHTML = cols.map((c) => "<th>" + c + "</th>").join("");

  let rows = [];
  for (let i = 0; i < configs.length; i++) {
    let row = [];
    row.push('<a class="query_link" href=' + forgeQueryUrl(configs[i])+ ' target="_blank">🔗</a> ' + configs[i].name);
    for (let j = 0; j < nb_results; j++) {
      row.push("");
    };
    rows.push(row.map((c) => "<td>" + c + "</td>").join(""));
  };
  values.innerHTML = rows.map((r, i) => '<tr id="config-' + i + '">' + r + '</tr>').join("")
}

const runQueries = () => {
  prepareTable();
  queries_awaited = configs.length;
  loader.style.display = "block";

  configs.forEach((config, i) => {
    const route = forgeQueryUrl(config);
    console.log("Call #" + i + ": " + route)
    fetch(route)
      .then(resp => resp.json())
      .then((data) => {
        console.log("Result #" + i + ": ", data)
        data.reponses.forEach((elt, n) => {
          let uri, text;
          if (elt.author_name) {
            text = elt.author_name;
            uri = "https://sciencespo.hal.science/search/index/?q=%2A&rows=30&sort=producedDate_tdate+desc&authIdPerson_i=" + elt["author_id-hal"];
          } else {
            text = elt.title_s;
            uri = elt.uri_s;
          }
          details[i + '#' + n] = elt;
          document.querySelector("#config-" + i + " td:nth-child(" + (n + 2) + ")").innerHTML = '<a href="' + uri + '" target="_blank">' + text + '</a>&nbsp;&nbsp;<span id="' + i + '#' + n + '" class="details">＋</span>';
        });
        document.querySelectorAll("#config-" + i + " span").forEach((el) => {
          el.addEventListener('mouseenter', () => showTooltip(el.id));
          el.addEventListener('mouseleave', () => clearTooltip());
        });
        queries_awaited -= 1;
      })
  });
}

const showTooltip = (elid) => {
  const dat = details[elid];
  if (query_type === "authors")
    tooltip.innerHTML = "<p><b>Score:</b> " + dat["aggregation score"] + "</p>" +
      "<p><b>Labo:</b> " + dat.author_labs_id + "</p>" +
      "<p><b>Matches (" + dat.results_phrases.length + "):</b> <ul><li>" + [...new Set(dat.results_phrases)].join("</li><li>") + "</li></ul></p>" +
      "<p><b>Papers (" + dat.results_metadata.length + "):</b> <ul><li>" + [...new Set(dat.results_metadata.map((p) => p.title_s[0]))].join("</li><li>") + "</li></ul></p>";
  else tooltip.innerHTML = "<p>" + dat.citationFull_s + "</p>" +
    "<p><b>Subtitle:</b> " + dat.subtitle_s[0] + "</p>" +
    "<p><b>Abstract:</b> " + dat.abstract_s[0] + "</p>" +
    "<p><b>Keywords:</b> <ul><li>" + dat.keyword_s.join("</li><li>") + "</li></ul></p>" +
    "<p><b>Year:</b> " + dat.publicationDate_s + "</p>";
  tooltip.style.display = "block";
  console.log(details[elid]);
}
const clearTooltip = () => {
  tooltip.innerHTML = "";
  tooltip.style.display = "none";
}

document.getElementById('query_authors').addEventListener('change', prepareTable);
document.getElementById('query_docs').addEventListener('change', prepareTable);

document.getElementById('instances').addEventListener('keyup', prepareTable);
document.getElementById('min_year').addEventListener('keyup', prepareTable);
document.getElementById('thresholds').addEventListener('keyup', prepareTable);

document.getElementById('metric_mean').addEventListener('change', prepareTable);
document.getElementById('metric_sigmoid').addEventListener('change', prepareTable);
document.getElementById('metric_sigmoid-mean').addEventListener('change', prepareTable);
document.getElementById('metric_median').addEventListener('change', prepareTable);
document.getElementById('metric_log-mean').addEventListener('change', prepareTable);

document.getElementById('query').addEventListener('keyup', prepareTable);
document.getElementById('query').addEventListener('change', runQueries);
document.getElementById('nb_results').addEventListener('change', prepareTable);
document.getElementById('submit').addEventListener('click', runQueries);

prepareTable();

setInterval(() => {
  if (!queries_awaited)
    loader.style.display = "none";
}, 100);
