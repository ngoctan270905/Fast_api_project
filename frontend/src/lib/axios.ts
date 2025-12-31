import axios from 'axios';
import AuthService from '../services/auth.service';

const instance = axios.create({
  baseURL: 'http://localhost:8000/api/v1',
});

instance.interceptors.request.use(
  (config) => {
    const user = AuthService.getCurrentUser();
    if (user && user.access_token) {
      config.headers['Authorization'] = `Bearer ${user.access_token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

export default instance;
