'use client';

import { useState } from 'react';
import { mockApplicants } from '../utils/mockData';
import { ApplicantCard } from '../../../packages/ui/src/ApplicantCard/ApplicantCard';

export default function HomePage() {
  const [searchQuery, setSearchQuery] = useState('');

  return (
    <div className="max-w-7xl mx-auto p-8">
      <h1 className="text-4xl font-bold mb-8">Recruiter Dashboard</h1>
      
      <div className="flex gap-4 mb-8">
        <input
          type="text"
          placeholder="Try searching 'Python developer with 4 years experience'"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="flex-1 px-4 py-2 rounded-lg border border-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
        <button className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
          Search
        </button>
      </div>

      <div className="space-y-6">
        {mockApplicants.map((applicant) => (
          <ApplicantCard key={applicant.id} applicant={applicant} />
        ))}
      </div>
    </div>
  );
} 