export interface ApplicantType {
  id: string;
  name: string;
  profileImage?: string;
  currentPosition: string;
  experience: Array<{
    company: string;
    title: string;
    startDate: string;
    endDate: string;
    description: string;
  }>;
  skills: string[];
  projects: Array<{
    name: string;
    description: string;
    metrics: {
      stars?: number;
      forks?: number;
      contributions?: number;
    };
  }>;
  outreachStatus: {
    stage: 'initial' | 'pending' | 'stage_2';
    linkedin?: 'pending' | 'sent' | 'responded';
    email?: 'pending' | 'sent' | 'responded';
    call?: 'scheduled' | 'completed' | 'no-show';
  };
}

export type CallStatus = 'not_started' | 'picked_up' | 'in_progress' | 'conversation_ended' | 'hung_up' | 'rescheduled';

export interface ShortlistedApplicant extends ApplicantType {
  callStatus: CallStatus;
  callSummary?: string;
  screeningScore?: number;
  rescheduleDate?: string;
} 