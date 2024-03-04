//import FileSaver from "file-saver";

let configs;
let nb_results;
let queries_awaited = 0;

const headers = document.getElementById("headers");
const results = document.getElementById("results");
const loader = document.getElementById("loader");

const trim = (text) => text.trim();

const readInputs = () => {
  configs = [];

  const instances = document.getElementById("instances").value
    .split('\n').map(trim)
    .map((url) => url.replace(/^(https?:\/\/)?/, "//").replace(/\/?$/, "/"));

  const min_years = document.getElementById("min_year").value
    .split('\n').map(trim)
    .map((year) => parseInt(year));

  const thresholds = document.getElementById("thresholds").value
    .split('\n').map(trim)
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

  nb_results = parseInt(document.getElementById("nb_results").value);

  console.log(configs, nb_results);
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
    row.push(configs[i].name);
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

  const query = document.getElementById("query").value;
  configs.forEach((config, i) => {
    if (i>1) return;
    //const route = config.instance + "authors/query?query=" + query + "&hits=" + nb_results + "&score_threshold=" + config.threshold + "&min_year=" + config.min_year + "&rank_metric=" + config.metric;
    const route = config.instance + "authors/query?query=" + query + "&score_threshold=" + config.threshold + "&min_year=" + config.min_year + "&rank_metric=" + config.metric;
    console.log("Call #" + i + ": " + route)
    fetch(route)
      .then(resp => resp.json()
        .then(data => ({status: resp.status, body: data}))
      )
      .then(obj => console.log(obj));
/*
      .then((res) => {console.log(res.arrayBuffer()); return res.arrayBuffer()})
      .then((data) => {
        console.log("Result #" + i + ": ", data)
        queries_awaited -= 1;
      })
*/
  });
}

document.getElementById('submit').addEventListener('click', runQueries);

prepareTable();

setInterval(() => {
  if (!queries_awaited)
    loader.style.display = "none";
}, 100);
