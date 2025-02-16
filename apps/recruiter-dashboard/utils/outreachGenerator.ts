import { ApplicantType } from './types';

export function generateOutreachMessage(
  applicant: ApplicantType,
  channel: 'linkedin' | 'email'
): string {
  const templates = {
    linkedin: `Hi ${applicant.name},

I came across your profile and was particularly impressed by your experience at ${applicant.experience[0].company}. Your work on ${applicant.projects[0].name} caught my attention.

Would you be interested in discussing an exciting opportunity at our company?

Best regards,
[Recruiter Name]`,
    
    email: `Dear ${applicant.name},

I hope this email finds you well. I'm reaching out because your background, particularly your work at ${applicant.experience[0].company}, aligns perfectly with what we're looking for.

I'd love to schedule a call to discuss how your expertise in ${applicant.skills.join(', ')} could be a great fit for our team.

Looking forward to your response.

Best regards,
[Recruiter Name]
[Company Name]`
  };

  return templates[channel];
} 