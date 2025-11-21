import { useState } from 'react';
import { Form, Button, Container, Card, Alert } from 'react-bootstrap';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import '../App.css';

function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const navigate = useNavigate();
  const auth = useAuth();

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setMessage('');
    setLoading(true);

    try {
      await auth.login(email, password);
      navigate('/'); // Redirect to home page on successful login
    } catch (error: any) {
      const resMessage =
        (error.response && error.response.data && error.response.data.detail) ||
        error.message ||
        error.toString();
      setMessage(resMessage);
      setLoading(false);
    }
  };

  return (
    <Container className="d-flex justify-content-center align-items-center flex-grow-1">
      <Card style={{ width: '25rem' }} className="form-card">
        <h2 className="text-center mb-4">Login</h2>
        <Form onSubmit={handleSubmit}>
          {message && <Alert variant="danger">{message}</Alert>}
          <Form.Group className="mb-3" controlId="formBasicUsernameOrEmail">
            <Form.Label>Username or Email</Form.Label>
            <Form.Control
              type="text" // Changed from email to text as it can be a username
              placeholder="Enter username or email"
              required
              value={email} // Keeping the state variable name as 'email' for now as it's what's being sent.
              onChange={(e) => setEmail(e.target.value)}
            />
          </Form.Group>

          <Form.Group className="mb-3" controlId="formBasicPassword">
            <Form.Label>Password</Form.Label>
            <Form.Control
              type="password"
              placeholder="Password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </Form.Group>
          <div className="text-end mb-3">
            <a href="/forgot-password">Forgot Password?</a>
          </div>
          <Button variant="primary" type="submit" className="w-100" disabled={loading}>
            {loading ? 'Logging in...' : 'Login'}
          </Button>
          
          <div className="divider my-4">OR</div>

          <Button 
            variant="outline-dark" 
            className="w-100" 
            as="a" 
            href="http://127.0.0.1:8000/api/v1/login/google"
          >
            <img src="https://img.icons8.com/color/16/000000/google-logo.png" alt="Google logo" className="me-2"/> 
            Login with Google
          </Button>

        </Form>
        <p className="text-center mt-3">
          Don't have an account? <a href="/register">Register here</a>
        </p>
      </Card>
    </Container>
  );
}

export default LoginPage;