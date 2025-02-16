'use client';

import { useState, useEffect } from 'react';
import { mockApplicants } from '../utils/mockData';
import { ApplicantCard } from '../../../packages/ui/src/ApplicantCard/ApplicantCard';
import { apiClient } from '../utils/api-client';
import { ApplicantType } from '../utils/types';

export default function HomePage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [applicants, setApplicants] = useState<ApplicantType[]>(mockApplicants);
  const [isLoading, setIsLoading] = useState(false);
  const [searchResults, setSearchResults] = useState<ApplicantType[]>([]);

  useEffect(() => {
    console.log('Search results updated:', searchResults);
  }, [searchResults]);

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;
    
    try {
      setIsLoading(true);
      console.log('Starting search with query:', searchQuery);
      
      const response = await fetch('http://localhost:8000/api/semantic-search', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: searchQuery.trim(),
          n_results: 400  // Match the API default
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        console.error('API error:', errorData);
        throw new Error(`Search failed: ${errorData.detail || response.statusText}`);
      }

      const data = await response.json();
      console.log('Received search results:', data);

      if (data.results && Array.isArray(data.results)) {
        const formattedResults: ApplicantType[] = data.results.map(result => ({
          id: result.candidate_id,
          name: result.candidate_name,
          matchScore: Math.round(result.score * 100),
          education: result.sections.education || [],
          experience: result.sections.experience || [],
          publications: result.sections.publications || [],
          projects: result.sections.projects || [],
          awards: result.sections.awards || [],
          relevantChunks: result.relevantChunks || [],
          personal_info: []
        }));

        console.log('Search Results:');
        formattedResults.forEach((result, index) => {
          console.log(`${index + 1}. ${result.name} (${result.matchScore}%)`);
        });

        setSearchResults(formattedResults);
      } else {
        setSearchResults([]);
      }
    } catch (error) {
      console.error('Search failed:', error);
      setSearchResults([]);
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
          onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
          className="flex-1 px-4 py-2 rounded-lg border border-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
        <button 
          onClick={handleSearch}
          className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
          disabled={isLoading || !searchQuery.trim()}
        >
          {isLoading ? (
            <span className="flex items-center gap-2">
              <span className="animate-spin">⌛</span>
              Searching...
            </span>
          ) : (
            'Search'
          )}
        </button>
      </div>

      <div className="space-y-6">
        {searchResults.length === 0 ? (
          <p>No results found</p>
        ) : (
          searchResults.map((applicant) => (
            <ApplicantCard key={applicant.id} applicant={applicant} />
          ))
        )}
      </div>
    </div>
  );
} 