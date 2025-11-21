import { useState, useEffect } from 'react';
import { Form, Button, Container, Card, Alert } from 'react-bootstrap';
import { useNavigate, useSearchParams } from 'react-router-dom';
import authService from '../services/auth.service';
import '../App.css';

function ResetPasswordPage() {
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [variant, setVariant] = useState('info');
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const token = searchParams.get('token');

  useEffect(() => {
    if (!token) {
      setMessage('No password reset token found. Please request a new link.');
      setVariant('danger');
    }
  }, [token]);

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setMessage('');
    setLoading(true);

    if (newPassword !== confirmPassword) {
      setMessage('Passwords do not match!');
      setVariant('danger');
      setLoading(false);
      return;
    }

    if (!token) {
        setMessage('No password reset token found. Please request a new link.');
        setVariant('danger');
        setLoading(false);
        return;
    }

    try {
      await authService.resetPassword(token, newPassword);
      setMessage('Password has been reset successfully! You can now log in with your new password.');
      setVariant('success');
      setTimeout(() => {
        navigate('/login');
      }, 3000);
    } catch (error: any) {
      const resMessage =
        (error.response && error.response.data && error.response.data.detail) ||
        error.message ||
        error.toString();
      setMessage(resMessage);
      setVariant('danger');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container className="d-flex justify-content-center align-items-center flex-grow-1">
      <Card style={{ width: '25rem' }} className="form-card">
        <h2 className="text-center mb-4">Reset Password</h2>
        <Form onSubmit={handleSubmit}>
          {message && <Alert variant={variant}>{message}</Alert>}
          <Form.Group className="mb-3" controlId="formNewPassword">
            <Form.Label>New Password</Form.Label>
            <Form.Control
              type="password"
              placeholder="Enter new password"
              required
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              disabled={!token}
            />
          </Form.Group>
          <Form.Group className="mb-3" controlId="formConfirmNewPassword">
            <Form.Label>Confirm New Password</Form.Label>
            <Form.Control
              type="password"
              placeholder="Confirm new password"
              required
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              disabled={!token}
            />
          </Form.Group>
          <Button variant="primary" type="submit" className="w-100" disabled={loading || !token}>
            {loading ? 'Resetting...' : 'Reset Password'}
          </Button>
        </Form>
      </Card>
    </Container>
  );
}

export default ResetPasswordPage;
