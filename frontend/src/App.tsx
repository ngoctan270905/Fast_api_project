import AppRouter from './routes/AppRouter';
import Layout from './components/Layout';
import { AuthProvider } from './contexts/AuthContext'; // Import AuthProvider

function App() {
  return (
    <AuthProvider> {/* Wrap the app with AuthProvider */}
      <Layout>
        <AppRouter />
      </Layout>
    </AuthProvider>
  );
}

export default App;