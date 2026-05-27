import { useEffect, useState } from "react";
import { api } from "../api.js";
import { useAuth } from "../auth.jsx";
import { useToast } from "../components/Toast.jsx";

const STATUS_LABEL = {
  available: { text: "Доступна", cls: "badge success" },
  on_site: { text: "На объекте", cls: "badge accent" },
  resting: { text: "Отдых", cls: "badge warn" },
  off_duty: { text: "Не на смене", cls: "badge" },
};

const emptyForm = () => ({
  name: "", foreman: "", members_count: 4, phone: "", status: "available",
});

export default function Brigades() {
  const { user } = useAuth();
  const toast = useToast();
  const [brigades, setBrigades] = useState([]);
  const [statusFilter, setStatusFilter] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState(emptyForm());
  const [err, setErr] = useState("");

  const isAdmin = user?.role === "admin";

  async function load() {
    const params = statusFilter ? { status: statusFilter } : {};
    setBrigades(await api.brigades.list(params));
  }
  useEffect(() => { load(); }, [statusFilter]);

  async function onCreate(e) {
    e.preventDefault();
    setErr("");
    try {
      await api.brigades.create({ ...form, members_count: Number(form.members_count) });
      setShowForm(false);
      setForm(emptyForm());
      toast.push("Бригада создана", "success");
      load();
    } catch (e) {
      setErr(e.message);
    }
  }

  async function changeStatus(id, status) {
    await api.brigades.patch(id, { status });
    toast.push("Статус обновлён", "success");
    load();
  }

  async function onDelete(id) {
    if (!confirm("Удалить бригаду?")) return;
    await api.brigades.remove(id);
    toast.push("Бригада удалена", "success");
    load();
  }

  return (
    <>
      <h2>Бригады обслуживания</h2>
      <div className="toolbar">
        <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
          <option value="">Все статусы</option>
          <option value="available">Доступна</option>
          <option value="on_site">На объекте</option>
          <option value="resting">Отдых</option>
          <option value="off_duty">Не на смене</option>
        </select>
        {isAdmin && <button onClick={() => setShowForm(true)}>+ Бригада</button>}
      </div>

      <table>
        <thead>
          <tr>
            <th>Название</th><th>Бригадир</th><th>Состав</th>
            <th>Телефон</th><th>Статус</th><th>Активных заявок</th><th></th>
          </tr>
        </thead>
        <tbody>
          {brigades.map((b) => {
            const s = STATUS_LABEL[b.status] || { text: b.status, cls: "badge" };
            return (
              <tr key={b.id}>
                <td><b>{b.name}</b></td>
                <td>{b.foreman}</td>
                <td>{b.members_count} чел.</td>
                <td>{b.phone || "—"}</td>
                <td>
                  {isAdmin ? (
                    <select value={b.status} onChange={(e) => changeStatus(b.id, e.target.value)}>
                      <option value="available">Доступна</option>
                      <option value="on_site">На объекте</option>
                      <option value="resting">Отдых</option>
                      <option value="off_duty">Не на смене</option>
                    </select>
                  ) : (
                    <span className={s.cls}>{s.text}</span>
                  )}
                </td>
                <td>{b.active_requests}</td>
                <td>{isAdmin && <button className="danger" onClick={() => onDelete(b.id)}>×</button>}</td>
              </tr>
            );
          })}
          {brigades.length === 0 && (
            <tr><td colSpan={7} className="notice">Бригады пока не заведены</td></tr>
          )}
        </tbody>
      </table>

      {showForm && (
        <div className="modal-backdrop" onClick={() => setShowForm(false)}>
          <form className="modal form" onClick={(e) => e.stopPropagation()} onSubmit={onCreate}>
            <h3>Новая бригада</h3>
            <label>Название<input required value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} /></label>
            <label>Бригадир<input required value={form.foreman} onChange={(e) => setForm({ ...form, foreman: e.target.value })} /></label>
            <label>Размер бригады<input type="number" min="1" max="50" required value={form.members_count} onChange={(e) => setForm({ ...form, members_count: e.target.value })} /></label>
            <label>Телефон<input placeholder="+7 (___) ___-__-__" value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })} /></label>
            <label>Статус
              <select value={form.status} onChange={(e) => setForm({ ...form, status: e.target.value })}>
                <option value="available">Доступна</option>
                <option value="on_site">На объекте</option>
                <option value="resting">Отдых</option>
                <option value="off_duty">Не на смене</option>
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
