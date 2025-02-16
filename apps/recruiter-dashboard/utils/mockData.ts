import { ApplicantType } from './types';

export const mockApplicants: ApplicantType[] = [
  {
    id: '1',
    name: 'John Doe',
    profileImage: '/placeholder-avatar.png',
    currentPosition: 'Senior Software Engineer at Tech Corp',
    experience: [
      {
        company: 'Tech Corp',
        title: 'Senior Software Engineer',
        startDate: '2020',
        endDate: 'Present',
        description: 'Led development of core platform services using Python and React',
      }
    ],
    skills: ['Python', 'React', 'AWS', 'Docker'],
    projects: [
      {
        name: 'Platform Services',
        description: 'Microservices architecture for handling user data',
        metrics: {
          stars: 45,
          forks: 12,
          contributions: 234
        }
      }
    ],
    outreachStatus: {
      stage: 'initial',
      linkedin: 'pending',
      email: 'sent',
      call: 'scheduled'
    }
  }
];

export const shortlistedApplicants = [
  {
    id: '1',
    name: 'Sarah Chen',
    currentPosition: 'ML Engineer at Stanford AI Lab',
    callStatus: 'picked_up',
    experience: [/* ... */],
  },
  {
    id: '2',
    name: 'Michael Rodriguez',
    currentPosition: 'Senior Data Scientist at Google',
    callStatus: 'in_progress',
    experience: [/* ... */],
  },
  {
    id: '3',
    name: 'Priya Patel',
    currentPosition: 'Research Engineer at DeepMind',
    callStatus: 'conversation_ended',
    callSummary: 'Strong technical background in ML/AI. Excellent communication skills. Demonstrated deep knowledge of transformer architectures and practical implementation experience.',
    screeningScore: 92,
    experience: [/* ... */],
  },
  {
    id: '4',
    name: 'James Wilson',
    currentPosition: 'Computer Vision Engineer at Tesla',
    callStatus: 'hung_up',
    experience: [/* ... */],
  },
  {
    id: '5',
    name: 'Emma Thompson',
    currentPosition: 'NLP Researcher at OpenAI',
    callStatus: 'rescheduled',
    rescheduleDate: '2024-02-20T15:00:00Z',
    experience: [/* ... */],
  },
]; 