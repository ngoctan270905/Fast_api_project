import { Navbar, Nav, Container, NavDropdown } from 'react-bootstrap'; // Import NavDropdown
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

function Header() {
  const auth = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    auth.logout();
    navigate('/login');
  };

  return (
    <Navbar bg="dark" variant="dark" expand="lg">
      <Container>
        <Navbar.Brand as={Link} to="/">Library App</Navbar.Brand>
        <Navbar.Toggle aria-controls="basic-navbar-nav" />
        <Navbar.Collapse id="basic-navbar-nav">
          <Nav className="me-auto">
            <Nav.Link as={Link} to="/">Home</Nav.Link>
            {/* Add more authenticated links here if needed */}
          </Nav>
          <Nav>
            {auth.user ? (
              <NavDropdown title={auth.user.username} id="basic-nav-dropdown" align="end">
                <NavDropdown.ItemText>
                  <small className="text-muted">
                    Logged in via: {auth.user.is_social_login ? 'Google' : 'Email'}
                  </small>
                </NavDropdown.ItemText>
                <NavDropdown.Divider />
                {!auth.user.is_social_login && (
                  <NavDropdown.Item as={Link} to="/change-password">
                    Change Password
                  </NavDropdown.Item>
                )}
                <NavDropdown.Item onClick={handleLogout}>
                  Logout
                </NavDropdown.Item>
              </NavDropdown>
            ) : (
              <>
                <Nav.Link as={Link} to="/login">Login</Nav.Link>
                <Nav.Link as={Link} to="/register">Register</Nav.Link>
              </>
            )}
          </Nav>
        </Navbar.Collapse>
      </Container>
    </Navbar>
  );
}

export default Header;