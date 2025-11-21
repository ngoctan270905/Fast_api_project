import { useEffect, useState } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { Container, Alert, Spinner, Card, Button } from 'react-bootstrap'; // Added Button
import authService from '../services/auth.service';
import '../App.css'; // Import the custom styles

function VerifyEmailPage() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [message, setMessage] = useState('Verifying your email...');
  const [variant, setVariant] = useState('info'); // 'info', 'success', 'danger'
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = searchParams.get('token');

    if (!token) {
      setMessage('No verification token found in the URL.');
      setVariant('danger');
      setLoading(false);
      return;
    }

    const verifyUserEmail = async () => {
      try {
        await authService.verifyEmail(token);
        setMessage('Email verified successfully! You can now log in.');
        setVariant('success');
        setLoading(false);
        // Optionally redirect to login page after a short delay
        setTimeout(() => {
          navigate('/login');
        }, 3000);
      } catch (error: any) {
        const resMessage =
          (error.response && error.response.data && error.response.data.detail) ||
          error.message ||
          error.toString();
        setMessage(`Email verification failed: ${resMessage}`);
        setVariant('danger');
        setLoading(false);
      }
    };

    verifyUserEmail();
  }, [searchParams, navigate]);

  return (
    <Container className="d-flex justify-content-center align-items-center flex-grow-1">
      <Card style={{ width: '30rem' }} className="form-card text-center">
        <h2 className="mb-4">Email Verification</h2>
        {loading ? (
          <Spinner animation="border" role="status" className="mb-3">
            <span className="visually-hidden">Loading...</span>
          </Spinner>
        ) : null}
        <Alert variant={variant}>
          {message}
        </Alert>
        {!loading && variant === 'success' && (
          <Button variant="primary" onClick={() => navigate('/login')}>Go to Login</Button>
        )}
        {!loading && variant === 'danger' && (
          <Button variant="secondary" onClick={() => navigate('/register')}>Back to Register</Button>
        )}
      </Card>
    </Container>
  );
}

export default VerifyEmailPage;
