export type ClassifierMode = 'sr' | 'qf' | 'both';

export type TestStatus = 'pending' | 'running' | 'completed' | 'failed';

export interface RunClassifierRequest {
  source_path: string;
  out_path: string;
  mode: ClassifierMode;
  use_filter: boolean;
  async_mode: boolean;
  max_concurrency: number;
}

export interface TestResult {
  test_id: string;
  status: TestStatus;
  source_path: string;
  out_path: string;
  mode: ClassifierMode;
  use_filter: boolean;
  async_mode: boolean;
  max_concurrency: number;
  created_at: string;
  started_at?: string;
  completed_at?: string;
  error_message?: string;
  total_emails?: number;
  processed_emails?: number;
  sr_positive?: number;
  sr_negative?: number;
  category_breakdown?: Record<string, number>;
}

export interface TestSummary {
  test_id: string;
  status: TestStatus;
  source_path: string;
  mode: ClassifierMode;
  created_at: string;
  completed_at?: string;
  total_emails?: number;
}

export interface AppConfig {
  default_mode: ClassifierMode;
  default_use_filter: boolean;
  default_async_mode: boolean;
  default_max_concurrency: number;
  max_concurrency_limit: number;
  allowed_file_types: string[];
}
