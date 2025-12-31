
import { useState, useEffect } from 'react';
import { Container, Row, Col, Card, Button, Table, Form } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import ExamService from '../services/exam.service';
import type { Exam } from '../types/exam';

const ExamPage = () => {
  const [exams, setExams] = useState<Exam[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchExams = async () => {
      try {
        const examsData = await ExamService.getExams();
        setExams(examsData);
      } catch (err) {
        setError('Failed to fetch exams.');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchExams();
  }, []);

  return (
    <Container fluid className="p-4">
      <Row className="justify-content-center">
        <Col lg={10}>
          <Card className="shadow-sm mb-4">
            <Card.Body className="p-5 text-center">
              <h1 className="h3 font-weight-bold text-gray-800 mb-4">
                Tạo đề kiểm tra
              </h1>
              <div className="d-flex gap-3 justify-content-center">
                <Button variant="outline-primary">
                  <i className="bi bi-magic me-2"></i>
                  Tạo bằng Ai
                </Button>
                <Button variant="outline-primary">
                  Tạo thủ công
                </Button>
              </div>
            </Card.Body>
          </Card>

          <Card className="shadow-sm">
            <Card.Body className="p-4">
              <h2 className="h5 font-weight-semibold text-gray-800 mb-4">Các đề đã tạo</h2>
              <Row className="mb-4 align-items-center">
                <Col md={8}>
                  <Form.Control
                    type="text"
                    placeholder="Tìm kiếm..."
                  />
                </Col>
                <Col md={4} className="d-flex justify-content-end">
                  {/* Filter controls can go here */}
                </Col>
              </Row>

              {loading && <p>Loading...</p>}
              {error && <p className="text-danger">{error}</p>}
              {!loading && !error && (
                <Table striped bordered hover responsive>
                  <thead className="bg-light">
                    <tr>
                      <th>Tên đề kiểm tra</th>
                      <th>Khối lớp</th>
                      <th>Ngày tạo</th>
                      <th>Thao tác</th>
                    </tr>
                  </thead>
                  <tbody>
                    {exams.map((exam) => (
                      <tr key={exam._id}>
                        <td>{exam.name}</td>
                        <td>{exam.grade}</td>
                        <td>{new Date(exam.created_at).toLocaleDateString()}</td>
                        <td>
                          <Button variant="light" size="sm" className="me-2" title="Chỉnh sửa">
                            <i className="bi bi-pencil-square"></i>
                          </Button>
                          <Button variant="light" size="sm" className="me-2" title="Xem">
                            <i className="bi bi-eye"></i>
                          </Button>
                          <Button variant="light" size="sm" title="Xóa">
                            <i className="bi bi-trash"></i>
                          </Button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </Table>
              )}
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  );
};

export default ExamPage;
