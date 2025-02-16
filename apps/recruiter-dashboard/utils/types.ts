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
    linkedin?: 'pending' | 'sent' | 'responded';
    email?: 'pending' | 'sent' | 'responded';
    call?: 'scheduled' | 'completed' | 'no-show';
  };
} 