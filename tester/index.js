/* TODO:
 * - reenable hits option when prod upgraded
 * - allow to see the actual full data of a single result
 * - allow sorting of results
*/

let configs, query_type, query, nb_results;
let queries_awaited = 0;

const headers = document.getElementById("headers");
const results = document.getElementById("results");
const loader = document.getElementById("loader");

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

const forgeQueryUrl = (conf) => {
  //return conf.instance + query_type + "/query?query=" + query + "&hits=" + nb_results + "&score_threshold=" + conf.threshold + "&min_year=" + conf.min_year + "&rank_metric=" + conf.metric;
    return conf.instance + query_type + "/query?query=" + query + "&score_threshold=" + conf.threshold + "&min_year=" + conf.min_year + "&rank_metric=" + conf.metric;
}

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
          if (elt.name) {
            text = elt.name;
            uri = "https://sciencespo.hal.science/search/index/?q=%2A&rows=30&sort=producedDate_tdate+desc&authIdPerson_i=" + elt["id-hal"];
          } else {
            text = elt.title_s;
            uri = elt.uri_s;
          }
          document.querySelector("#config-" + i + " td:nth-child(" + (n + 2) + ")").innerHTML = '<a href="' + uri + '" target="_blank">' + text + '</a>';
        });
        queries_awaited -= 1;
      })
  });
}

document.getElementById('query_authors').addEventListener('change', prepareTable);
document.getElementById('query_docs').addEventListener('change', prepareTable);

document.getElementById('instances').addEventListener('keyup', prepareTable);
document.getElementById('min_year').addEventListener('keyup', prepareTable);
document.getElementById('thresholds').addEventListener('keyup', prepareTable);

document.getElementById('metric_mean').addEventListener('change', prepareTable);
document.getElementById('metric_median').addEventListener('change', prepareTable);
document.getElementById('metric_log-mean').addEventListener('change', prepareTable);

document.getElementById('query').addEventListener('keyup', prepareTable);
document.getElementById('nb_results').addEventListener('change', prepareTable);
document.getElementById('submit').addEventListener('click', runQueries);

prepareTable();

setInterval(() => {
  if (!queries_awaited)
    loader.style.display = "none";
}, 100);
