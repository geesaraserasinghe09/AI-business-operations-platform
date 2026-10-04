export type UserRole = 'admin' | 'manager' | 'employee';

export interface User {
  id: string;
  email: string;
  full_name: string;
  role: UserRole;
  is_active: boolean;
  organization_id?: string;
  created_at: string;
}

export type WorkflowStatus = 
  | 'draft' 
  | 'pending_approval' 
  | 'running' 
  | 'waiting_for_human' 
  | 'completed' 
  | 'failed' 
  | 'cancelled';

export type StepStatus = 
  | 'pending' 
  | 'running' 
  | 'waiting_approval' 
  | 'completed' 
  | 'failed' 
  | 'skipped';

export type AgentType = 'planner' | 'finance' | 'support' | 'document' | 'reporting';

export interface WorkflowStep {
  id: string;
  workflow_id: string;
  step_order: number;
  name: string;
  description?: string;
  agent_type: AgentType;
  status: StepStatus;
  input_data: Record<string, any>;
  output_data: Record<string, any>;
  execution_time_ms: number;
  error_message?: string;
  requires_approval: boolean;
  created_at: string;
  completed_at?: string;
  approval?: Approval;
}

export type RiskLevel = 'low' | 'medium' | 'high' | 'critical';
export type ApprovalStatus = 'pending' | 'approved' | 'rejected' | 'modified';

export interface Approval {
  id: string;
  workflow_id: string;
  step_id?: string;
  action_type: string;
  title: string;
  description: string;
  reason: string;
  ai_explanation: string;
  data_payload: Record<string, any>;
  agent_name: string;
  risk_level: RiskLevel;
  status: ApprovalStatus;
  requested_at: string;
  reviewed_at?: string;
  reviewed_by_id?: string;
  review_notes?: string;
  modification_payload?: Record<string, any>;
}

export interface Workflow {
  id: string;
  title: string;
  description?: string;
  prompt: string;
  status: WorkflowStatus;
  current_step_index: number;
  created_by_id?: string;
  created_at: string;
  updated_at: string;
  completed_at?: string;
  execution_metadata: Record<string, any>;
  summary_result?: string;
  steps: WorkflowStep[];
  approvals: Approval[];
}

export type TaskPriority = 'low' | 'medium' | 'high' | 'urgent';
export type TaskStatus = 'pending' | 'in_progress' | 'completed' | 'failed' | 'blocked';

export interface Task {
  id: string;
  title: string;
  description?: string;
  priority: TaskPriority;
  status: TaskStatus;
  assigned_agent?: string;
  created_by_id?: string;
  workflow_id?: string;
  created_at: string;
  updated_at: string;
  due_date?: string;
  completed_at?: string;
  result_data: Record<string, any>;
  approval_status?: string;
}

export interface DocumentChunk {
  id: string;
  document_id: string;
  chunk_index: number;
  content: string;
  metadata_info: Record<string, any>;
}

export interface DocumentItem {
  id: string;
  filename: string;
  file_type: string;
  file_size: number;
  content_summary?: string;
  uploaded_by_id?: string;
  created_at: string;
  chunks_count?: number;
  raw_text?: string;
  chunks?: DocumentChunk[];
}

export interface ReportItem {
  id: string;
  title: string;
  report_type: string;
  format: string;
  summary: string;
  content: string;
  metrics: Record<string, any>;
  generated_by_agent: string;
  workflow_id?: string;
  created_at: string;
}

export interface AgentMetric {
  id: string;
  agent_type: string;
  name: string;
  status: 'idle' | 'executing' | 'paused' | 'error';
  current_task?: string;
  total_tasks: number;
  successful_tasks: number;
  failed_tasks: number;
  avg_execution_time_ms: number;
  success_rate: number;
  last_active_at: string;
}

export interface DashboardStats {
  total_tasks: number;
  active_workflows: number;
  completed_workflows: number;
  pending_approvals: number;
  failed_workflows: number;
  total_revenue: number;
  total_tickets: number;
  open_tickets: number;
  system_health: string;
  agent_activity: AgentMetric[];
  recent_workflows: Array<{
    id: string;
    title: string;
    status: WorkflowStatus;
    created_at: string;
    steps_count: number;
  }>;
  monthly_sales_chart: Array<{
    month: string;
    sales: number;
    target: number;
  }>;
  ticket_distribution: Array<{
    name: string;
    value: number;
  }>;
}

export interface ActivityLog {
  id: string;
  user_id?: string;
  user_name?: string;
  action: string;
  agent?: string;
  workflow_id?: string;
  details: Record<string, any>;
  ip_address?: string;
  result_status: string;
  timestamp: string;
}

export interface NotificationItem {
  id: string;
  user_id?: string;
  title: string;
  message: string;
  type: string;
  is_read: boolean;
  link_url?: string;
  created_at: string;
}
