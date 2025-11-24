import { createContext, useState, useEffect, useContext } from 'react';
import AuthService from '../services/auth.service';
import axios from 'axios';

// Define the shape of the user object and context data
// In a real app, you would define a proper User type
interface User {
  id: number;
  username: string;
  email: string;
  is_active: boolean;
  role: string;
  email_verified: boolean;
  is_social_login: boolean; // Replaced hashed_password with this flag
  created_at: string; // Assuming datetime comes as string
  updated_at: string; // Assuming datetime comes as string
  access_token: string;
  token_type: string;
}

interface AuthContextType {
  user: User | null;
  isAuthenticating: boolean; // Exposed for UI feedback
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  loginWithToken: (token: string) => Promise<void>; // Make it async
}

// Create the context with a default null value
const AuthContext = createContext<AuthContextType | null>(null);

// Custom hook to use the auth context
export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

interface AuthProviderProps {
  children: any;
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<User | null>(null);
  const [isInitializing, setIsInitializing] = useState(true); // Renamed for clarity
  const [isAuthenticating, setIsAuthenticating] = useState(false); // For login process

  // On initial load, check localStorage for a user/token
  useEffect(() => {
    try {
      const currentUser = AuthService.getCurrentUser();
      if (currentUser && currentUser.access_token) {
        // Set the Authorization header for all subsequent axios requests
        axios.defaults.headers.common['Authorization'] = `Bearer ${currentUser.access_token}`;
        setUser(currentUser);
      }
    } catch (error) {
      console.error("Could not load user from localStorage", error);
      // Clear corrupted storage if necessary
      AuthService.logout();
    }
    finally {
      setIsInitializing(false); // Finish initial loading
    }
  }, []);

  const login = async (email: string, password: string) => {
    setIsAuthenticating(true);
    try {
      // AuthService.login will now handle fetching user details after getting token
      const user = await AuthService.login(email, password);
      axios.defaults.headers.common['Authorization'] = `Bearer ${user.access_token}`;
      setUser(user);
    }
    finally {
      setIsAuthenticating(false);
    }
  };

  const loginWithToken = async (token: string) => {
    setIsAuthenticating(true);
    try {
      // 1. Set the token for the upcoming /me call
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      
      // 2. Fetch user details from the /me endpoint
      const userDetails = await AuthService.getMe();

      // 3. Combine token and user details
      const userFromToken: User = {
        ...userDetails,
        access_token: token,
        token_type: 'Bearer',
        is_social_login: true, // We know this is true for this flow
      };

      AuthService.setCurrentUser(userFromToken);
      setUser(userFromToken);
    }
    finally {
      setIsAuthenticating(false);
    }
  };

  const logout = () => {
    AuthService.logout();
    delete axios.defaults.headers.common['Authorization'];
    setUser(null);
  };

  const value = {
    user,
    isAuthenticating, // Provide this to consumers
    login,
    logout,
    loginWithToken,
  };

  // Don't render children until the initial check is done
  return (
    <AuthContext.Provider value={value}>
      {!isInitializing && children}
    </AuthContext.Provider>
  );
}
