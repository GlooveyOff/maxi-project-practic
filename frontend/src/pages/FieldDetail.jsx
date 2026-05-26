import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api } from "../api.js";

export default function FieldDetail() {
  const { id } = useParams();
  const [field, setField] = useState(null);
  const [wells, setWells] = useState([]);
  const [err, setErr] = useState("");

  useEffect(() => {
    (async () => {
      try {
        setField(await api.fields.get(id));
        setWells(await api.wells.list({ field_id: id }));
      } catch (e) {
        setErr(e.message);
      }
    })();
  }, [id]);

  if (err) return <p className="error">{err}</p>;
  if (!field) return <p className="notice">Загрузка…</p>;

  return (
    <>
      <h2>{field.name}</h2>
      <p className="notice">{field.location} · открыто в {field.discovered_year}</p>
      <p>{field.description || "—"}</p>

      <div className="cards">
        <div className="card"><h3>Запасы</h3><p>{field.reserves_tons.toLocaleString("ru-RU")} тонн</p></div>
        <div className="card"><h3>Скважин</h3><p>{wells.length}</p></div>
        <div className="card"><h3>Статус</h3><p>{field.status}</p></div>
      </div>

      <h3 style={{ marginTop: 24 }}>Скважины месторождения</h3>
      <table>
        <thead><tr><th>Название</th><th>Глубина, м</th><th>Добыча, т/сут</th><th>Статус</th></tr></thead>
        <tbody>
          {wells.map((w) => (
            <tr key={w.id}>
              <td>{w.name}</td>
              <td>{w.depth_m}</td>
              <td>{w.daily_output_tons}</td>
              <td>{w.status}</td>
            </tr>
          ))}
          {wells.length === 0 && <tr><td colSpan={4} className="notice">Скважины пока не заведены</td></tr>}
        </tbody>
      </table>

      <p style={{ marginTop: 16 }}><Link to="/fields">← К списку месторождений</Link></p>
    </>
  );
}
