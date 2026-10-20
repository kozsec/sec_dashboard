const yearMonth = location.pathname.match(/(\d{4})-(\d{2})/);

if (!yearMonth) {
  throw new Error("ページの年月を特定できません。");
}

const [, year, month] = yearMonth;
const jsonPath = `../article/${year}-${month}/incidents_${year}${month}.json`;

fetch(jsonPath)
  .then(response => {
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return response.json();
  })


  .then(incidents => {
  
    document.getElementById("incident-count").textContent = `${incidents.length}件`;

    const threatCategories = [
      "ランサムウェアによる被害",
      "サプライチェーンや委託先を狙った攻撃",
      "システムの脆弱性を悪用した攻撃",
      "内部不正による情報漏えい等",
      "機密情報等を狙った標的型攻撃",
      "リモートワーク等の環境や仕組みを狙った攻撃",
      "地政学的リスクに起因するサイバー攻撃",
      "分散型サービス妨害攻撃（DDoS攻撃）",
      "ビジネスメール詐欺",
      "不注意による情報漏えい等"
    ];

    const threatCounts = new Map(
      threatCategories.map(category => [category, 0])
    );

    incidents.forEach(item => {
      (item.threats || []).forEach(threat => {
        if (threatCounts.has(threat)) {
          threatCounts.set(threat, threatCounts.get(threat) + 1);
        }
      });
    });

    const maxCount = Math.max(1, ...threatCounts.values());
    const threatContainer = document.getElementById("threat-chart-bars");
    threatContainer.innerHTML = "";

    threatCategories.forEach(category => {
      const count = threatCounts.get(category);
      const row = document.createElement("div");
      row.className = "threat-row";

      const name = document.createElement("span");
      name.className = "threat-name";
      name.textContent = category;

      const track = document.createElement("div");
      track.className = "threat-track";

      const bar = document.createElement("div");
      bar.className = "threat-bar";
      bar.style.width = `${count / maxCount * 100}%`;

      track.appendChild(bar);

      const value = document.createElement("span");
      value.className = "threat-count";
      value.textContent = count;

      row.append(name, track, value);
      threatContainer.appendChild(row);
    });

    const container = document.getElementById("incident-list");
    container.innerHTML = "";
    const perPage = 5;
    const sorted = incidents.slice().sort((a, b) => b.date.localeCompare(a.date));
    const pages = [];
    for (let i = 0; i < sorted.length; i += perPage) pages.push(sorted.slice(i, i + perPage));
    pages.forEach((items, pageIndex) => {
      const page = document.createElement("section");
      page.className = "report-list-page";
      if (pageIndex > 0) {
        const heading = document.createElement("h2");
        heading.textContent = `インシデント一覧（${pageIndex + 1}）`;
        page.appendChild(heading);
      }
      items.forEach(item => {
        const article = document.createElement("article");
        article.className = "report-list-item";
        const title = document.createElement("h3");
        title.textContent = `${item.date.replaceAll("-", "/")}｜${item.organization}：${item.title}`;
        article.appendChild(title);
        const summary = document.createElement("p");
        summary.textContent = item.summary;
        article.appendChild(summary);
        const tags = document.createElement("div");

        article.appendChild(tags);
        const links = document.createElement("div");
        links.className = "report-links";
        item.reports.forEach(report => {
          const a = document.createElement("a");
          a.href = report.url;
          a.target = "_blank";
          a.rel = "noopener noreferrer";
          a.textContent = report.label;
          a.title = `${report.title}（${report.date}）`;
          links.appendChild(a);
        });
        article.appendChild(links);
        page.appendChild(article);
      });
      container.appendChild(page);
    });
  })
  .catch(() => {
    document.getElementById("incident-list").textContent = "一覧データを読み込めませんでした。JSONファイルの配置とパスを確認してください。";
  });
