import { Navigate, Outlet } from 'react-router-dom';
import { useAppSelector } from '../../hooks/useStore';

export default function ProtectedRoute() {
  const { token } = useAppSelector((s) => s.auth);
  if (!token) return <Navigate to="/login" replace />;
  return <Outlet />;
}
