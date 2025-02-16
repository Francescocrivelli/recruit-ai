'use client';

import { useState } from 'react';
import type { StaticImageData } from 'next/image';
import Image from 'next/image';
import { useRouter } from 'next/navigation';

interface ApplicantCardProps {
  applicant: {
    id: string;
    name: string;
    profileImage?: string | StaticImageData;
    currentPosition: string;
    experience: Array<{
      company: string;
      title: string;
      description: string;
    }>;
    skills?: string[];
  };
}

export function ApplicantCard({ applicant }: ApplicantCardProps) {
  const router = useRouter();

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
              {applicant.experience && applicant.experience[0] 
                ? applicant.experience[0].description 
                : 'No experience details available'}
            </p>
          </div>

          <div className="mt-4 flex flex-wrap gap-2">
            {applicant.skills?.map((skill) => (
              <span 
                key={skill}
                className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm"
              >
                {skill}
              </span>
            ))}
          </div>

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
  );
}

