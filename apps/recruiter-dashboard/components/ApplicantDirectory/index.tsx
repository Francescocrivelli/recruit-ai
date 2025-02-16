import { ApplicantType } from '../../utils/types';
import ApplicantCard from './ApplicantCard';

interface ApplicantDirectoryProps {
  applicants: ApplicantType[];
}

export default function ApplicantDirectory({ applicants }: ApplicantDirectoryProps) {
  if (applicants.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">
          No applicants found. Try adjusting your search criteria.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {applicants.map((applicant) => (
        <ApplicantCard key={applicant.id} applicant={applicant} />
      ))}
    </div>
  );
} 