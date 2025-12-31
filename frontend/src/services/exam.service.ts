import api from '../lib/axios';
import type { Exam } from '../types/exam';

class ExamService {
  async getExams(): Promise<Exam[]> {
    const response = await api.get('/exams/');
    return response.data.data;
  }
}

export default new ExamService();
