'use client';

import { useState } from 'react';
import SearchBar from '../components/SearchBar';
import ApplicantDirectory from '../components/ApplicantDirectory';
import { ApplicantType } from '../utils/types';
import { mockApplicants } from '../utils/mockData';

export default function RecruiterDashboard() {
  const [searchQuery, setSearchQuery] = useState('');
  const [applicants, setApplicants] = useState<ApplicantType[]>(mockApplicants);
  const [isLoading, setIsLoading] = useState(false);

  const handleSearch = async (query: string) => {
    setIsLoading(true);
    try {
      // TODO: Replace with actual API call
      // Simulating API call with mock data
      setTimeout(() => {
        setApplicants(mockApplicants);
        setIsLoading(false);
      }, 1000);
    } catch (error) {
      console.error('Error searching applicants:', error);
      setIsLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-3xl font-bold mb-8">Recruiter Dashboard</h1>
        <SearchBar onSearch={handleSearch} />
        {isLoading ? (
          <div className="flex justify-center my-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900" />
          </div>
        ) : (
          <ApplicantDirectory applicants={applicants} />
        )}
      </div>
    </main>
  );
} 