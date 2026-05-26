import { useEffect, useState } from "react";
import { api } from "../api.js";
import { useAuth } from "../auth.jsx";

const STATUSES = ["", "drilling", "operating", "maintenance", "closed"];

export default function Wells() {
  const { user } = useAuth();
  const [wells, setWells] = useState([]);
  const [fields, setFields] = useState([]);
  const [statusFilter, setStatusFilter] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ field_id: "", name: "", depth_m: 1000, daily_output_tons: 0, status: "drilling" });
  const [err, setErr] = useState("");

  async function load() {
    const params = statusFilter ? { status: statusFilter } : {};
    setWells(await api.wells.list(params));
  }

  useEffect(() => { api.fields.list().then(setFields); }, []);
  useEffect(() => { load(); }, [statusFilter]);

  const isAdmin = user?.role === "admin";

  async function onCreate(e) {
    e.preventDefault();
    setErr("");
    try {
      await api.wells.create({
        ...form,
        field_id: Number(form.field_id),
        depth_m: Number(form.depth_m),
        daily_output_tons: Number(form.daily_output_tons),
      });
      setShowForm(false);
      load();
    } catch (e) {
      setErr(e.message);
    }
  }

  async function onDelete(id) {
    if (!confirm("Удалить скважину?")) return;
    await api.wells.remove(id);
    load();
  }

  function fieldName(id) {
    return fields.find((f) => f.id === id)?.name || `#${id}`;
  }

  return (
    <>
      <h2>Скважины</h2>
      <div className="toolbar">
        <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
          {STATUSES.map((s) => <option key={s} value={s}>{s ? s : "Все статусы"}</option>)}
        </select>
        {isAdmin && <button onClick={() => setShowForm(true)}>+ Скважина</button>}
      </div>

      <table>
        <thead><tr><th>Название</th><th>Месторождение</th><th>Глубина, м</th><th>Добыча, т/сут</th><th>Статус</th><th></th></tr></thead>
        <tbody>
          {wells.map((w) => (
            <tr key={w.id}>
              <td>{w.name}</td>
              <td>{fieldName(w.field_id)}</td>
              <td>{w.depth_m}</td>
              <td>{w.daily_output_tons}</td>
              <td><span className="badge">{w.status}</span></td>
              <td>{isAdmin && <button className="danger" onClick={() => onDelete(w.id)}>×</button>}</td>
            </tr>
          ))}
          {wells.length === 0 && <tr><td colSpan={6} className="notice">Нет данных</td></tr>}
        </tbody>
      </table>

      {showForm && (
        <div className="modal-backdrop" onClick={() => setShowForm(false)}>
          <form className="modal form" onClick={(e) => e.stopPropagation()} onSubmit={onCreate}>
            <h3>Новая скважина</h3>
            <label>Месторождение
              <select required value={form.field_id} onChange={(e) => setForm({ ...form, field_id: e.target.value })}>
                <option value="">— выбрать —</option>
                {fields.map((f) => <option key={f.id} value={f.id}>{f.name}</option>)}
              </select>
            </label>
            <label>Название<input required value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} /></label>
            <label>Глубина (м)<input type="number" min="1" step="0.1" required value={form.depth_m} onChange={(e) => setForm({ ...form, depth_m: e.target.value })} /></label>
            <label>Добыча (т/сут)<input type="number" min="0" step="0.1" value={form.daily_output_tons} onChange={(e) => setForm({ ...form, daily_output_tons: e.target.value })} /></label>
            <label>Статус
              <select value={form.status} onChange={(e) => setForm({ ...form, status: e.target.value })}>
                <option value="drilling">Бурение</option>
                <option value="operating">Эксплуатация</option>
                <option value="maintenance">ТО</option>
                <option value="closed">Закрыта</option>
              </select>
            </label>
            <div style={{ display: "flex", gap: 8 }}>
              <button type="submit">Сохранить</button>
              <button type="button" className="secondary" onClick={() => setShowForm(false)}>Отмена</button>
            </div>
            {err && <div className="error">{err}</div>}
          </form>
        </div>
      )}
    </>
  );
}
