import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api.js";
import { useAuth } from "../auth.jsx";

const STATUS_LABEL = {
  exploration: { text: "Разведка", cls: "badge accent" },
  active: { text: "В эксплуатации", cls: "badge success" },
  suspended: { text: "Приостановлено", cls: "badge warn" },
  depleted: { text: "Истощено", cls: "badge danger" },
};

export default function Fields() {
  const { user } = useAuth();
  const [items, setItems] = useState([]);
  const [q, setQ] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState(emptyForm());
  const [err, setErr] = useState("");

  function emptyForm() {
    return { name: "", location: "", reserves_tons: 0, discovered_year: 2000, status: "exploration", description: "" };
  }

  async function load() {
    setItems(await api.fields.list(q));
  }

  useEffect(() => {
    load();
  }, [q]);

  async function onCreate(e) {
    e.preventDefault();
    setErr("");
    try {
      await api.fields.create({
        ...form,
        reserves_tons: Number(form.reserves_tons),
        discovered_year: Number(form.discovered_year),
      });
      setShowForm(false);
      setForm(emptyForm());
      load();
    } catch (e) {
      setErr(e.message);
    }
  }

  async function onDelete(id) {
    if (!confirm("Удалить месторождение?")) return;
    await api.fields.remove(id);
    load();
  }

  const isAdmin = user?.role === "admin";

  return (
    <>
      <h2>Месторождения</h2>
      <div className="toolbar">
        <input placeholder="Поиск по названию…" value={q} onChange={(e) => setQ(e.target.value)} />
        {isAdmin && <button onClick={() => setShowForm(true)}>+ Добавить</button>}
      </div>

      <table>
        <thead>
          <tr>
            <th>Название</th>
            <th>Локация</th>
            <th>Запасы, т</th>
            <th>Открыто</th>
            <th>Статус</th>
            <th>Скважин</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {items.map((f) => {
            const s = STATUS_LABEL[f.status] || { text: f.status, cls: "badge" };
            return (
              <tr key={f.id}>
                <td><Link to={`/fields/${f.id}`}>{f.name}</Link></td>
                <td>{f.location}</td>
                <td>{f.reserves_tons.toLocaleString("ru-RU")}</td>
                <td>{f.discovered_year}</td>
                <td><span className={s.cls}>{s.text}</span></td>
                <td>{f.wells_count}</td>
                <td>{isAdmin && <button className="danger" onClick={() => onDelete(f.id)}>Удалить</button>}</td>
              </tr>
            );
          })}
          {items.length === 0 && (
            <tr><td colSpan={7} className="notice">Ничего не найдено</td></tr>
          )}
        </tbody>
      </table>

      {showForm && (
        <div className="modal-backdrop" onClick={() => setShowForm(false)}>
          <form className="modal form" onClick={(e) => e.stopPropagation()} onSubmit={onCreate}>
            <h3>Новое месторождение</h3>
            <label>Название<input required value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} /></label>
            <label>Локация<input required value={form.location} onChange={(e) => setForm({ ...form, location: e.target.value })} /></label>
            <label>Запасы (тонн)<input type="number" min="0" step="0.1" required value={form.reserves_tons} onChange={(e) => setForm({ ...form, reserves_tons: e.target.value })} /></label>
            <label>Год открытия<input type="number" min="1900" max="2100" required value={form.discovered_year} onChange={(e) => setForm({ ...form, discovered_year: e.target.value })} /></label>
            <label>Статус
              <select value={form.status} onChange={(e) => setForm({ ...form, status: e.target.value })}>
                <option value="exploration">Разведка</option>
                <option value="active">В эксплуатации</option>
                <option value="suspended">Приостановлено</option>
                <option value="depleted">Истощено</option>
              </select>
            </label>
            <label>Описание<textarea value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} /></label>
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
