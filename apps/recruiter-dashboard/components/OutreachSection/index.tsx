import { ApplicantType } from '../../utils/types';

interface OutreachSectionProps {
  applicant: ApplicantType;
}

export default function OutreachSection({ applicant }: OutreachSectionProps) {
  const handleOutreach = (type: 'linkedin' | 'email' | 'call') => {
    // TODO: Implement outreach functionality
    console.log(`Initiating ${type} outreach to ${applicant.name}`);
  };

  return (
    <div className="mt-4 space-y-4">
      <div className="grid grid-cols-3 gap-4">
        <button
          onClick={() => handleOutreach('linkedin')}
          className={`px-4 py-2 rounded-lg text-sm font-medium ${
            applicant.outreachStatus.linkedin === 'sent'
              ? 'bg-green-100 text-green-800'
              : 'bg-blue-100 text-blue-800'
          }`}
        >
          LinkedIn {applicant.outreachStatus.linkedin || 'Not Started'}
        </button>
        <button
          onClick={() => handleOutreach('email')}
          className={`px-4 py-2 rounded-lg text-sm font-medium ${
            applicant.outreachStatus.email === 'sent'
              ? 'bg-green-100 text-green-800'
              : 'bg-blue-100 text-blue-800'
          }`}
        >
          Email {applicant.outreachStatus.email || 'Not Started'}
        </button>
        <button
          onClick={() => handleOutreach('call')}
          className={`px-4 py-2 rounded-lg text-sm font-medium ${
            applicant.outreachStatus.call === 'completed'
              ? 'bg-green-100 text-green-800'
              : 'bg-blue-100 text-blue-800'
          }`}
        >
          Call {applicant.outreachStatus.call || 'Not Scheduled'}
        </button>
      </div>
    </div>
  );
} 