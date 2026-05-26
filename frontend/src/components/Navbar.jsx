import { NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../auth.jsx";

export default function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  function onLogout() {
    logout();
    navigate("/login");
  }

  return (
    <header className="navbar">
      <div className="logo">НЕФТЕГАЗ</div>
      <nav>
        <NavLink to="/" end>Главная</NavLink>
        <NavLink to="/fields">Месторождения</NavLink>
        {user && <NavLink to="/wells">Скважины</NavLink>}
        {user && <NavLink to="/requests">Заявки</NavLink>}
      </nav>
      {user ? (
        <>
          <span className="user">{user.full_name} · {user.role}</span>
          <button className="secondary" onClick={onLogout}>Выйти</button>
        </>
      ) : (
        <>
          <NavLink to="/login">Вход</NavLink>
          <NavLink to="/register">Регистрация</NavLink>
        </>
      )}
    </header>
  );
}
