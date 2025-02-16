import type { ApplicantType } from './types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const apiClient = {
  // Search applicants using ChromaDB
  async searchApplicants(query: string): Promise<ApplicantType[]> {
    const response = await fetch(`${API_BASE_URL}/api/search`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query })
    });
    if (!response.ok) throw new Error('Search failed');
    return response.json();
  },

  // Get applicant details
  async getApplicant(id: string): Promise<ApplicantType> {
    const response = await fetch(`${API_BASE_URL}/api/applicants/${id}`);
    if (!response.ok) throw new Error('Failed to fetch applicant');
    return response.json();
  },

  // Update applicant status
  async updateApplicantStatus(id: string, status: string): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/api/applicants/${id}/status`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status })
    });
    if (!response.ok) throw new Error('Failed to update status');
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