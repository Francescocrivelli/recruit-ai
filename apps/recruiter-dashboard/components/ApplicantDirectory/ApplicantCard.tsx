'use client';

import { useState } from 'react';
import Image from 'next/image';
import ProjectsMetrics from '../ProjectsMetrics';
import OutreachSection from '../OutreachSection';
import { useRouter } from 'next/navigation';
import { ApplicantType } from '../../utils/types';

interface ApplicantCardProps {
  applicant: ApplicantType;
}

export function ApplicantCard({ applicant }: ApplicantCardProps) {
  const router = useRouter();
  const [isProjectsOpen, setIsProjectsOpen] = useState(false);
  const [isOutreachOpen, setIsOutreachOpen] = useState(false);

  const handleSendOutreach = () => {
    router.push(`/outreach/${applicant.id}`);
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6 mb-4">
      <div className="flex items-start gap-4">
        <div className="w-16 h-16 relative rounded-full overflow-hidden">
          <Image
            src={applicant.profileImage || '/placeholder-avatar.png'}
            alt={applicant.name}
            fill
            className="object-cover"
          />
        </div>
        
        <div className="flex-1">
          <div className="flex justify-between items-start">
            <div>
              <h3 className="text-xl font-semibold">{applicant.name}</h3>
              <p className="text-gray-600">{applicant.currentPosition}</p>
            </div>
          </div>
          
          <div className="mt-4">
            <h4 className="font-medium">Experience Highlights</h4>
            <p className="text-gray-700">
              {applicant.experience?.[0]?.description || 'No experience details available'}
            </p>
          </div>

          {applicant.skills && applicant.skills.length > 0 && (
            <div className="mt-4 flex flex-wrap gap-2">
              {applicant.skills.map((skill) => (
                <span 
                  key={skill}
                  className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm"
                >
                  {skill}
                </span>
              ))}
            </div>
          )}

          <div className="mt-6 space-y-4">
            <button
              onClick={() => setIsProjectsOpen(!isProjectsOpen)}
              className="w-full text-left px-4 py-2 bg-gray-50 rounded flex justify-between items-center"
            >
              <span>Projects & Metrics</span>
              <span>{isProjectsOpen ? '−' : '+'}</span>
            </button>
            {isProjectsOpen && <ProjectsMetrics projects={applicant.projects} />}

            <button
              onClick={() => setIsOutreachOpen(!isOutreachOpen)}
              className="w-full text-left px-4 py-2 bg-gray-50 rounded flex justify-between items-center"
            >
              <span>Outreach Status</span>
              <span>{isOutreachOpen ? '−' : '+'}</span>
            </button>
            {isOutreachOpen && <OutreachSection applicant={applicant} />}

            <div className="mt-4">
              <button
                onClick={handleSendOutreach}
                className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                Send Outreach
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
} 