import { useEffect, useState } from "react";
import { api } from "../api.js";

function Tile({ title, value, hint }) {
  return (
    <div className="card">
      <h3>{title}</h3>
      <div style={{ fontSize: 28, fontWeight: 700, margin: "6px 0" }}>{value}</div>
      {hint && <p>{hint}</p>}
    </div>
  );
}

function Bar({ part, total, color }) {
  const pct = total > 0 ? Math.round((part / total) * 100) : 0;
  return (
    <div style={{ background: "var(--panel-2)", borderRadius: 6, overflow: "hidden", height: 10 }}>
      <div style={{ width: `${pct}%`, background: color, height: "100%" }} />
    </div>
  );
}

export default function Stats() {
  const [data, setData] = useState(null);
  const [err, setErr] = useState("");

  useEffect(() => {
    api.stats.overview().then(setData).catch((e) => setErr(e.message));
  }, []);

  if (err) return <p className="error">{err}</p>;
  if (!data) return <p className="notice">Загрузка…</p>;

  const requestsTotal = data.requests_open + data.requests_done;

  return (
    <>
      <h2>Сводка по компании</h2>

      <div className="cards">
        <Tile
          title="Месторождения"
          value={`${data.fields_active} / ${data.fields_total}`}
          hint="в эксплуатации / всего"
        />
        <Tile
          title="Скважины"
          value={`${data.wells_operating} / ${data.wells_total}`}
          hint="работают / всего"
        />
        <Tile
          title="Заявки"
          value={`${data.requests_open}`}
          hint={`в работе, закрыто ${data.requests_done}`}
        />
        <Tile
          title="Добыча"
          value={`${data.daily_output_tons.toLocaleString("ru-RU")} т`}
          hint="суммарно в сутки"
        />
        <Tile
          title="Свободные бригады"
          value={`${data.brigades_available}`}
          hint="можно назначить на новые заявки"
        />
      </div>

      <h3 style={{ marginTop: 28 }}>Загруженность</h3>

      <div style={{ display: "grid", gap: 16, maxWidth: 700, marginTop: 12 }}>
        <div>
          <div style={{ display: "flex", justifyContent: "space-between", fontSize: 13, marginBottom: 4 }}>
            <span>Скважины в эксплуатации</span>
            <span className="notice">{data.wells_operating} / {data.wells_total}</span>
          </div>
          <Bar part={data.wells_operating} total={data.wells_total} color="#22c55e" />
        </div>
        <div>
          <div style={{ display: "flex", justifyContent: "space-between", fontSize: 13, marginBottom: 4 }}>
            <span>Активные месторождения</span>
            <span className="notice">{data.fields_active} / {data.fields_total}</span>
          </div>
          <Bar part={data.fields_active} total={data.fields_total} color="#f08a24" />
        </div>
        <div>
          <div style={{ display: "flex", justifyContent: "space-between", fontSize: 13, marginBottom: 4 }}>
            <span>Закрытые заявки</span>
            <span className="notice">{data.requests_done} / {requestsTotal}</span>
          </div>
          <Bar part={data.requests_done} total={requestsTotal} color="#94a3b8" />
        </div>
      </div>
    </>
  );
}
