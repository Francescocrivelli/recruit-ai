import type { ApplicantType, ShortlistedApplicant } from './types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const apiClient = {
  // Search applicants
  async searchApplicants(query: string): Promise<ApplicantType[]> {
    const response = await fetch(`${API_BASE_URL}/api/search?q=${encodeURIComponent(query)}`);
    if (!response.ok) throw new Error('Search failed');
    return response.json();
  },

  // Initiate call
  async initiateCall(applicantId: string): Promise<boolean> {
    const response = await fetch(`${API_BASE_URL}/api/call/initiate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ applicantId })
    });
    if (!response.ok) throw new Error('Failed to initiate call');
    return response.json();
  },

  // Update call status
  async updateCallStatus(
    applicantId: string, 
    status: string, 
    data?: { summary?: string; score?: number }
  ): Promise<boolean> {
    const response = await fetch(`${API_BASE_URL}/api/call/status`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ applicantId, status, ...data })
    });
    if (!response.ok) throw new Error('Failed to update status');
    return response.json();
  }
}; 