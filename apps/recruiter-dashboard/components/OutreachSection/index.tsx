'use client';

import { useRouter } from 'next/navigation';
import { ApplicantType } from '../../utils/types';

interface OutreachSectionProps {
  applicant: ApplicantType;
}

export default function OutreachSection({ applicant }: OutreachSectionProps) {
  const router = useRouter();

  const handleSendOutreach = () => {
    router.push(`/outreach/${applicant.id}`);
  };

  return (
    <button
      onClick={handleSendOutreach}
      className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
    >
      Send Outreach
    </button>
  );
} 