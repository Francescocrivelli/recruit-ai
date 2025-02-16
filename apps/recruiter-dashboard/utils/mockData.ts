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
      linkedin: 'pending',
      email: 'sent',
      call: 'scheduled'
    }
  }
]; 