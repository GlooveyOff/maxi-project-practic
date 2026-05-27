import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../auth.jsx";

export default function Login() {
  const { login } = useAuth();
  const nav = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [err, setErr] = useState("");

  async function onSubmit(e) {
    e.preventDefault();
    setErr("");
    try {
      await login(email, password);
      nav("/fields");
    } catch (e) {
      setErr(e.message);
    }
  }

  return (
    <form className="form" onSubmit={onSubmit}>
      <h2>Вход</h2>
      <label>
        Email
        <input
          type="email"
          autoFocus
          placeholder="ivanov@neftegaz.ru"
          required
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />
      </label>
      <label>
        Пароль
        <input
          type="password"
          placeholder="••••••••"
          required
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
      </label>
      <button type="submit">Войти</button>
      {err && <div className="error">{err}</div>}
      <p className="notice">Тестовый администратор: admin@neftegaz.ru / admin123</p>
    </form>
  );
}
