import type {
  RunClassifierRequest,
  TestResult,
  TestSummary,
  AppConfig,
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  private async request<T>(
    endpoint: string,
    options?: RequestInit
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
      throw new Error(error.detail || `HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  async runTest(request: RunClassifierRequest): Promise<TestResult> {
    return this.request<TestResult>('/api/tests/run', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  async getTests(): Promise<TestSummary[]> {
    return this.request<TestSummary[]>('/api/tests');
  }

  async getTest(testId: string): Promise<TestResult> {
    return this.request<TestResult>(`/api/tests/${testId}`);
  }

  async deleteTest(testId: string): Promise<void> {
    return this.request<void>(`/api/tests/${testId}`, {
      method: 'DELETE',
    });
  }

  async getConfig(): Promise<AppConfig> {
    return this.request<AppConfig>('/api/config');
  }

  async healthCheck(): Promise<{ status: string }> {
    return this.request<{ status: string }>('/health');
  }
}

export const apiClient = new ApiClient();
