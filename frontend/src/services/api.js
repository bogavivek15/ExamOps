/**
 * ExamOps Frontend — API Client Layer
 * Handles communication with FastAPI backend, token management, and authenticated session dispatching.
 */

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

class ApiClient {
  constructor() {
    this.token = localStorage.getItem('examops_token') || null;
    try {
      this.currentUser = JSON.parse(localStorage.getItem('examops_user') || 'null');
    } catch {
      this.currentUser = null;
    }
    this.activeRole = this.currentUser?.role || 'ACADEMIC_ADMINISTRATOR';
  }

  getToken() {
    return this.token;
  }

  setSession(token, user) {
    this.token = token;
    this.currentUser = user;
    this.activeRole = user?.role || 'ACADEMIC_ADMINISTRATOR';
    if (token) {
      localStorage.setItem('examops_token', token);
    } else {
      localStorage.removeItem('examops_token');
    }
    if (user) {
      localStorage.setItem('examops_user', JSON.stringify(user));
      localStorage.setItem('examops_active_role', user.role);
    } else {
      localStorage.removeItem('examops_user');
      localStorage.removeItem('examops_active_role');
    }
  }

  getActiveRole() {
    return this.currentUser?.role || this.activeRole;
  }

  _formatParams(params = {}) {
    const formatted = { ...params };
    if (params.page_size && !params.limit) {
      formatted.limit = params.page_size;
      delete formatted.page_size;
    }
    if (params.page && params.offset === undefined) {
      const limit = formatted.limit || 50;
      formatted.offset = (params.page - 1) * limit;
      delete formatted.page;
    }
    Object.keys(formatted).forEach((k) => {
      if (formatted[k] === undefined || formatted[k] === null || formatted[k] === '') {
        delete formatted[k];
      }
    });
    return formatted;
  }

  async request(endpoint, options = {}) {
    const url = `${API_BASE}${endpoint.startsWith('/') ? endpoint : `/${endpoint}`}`;
    const headers = {
      'Content-Type': 'application/json',
      ...(this.token ? { Authorization: `Bearer ${this.token}` } : {}),
      ...options.headers,
    };

    const config = {
      ...options,
      headers,
    };

    try {
      const response = await fetch(url, config);
      
      // Handle file downloads
      if (response.headers.get('content-type')?.includes('text/csv')) {
        return await response.text();
      }

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || data.message || `Request failed with status ${response.status}`);
      }
      if (Array.isArray(data)) {
        data.items = data;
        data.total = data.length;
      }
      return data;
    } catch (err) {
      console.error(`API Error [${endpoint}]:`, err);
      throw err;
    }
  }

  // Auth & Profile
  async login(email, password = null) {
    const data = await this.request('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
    this.setSession(data.access_token, data.user);
    return data;
  }

  async devSwitchRole(role) {
    const data = await this.request('/auth/dev-switch-role', {
      method: 'POST',
      body: JSON.stringify({ role }),
    });
    this.setSession(data.access_token, data.user);
    return data;
  }

  async getMe() {
    return this.request('/auth/me');
  }

  async listProfiles() {
    return this.request('/auth/profiles');
  }

  // Master Data
  async listStudents(params = {}) {
    const q = new URLSearchParams(this._formatParams(params)).toString();
    return this.request(`/students${q ? `?${q}` : ''}`);
  }

  async getStudent(id) {
    return this.request(`/students/${id}`);
  }

  async getStudentSchedule(id) {
    return this.request(`/students/${id}/schedule`);
  }

  async listCourses(params = {}) {
    const q = new URLSearchParams(this._formatParams(params)).toString();
    return this.request(`/courses${q ? `?${q}` : ''}`);
  }

  async listEnrollments(params = {}) {
    const q = new URLSearchParams(this._formatParams(params)).toString();
    return this.request(`/enrollments${q ? `?${q}` : ''}`);
  }

  async listExams(params = {}) {
    const q = new URLSearchParams(this._formatParams(params)).toString();
    return this.request(`/exams${q ? `?${q}` : ''}`);
  }

  async getExam(id) {
    return this.request(`/exams/${id}`);
  }

  async getExamRequirements(id) {
    return this.request(`/exams/${id}/requirements`);
  }

  async listRooms(params = {}) {
    const q = new URLSearchParams(this._formatParams(params)).toString();
    return this.request(`/rooms${q ? `?${q}` : ''}`);
  }

  async getRoom(id) {
    return this.request(`/rooms/${id}`);
  }

  async listInvigilators(params = {}) {
    const q = new URLSearchParams(this._formatParams(params)).toString();
    return this.request(`/invigilators${q ? `?${q}` : ''}`);
  }

  async getInvigilator(id) {
    return this.request(`/invigilators/${id}`);
  }

  async getInvigilatorSchedule(id) {
    return this.request(`/invigilators/${id}/schedule`);
  }

  async listAccommodations(params = {}) {
    const q = new URLSearchParams(this._formatParams(params)).toString();
    return this.request(`/accommodations${q ? `?${q}` : ''}`);
  }

  async getAccommodationNotes(id) {
    return this.request(`/accommodations/${id}/notes`);
  }

  // Scheduling Lifecycle
  async listRuns() {
    return this.request('/scheduling/runs');
  }

  async createRun(payload) {
    return this.request('/scheduling/runs', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  }

  async getRun(id) {
    return this.request(`/scheduling/runs/${id}`);
  }

  async executeRun(id) {
    return this.request(`/scheduling/runs/${id}/execute`, {
      method: 'POST',
    });
  }

  async getRunAssignments(id, params = {}) {
    const q = new URLSearchParams(this._formatParams(params)).toString();
    return this.request(`/scheduling/runs/${id}/assignments${q ? `?${q}` : ''}`);
  }

  async getRunDecisions(id, params = {}) {
    const q = new URLSearchParams(this._formatParams(params)).toString();
    return this.request(`/scheduling/runs/${id}/decisions${q ? `?${q}` : ''}`);
  }

  async getRunIssues(id) {
    return this.request(`/scheduling/runs/${id}/issues`);
  }

  async approveRun(id) {
    return this.request(`/scheduling/runs/${id}/approve`, {
      method: 'POST',
    });
  }

  async publishRun(id) {
    return this.request(`/scheduling/runs/${id}/publish`, {
      method: 'POST',
    });
  }

  // Analytics & Exports
  async getAnalyticsOverview() {
    return this.request('/analytics/overview');
  }

  async getRunReconciliation(id) {
    return this.request(`/analytics/runs/${id}/reconciliation`);
  }

  async listAuditLogs(params = {}) {
    const q = new URLSearchParams(this._formatParams(params)).toString();
    return this.request(`/audit/logs${q ? `?${q}` : ''}`);
  }

  async exportRunCsv(id) {
    return this.request(`/export/runs/${id}/csv`);
  }

  async exportRunJson(id) {
    return this.request(`/export/runs/${id}/json`);
  }
}

export const api = new ApiClient();
