import { Navigate, Route, Routes } from "react-router-dom";
import Layout from "./components/Layout.jsx";
import ProtectedRoute from "./components/ProtectedRoute.jsx";
import Home from "./pages/Home.jsx";
import Login from "./pages/Login.jsx";
import Register from "./pages/Register.jsx";
import Fields from "./pages/Fields.jsx";
import FieldDetail from "./pages/FieldDetail.jsx";
import Wells from "./pages/Wells.jsx";
import Requests from "./pages/Requests.jsx";

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route index element={<Home />} />
        <Route path="login" element={<Login />} />
        <Route path="register" element={<Register />} />
        <Route path="fields" element={<Fields />} />
        <Route path="fields/:id" element={<FieldDetail />} />
        <Route
          path="wells"
          element={
            <ProtectedRoute>
              <Wells />
            </ProtectedRoute>
          }
        />
        <Route
          path="requests"
          element={
            <ProtectedRoute>
              <Requests />
            </ProtectedRoute>
          }
        />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  );
}
