document.addEventListener("DOMContentLoaded", function () {
  var button = document.getElementById("load-predictions");
  var container = document.getElementById("prediction-result");

  if (!button || !container) {
    return;
  }

  button.addEventListener("click", async function () {
    try {
      var response = await fetch("prediction_engine/data/match_predictions.csv");
      if (!response.ok) {
        container.textContent = "Erreur lors du chargement des prédictions.";
        return;
      }
      var text = await response.text();
      var lines = text.trim().split("\n");
      if (lines.length < 2) {
        container.textContent = "Aucune prédiction disponible.";
        return;
      }
      var headers = lines[0].split(",");
      var values = lines[1].split(",");
      var row = {};
      for (var i = 0; i < headers.length; i += 1) {
        row[headers[i]] = values[i];
      }

      var homeTeam = row["home_team"] || "";
      var awayTeam = row["away_team"] || "";
      var pHome = parseFloat(row["proba_home_win"] || "0");
      var pDraw = parseFloat(row["proba_draw"] || "0");
      var pAway = parseFloat(row["proba_away_win"] || "0");

      var homePct = (pHome * 100).toFixed(1);
      var drawPct = (pDraw * 100).toFixed(1);
      var awayPct = (pAway * 100).toFixed(1);

      container.innerHTML =
        homeTeam +
        " vs " +
        awayTeam +
        "<br>" +
        "Victoire " +
        homeTeam +
        " : " +
        homePct +
        " %" +
        "<br>" +
        "Match nul : " +
        drawPct +
        " %" +
        "<br>" +
        "Victoire " +
        awayTeam +
        " : " +
        awayPct +
        " %";
    } catch (e) {
      container.textContent = "Erreur inattendue lors du chargement des prédictions.";
    }
  });
});

