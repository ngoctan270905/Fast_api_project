import axios from 'axios';

// Define the User type to match the AuthContext
// This avoids having to import it and potentially causing circular dependencies
interface User {
  id: number;
  username: string;
  email: string;
  is_active: boolean;
  role: string;
  email_verified: boolean;
  is_social_login: boolean;
  created_at: string;
  updated_at: string;
  access_token: string;
  token_type: string;
}

const AUTH_API_URL = 'http://localhost:8000/api/v1/auth/';
const USER_API_URL = 'http://localhost:8000/api/v1/users/';

class AuthService {
  async register(username: string, email: string, password: string): Promise<any> {
    const response = await axios.post(AUTH_API_URL + 'register', {
      username,
      email,
      password,
    });
    return response.data;
  }

  async verifyEmail(token: string): Promise<any> {
    const response = await axios.post(AUTH_API_URL + 'verify-email', {
      token,
    });
    return response.data;
  }

  async forgotPassword(email: string): Promise<any> {
    const response = await axios.post(AUTH_API_URL + 'forgot-password', {
      email,
    });
    return response.data;
  }

  async resetPassword(token: string, new_password: string): Promise<any> {
    const response = await axios.post(AUTH_API_URL + 'reset-password', {
      token,
      new_password,
    });
    return response.data;
  }
  
  async getMe(): Promise<Omit<User, 'access_token' | 'token_type'>> {
    const response = await axios.get(AUTH_API_URL + 'me');
    return response.data;
  }

  async login(email: string, password: string): Promise<User> {
    const params = new URLSearchParams();
    params.append('username', email);
    params.append('password', password);

    // 1. Get the token
    const tokenResponse = await axios.post(AUTH_API_URL + 'login', params, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    });

    const { access_token, token_type } = tokenResponse.data;

    if (access_token) {
      // 2. Set auth header for the next request
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;

      // 3. Get user details
      const userDetails = await this.getMe();

      // 4. Combine into a full user object
      const user: User = {
        ...userDetails,
        access_token,
        token_type,
      };
      
      this.setCurrentUser(user);
      return user;
    }
    
    // This part should ideally not be reached if login fails, as axios will throw.
    // But as a fallback, we throw an error.
    throw new Error("Login failed: No access token received.");
  }

  logout(): void {
    localStorage.removeItem('user');
  }

  setCurrentUser(user: User): void {
    localStorage.setItem('user', JSON.stringify(user));
  }

  getCurrentUser(): User | null {
    const userStr = localStorage.getItem('user');
    if (userStr) {
      return JSON.parse(userStr);
    }
    return null;
  }

  async changePassword(old_password: string, new_password: string): Promise<any> {
    const response = await axios.post(USER_API_URL + 'me/change-password', {
      old_password,
      new_password,
    });
    return response.data;
  }
}

export default new AuthService();

