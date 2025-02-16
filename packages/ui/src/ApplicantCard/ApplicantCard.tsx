'use client';

import React from 'react';
import { useState } from 'react';
import type { StaticImageData } from 'next/image';
import Image from 'next/image';
import { useRouter } from 'next/navigation';

interface SectionContent {
  content: string;
  score: number;
}

interface ApplicantProps {
  applicant: {
    id: string;
    name: string;
    score: number;
    education: SectionContent[];
    experience: SectionContent[];
    publications: SectionContent[];
    personal_info: SectionContent[];
    awards: SectionContent[];
    research: SectionContent[];
  };
}

export function ApplicantCard({ applicant }: ApplicantProps) {
  const router = useRouter();

  const handleSendOutreach = () => {
    router.push(`/outreach/${applicant.id}`);
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex justify-between items-start mb-4">
        <div>
          <h2 className="text-xl font-bold">{applicant.name}</h2>
          <p className="text-gray-600">Match Score: {(applicant.score * 100).toFixed(1)}%</p>
        </div>
      </div>

      {/* Personal Info */}
      {applicant.personal_info.length > 0 && (
        <div className="mb-4">
          <h3 className="font-semibold text-gray-700">Contact Information</h3>
          <div className="mt-2 text-sm">
            {applicant.personal_info.map((info, i) => (
              <div key={i} className="whitespace-pre-line">{info.content}</div>
            ))}
          </div>
        </div>
      )}

      {/* Education */}
      {applicant.education.length > 0 && (
        <div className="mb-4">
          <h3 className="font-semibold text-gray-700">Education</h3>
          <div className="mt-2 space-y-2">
            {applicant.education.map((edu, i) => (
              <div key={i} className="text-sm whitespace-pre-line">{edu.content}</div>
            ))}
          </div>
        </div>
      )}

      {/* Experience */}
      {applicant.experience.length > 0 && (
        <div className="mb-4">
          <h3 className="font-semibold text-gray-700">Experience</h3>
          <div className="mt-2 space-y-2">
            {applicant.experience.map((exp, i) => (
              <div key={i} className="text-sm whitespace-pre-line">{exp.content}</div>
            ))}
          </div>
        </div>
      )}

      {/* Publications */}
      {applicant.publications.length > 0 && (
        <div className="mb-4">
          <h3 className="font-semibold text-gray-700">Publications</h3>
          <div className="mt-2 space-y-2">
            {applicant.publications.map((pub, i) => (
              <div key={i} className="text-sm whitespace-pre-line">{pub.content}</div>
            ))}
          </div>
        </div>
      )}

      {/* Research */}
      {applicant.research.length > 0 && (
        <div className="mb-4">
          <h3 className="font-semibold text-gray-700">Research</h3>
          <div className="mt-2 space-y-2">
            {applicant.research.map((res, i) => (
              <div key={i} className="text-sm whitespace-pre-line">{res.content}</div>
            ))}
          </div>
        </div>
      )}

      {/* Awards */}
      {applicant.awards.length > 0 && (
        <div className="mb-4">
          <h3 className="font-semibold text-gray-700">Awards</h3>
          <div className="mt-2 space-y-2">
            {applicant.awards.map((award, i) => (
              <div key={i} className="text-sm whitespace-pre-line">{award.content}</div>
            ))}
          </div>
        </div>
      )}

      <div className="mt-4">
        <button
          onClick={handleSendOutreach}
          className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          Send Outreach
        </button>
      </div>
    </div>
  );
}

