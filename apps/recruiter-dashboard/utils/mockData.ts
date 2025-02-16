import { ApplicantType, ShortlistedApplicant } from './types';

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

export const shortlistedApplicants: ShortlistedApplicant[] = [
  {
    id: '1',
    name: 'Sarah Chen',
    profileImage: '/placeholder-avatar.png',
    currentPosition: 'ML Engineer at Stanford AI Lab',
    experience: [
      {
        company: 'Stanford AI Lab',
        title: 'ML Engineer',
        startDate: '2022',
        endDate: 'Present',
        description: 'Leading research in transformer architectures',
      }
    ],
    skills: ['Python', 'PyTorch', 'Transformers', 'MLOps'],
    projects: [
      {
        name: 'Attention Mechanisms',
        description: 'Novel attention mechanism for transformer models',
        metrics: {
          citations: 45,
          implementations: 12
        }
      }
    ],
    outreachStatus: {
      stage: 'initial',
      linkedin: 'pending',
      email: 'pending',
      call: 'scheduled'
    },
    callStatus: 'not_started'
  },
  {
    id: '2',
    name: 'Michael Rodriguez',
    profileImage: '/placeholder-avatar.png',
    currentPosition: 'Senior Data Scientist at Google',
    experience: [
      {
        company: 'Google',
        title: 'Senior Data Scientist',
        startDate: '2021',
        endDate: 'Present',
        description: 'Leading ML infrastructure development',
      }
    ],
    skills: ['Python', 'TensorFlow', 'Kubernetes', 'GCP'],
    projects: [
      {
        name: 'ML Pipeline Optimization',
        description: 'Scalable ML training infrastructure',
        metrics: {
          deployments: 100,
          efficiency: 40
        }
      }
    ],
    outreachStatus: {
      stage: 'initial',
      linkedin: 'pending',
      email: 'pending',
      call: 'scheduled'
    },
    callStatus: 'in_progress'
  },
  {
    id: '3',
    name: 'Priya Patel',
    currentPosition: 'Research Engineer at DeepMind',
    callStatus: 'conversation_ended' as const,
    callSummary: 'Strong technical background in ML/AI. Excellent communication skills. Demonstrated deep knowledge of transformer architectures and practical implementation experience.',
    screeningScore: 92,
    experience: []
  },
  {
    id: '4',
    name: 'James Wilson',
    currentPosition: 'Computer Vision Engineer at Tesla',
    callStatus: 'not_started' as const,
    experience: []
  },
  {
    id: '5',
    name: 'Emma Thompson',
    currentPosition: 'NLP Researcher at OpenAI',
    callStatus: 'not_started' as const,
    experience: []
  }
]; 