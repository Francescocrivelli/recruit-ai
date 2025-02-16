import { ApplicantType } from './types';

export function generateOutreachMessages(applicant: ApplicantType) {
  // Helper function to get experience or project info safely
  const getExperienceText = () => {
    if (applicant.experience?.[0]) {
      return `your experience at ${applicant.experience[0].company}`;
    }
    return 'your professional background';
  };

  const getProjectText = () => {
    if (applicant.projects?.[0]) {
      return ` Your work on ${applicant.projects[0].name} caught my attention`;
    }
    return '';
  };

  return {
    linkedin: `Hi ${applicant.name},

I came across your profile and was particularly impressed by ${getExperienceText()}.${getProjectText()}.

Would you be interested in discussing an exciting opportunity at our company?

Best regards`,

    email: `Dear ${applicant.name},

I hope this email finds you well. I recently came across your profile and was impressed by ${getExperienceText()}.${getProjectText()}.

We have an exciting opportunity that I believe would be a great fit for someone with your expertise. Would you be open to having a brief conversation about it?

Looking forward to hearing from you.

Best regards`,
  };
} 