import { useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Container, Spinner, Alert } from 'react-bootstrap';

function AuthCallbackPage() {
  const [error, setError] = useState('');
  const location = useLocation();
  const navigate = useNavigate();
  const auth = useAuth();

  // Effect to process the token on component mount
  useEffect(() => {
    const searchParams = new URLSearchParams(location.search);
    const token = searchParams.get('token');

    if (token) {
      try {
        // Start the login process, but don't navigate here
        auth.loginWithToken(token);
      } catch (err: any) {
        setError(err.message || 'An unexpected error occurred during login.');
      }
    } else {
      setError('Authentication failed: No token provided.');
    }
    // Intentionally not including navigate/auth in deps to run only once on mount
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [location]);

  // Effect to navigate *after* authentication state has been updated
  useEffect(() => {
    // We navigate only when authentication is no longer in progress and we have a user
    if (!auth.isAuthenticating && auth.user) {
      navigate('/');
    }
  }, [auth.isAuthenticating, auth.user, navigate]);

  return (
    <Container className="d-flex flex-column justify-content-center align-items-center flex-grow-1">
      {error ? (
        <Alert variant="danger">{error}</Alert>
      ) : (
        <>
          <Spinner animation="border" role="status" className="mb-3">
            <span className="visually-hidden">Loading...</span>
          </Spinner>
          <p>Finalizing authentication, please wait...</p>
        </>
      )}
    </Container>
  );
}

export default AuthCallbackPage;

