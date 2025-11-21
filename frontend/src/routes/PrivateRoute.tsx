import { Navigate, Outlet } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

function PrivateRoute() {
  const auth = useAuth();

  if (!auth.user) {
    // Redirect them to the /login page, but save the current location they were
    // trying to go to. This allows us to send them along to that page after they login.
    // The `replace` prop is used to replace the current entry in the history stack,
    // so the user won't get stuck in a loop of login pages if they press the back button.
    return <Navigate to="/login" replace />;
  }

  return <Outlet />; // Render the child route component (e.g., ChangePasswordPage)
}

export default PrivateRoute;
