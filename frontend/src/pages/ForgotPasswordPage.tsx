import { useState } from 'react';
import { Form, Button, Container, Card, Alert } from 'react-bootstrap';
import authService from '../services/auth.service';
import '../App.css';

function ForgotPasswordPage() {
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [variant, setVariant] = useState('info');

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setMessage('');
    setLoading(true);

    try {
      const response = await authService.forgotPassword(email);
      setMessage(response.message);
      setVariant('success');
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
        <h2 className="text-center mb-4">Forgot Password</h2>
        <Form onSubmit={handleSubmit}>
          {message && <Alert variant={variant}>{message}</Alert>}
          <p className="text-center text-muted mb-4">
            Enter your email address and we will send you a link to reset your password.
          </p>
          <Form.Group className="mb-3" controlId="formBasicEmail">
            <Form.Label>Email address</Form.Label>
            <Form.Control
              type="email"
              placeholder="Enter email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </Form.Group>
          <Button variant="primary" type="submit" className="w-100" disabled={loading}>
            {loading ? 'Sending...' : 'Send Reset Link'}
          </Button>
        </Form>
        <p className="text-center mt-3">
          <a href="/login">Back to Login</a>
        </p>
      </Card>
    </Container>
  );
}

export default ForgotPasswordPage;
