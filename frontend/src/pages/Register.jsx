import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../auth.jsx";

export default function Register() {
  const { register } = useAuth();
  const nav = useNavigate();
  const [form, setForm] = useState({ email: "", full_name: "", password: "" });
  const [err, setErr] = useState("");

  function upd(k, v) {
    setForm((f) => ({ ...f, [k]: v }));
  }

  async function onSubmit(e) {
    e.preventDefault();
    setErr("");
    try {
      await register(form);
      nav("/fields");
    } catch (e) {
      setErr(e.message);
    }
  }

  return (
    <form className="form" onSubmit={onSubmit}>
      <h2>Регистрация</h2>
      <label>
        ФИО
        <input required value={form.full_name} onChange={(e) => upd("full_name", e.target.value)} />
      </label>
      <label>
        Email
        <input type="email" required value={form.email} onChange={(e) => upd("email", e.target.value)} />
      </label>
      <label>
        Пароль (от 6 символов)
        <input type="password" minLength={6} required value={form.password} onChange={(e) => upd("password", e.target.value)} />
      </label>
      <button type="submit">Зарегистрироваться</button>
      {err && <div className="error">{err}</div>}
    </form>
  );
}
