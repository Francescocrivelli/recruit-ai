export interface ChunkType {
  section: string;
  content: string;
  score: number;
}

export interface ApplicantType {
  id: string;
  name: string;
  currentPosition: string;
  profileImage: string;
  experience: Array<{
    title: string;
    company: string;
    description: string;
  }>;
  skills: string[];
  projects: Array<{
    name: string;
    description: string;
  }>;
  publications: Array<{
    title: string;
    summary: string;
  }>;
  outreachStatus: {
    stage: 'initial' | 'pending' | 'stage_2';
    linkedin?: 'pending' | 'sent' | 'responded';
    email?: 'pending' | 'sent' | 'responded';
    call?: 'scheduled' | 'completed' | 'no-show';
  };
  score: number;
  education: ChunkType[];
  publications: ChunkType[];
  experience: ChunkType[];
}

export type CallStatus = 'not_started' | 'picked_up' | 'in_progress' | 'conversation_ended' | 'hung_up' | 'rescheduled';

export interface ShortlistedApplicant extends ApplicantType {
  callStatus: CallStatus;
  callSummary?: string;
  screeningScore?: number;
  rescheduleDate?: string;
} 