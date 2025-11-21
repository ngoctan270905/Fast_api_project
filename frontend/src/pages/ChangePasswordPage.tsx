import { useState } from 'react';
import { Form, Button, Container, Card, Alert } from 'react-bootstrap';
import { useNavigate } from 'react-router-dom';
import authService from '../services/auth.service';
import '../App.css';

function ChangePasswordPage() {
  const [oldPassword, setOldPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [variant, setVariant] = useState('info');
  const navigate = useNavigate();

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setMessage('');
    setLoading(true);

    if (newPassword !== confirmPassword) {
      setMessage('New passwords do not match!');
      setVariant('danger');
      setLoading(false);
      return;
    }

    try {
      await authService.changePassword(oldPassword, newPassword);
      setMessage('Password changed successfully! You will be redirected shortly.');
      setVariant('success');
      setTimeout(() => {
        // In a real app, you might want to log the user out here.
        // For simplicity, we just navigate to the home page.
        navigate('/');
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
        <h2 className="text-center mb-4">Change Password</h2>
        <Form onSubmit={handleSubmit}>
          {message && <Alert variant={variant}>{message}</Alert>}
          <Form.Group className="mb-3" controlId="formOldPassword">
            <Form.Label>Old Password</Form.Label>
            <Form.Control
              type="password"
              placeholder="Enter your old password"
              required
              value={oldPassword}
              onChange={(e) => setOldPassword(e.target.value)}
            />
          </Form.Group>
          <Form.Group className="mb-3" controlId="formNewPassword">
            <Form.Label>New Password</Form.Label>
            <Form.Control
              type="password"
              placeholder="Enter new password"
              required
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
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
            />
          </Form.Group>
          <Button variant="primary" type="submit" className="w-100" disabled={loading}>
            {loading ? 'Changing...' : 'Change Password'}
          </Button>
        </Form>
      </Card>
    </Container>
  );
}

export default ChangePasswordPage;
