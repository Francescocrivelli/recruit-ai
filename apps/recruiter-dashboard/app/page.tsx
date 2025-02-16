'use client';

import { useState } from 'react';
import { mockApplicants } from '../utils/mockData';
import { ApplicantCard } from '../../../packages/ui/src/ApplicantCard/ApplicantCard';
import { apiClient } from '../utils/api-client';
import { ApplicantType } from '../utils/types';

export default function HomePage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [applicants, setApplicants] = useState<ApplicantType[]>(mockApplicants);
  const [isLoading, setIsLoading] = useState(false);

  const handleSearch = async (query: string) => {
    setIsLoading(true);
    try {
      const results = await apiClient.searchApplicants(query);
      setApplicants(results);
    } catch (error) {
      console.error('Search failed:', error);
      // Show error message to user
    } finally {
      setIsLoading(false);
    }
  };

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
        <button 
          onClick={() => handleSearch(searchQuery)}
          className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          Search
        </button>
      </div>

      <div className="space-y-6">
        {applicants.map((applicant) => (
          <ApplicantCard key={applicant.id} applicant={applicant} />
        ))}
      </div>
    </div>
  );
} 