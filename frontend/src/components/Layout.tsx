import { Container } from 'react-bootstrap';
import Header from './Header';

interface LayoutProps {
  children: React.ReactNode;
}

function Layout({ children }: LayoutProps) {
  return (
    <>
      <Header />
      <Container className="my-4">
        {children}
      </Container>
    </>
  );
}

export default Layout;