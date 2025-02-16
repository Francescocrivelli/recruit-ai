import { CallStatus } from './types';

export async function initiateCall(applicantId: string): Promise<boolean> {
  // TODO: Replace with actual API call to Tools folder
  console.log('Initiating call for applicant:', applicantId);
  return new Promise((resolve) => setTimeout(() => resolve(true), 1000));
}

export async function updateCallStatus(
  applicantId: string, 
  status: CallStatus, 
  data?: { 
    summary?: string; 
    score?: number;
    rescheduleDate?: string;
  }
): Promise<boolean> {
  // TODO: Replace with actual API call to Tools folder
  console.log('Updating call status:', { applicantId, status, data });
  return new Promise((resolve) => setTimeout(() => resolve(true), 500));
} 