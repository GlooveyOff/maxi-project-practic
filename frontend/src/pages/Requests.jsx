import { useEffect, useState } from "react";
import { api } from "../api.js";
import { useAuth } from "../auth.jsx";

const PRIORITY = ["low", "medium", "high", "critical"];
const STATUS = ["new", "in_progress", "done", "rejected"];

export default function Requests() {
  const { user } = useAuth();
  const [requests, setRequests] = useState([]);
  const [wells, setWells] = useState([]);
  const [statusFilter, setStatusFilter] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ well_id: "", title: "", description: "", priority: "medium" });
  const [err, setErr] = useState("");

  async function load() {
    const params = statusFilter ? { status: statusFilter } : {};
    setRequests(await api.requests.list(params));
  }

  useEffect(() => { api.wells.list().then(setWells); }, []);
  useEffect(() => { load(); }, [statusFilter]);

  async function onCreate(e) {
    e.preventDefault();
    setErr("");
    try {
      await api.requests.create({ ...form, well_id: Number(form.well_id) });
      setShowForm(false);
      setForm({ well_id: "", title: "", description: "", priority: "medium" });
      load();
    } catch (e) {
      setErr(e.message);
    }
  }

  async function changeStatus(id, status) {
    await api.requests.patch(id, { status });
    load();
  }

  function wellName(id) {
    return wells.find((w) => w.id === id)?.name || `#${id}`;
  }

  return (
    <>
      <h2>Заявки на обслуживание</h2>
      <div className="toolbar">
        <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
          <option value="">Все статусы</option>
          {STATUS.map((s) => <option key={s} value={s}>{s}</option>)}
        </select>
        <button onClick={() => setShowForm(true)}>+ Создать</button>
      </div>

      <table>
        <thead><tr><th>Заголовок</th><th>Скважина</th><th>Приоритет</th><th>Статус</th><th>Создано</th></tr></thead>
        <tbody>
          {requests.map((r) => (
            <tr key={r.id}>
              <td><b>{r.title}</b><div className="notice">{r.description}</div></td>
              <td>{wellName(r.well_id)}</td>
              <td><span className="badge accent">{r.priority}</span></td>
              <td>
                <select value={r.status} onChange={(e) => changeStatus(r.id, e.target.value)}>
                  {STATUS.map((s) => <option key={s} value={s}>{s}</option>)}
                </select>
              </td>
              <td>{new Date(r.created_at).toLocaleString("ru-RU")}</td>
            </tr>
          ))}
          {requests.length === 0 && <tr><td colSpan={5} className="notice">Заявок нет</td></tr>}
        </tbody>
      </table>

      {showForm && (
        <div className="modal-backdrop" onClick={() => setShowForm(false)}>
          <form className="modal form" onClick={(e) => e.stopPropagation()} onSubmit={onCreate}>
            <h3>Новая заявка</h3>
            <label>Скважина
              <select required value={form.well_id} onChange={(e) => setForm({ ...form, well_id: e.target.value })}>
                <option value="">— выбрать —</option>
                {wells.map((w) => <option key={w.id} value={w.id}>{w.name}</option>)}
              </select>
            </label>
            <label>Заголовок<input required minLength={3} value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} /></label>
            <label>Описание<textarea required value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} /></label>
            <label>Приоритет
              <select value={form.priority} onChange={(e) => setForm({ ...form, priority: e.target.value })}>
                {PRIORITY.map((p) => <option key={p} value={p}>{p}</option>)}
              </select>
            </label>
            <div style={{ display: "flex", gap: 8 }}>
              <button type="submit">Создать</button>
              <button type="button" className="secondary" onClick={() => setShowForm(false)}>Отмена</button>
            </div>
            {err && <div className="error">{err}</div>}
          </form>
        </div>
      )}
    </>
  );
}
