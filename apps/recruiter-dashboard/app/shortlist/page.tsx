'use client';

import { useState } from 'react';
import { initiateCall, updateCallStatus } from '../../utils/api';
import { CallStatus, ShortlistedApplicant } from '../../utils/types';
import { shortlistedApplicants } from '../../utils/mockData';

export default function ShortlistPage() {
  const [applicants, setApplicants] = useState<ShortlistedApplicant[]>(shortlistedApplicants);
  const [isLoading, setIsLoading] = useState<string | null>(null);

  const handleCallButton = async (applicantId: string) => {
    setIsLoading(applicantId);
    try {
      await initiateCall(applicantId);
      setApplicants(current =>
        current.map(a =>
          a.id === applicantId
            ? { ...a, callStatus: 'in_progress' }
            : a
        )
      );
    } catch (error) {
      console.error('Error initiating call:', error);
    } finally {
      setIsLoading(null);
    }
  };

  const getStatusBadge = (status: CallStatus) => {
    const styles = {
      'picked_up': 'bg-blue-100 text-blue-800',
      'in_progress': 'bg-yellow-100 text-yellow-800',
      'conversation_ended': 'bg-green-100 text-green-800',
      'hung_up': 'bg-red-100 text-red-800',
      'rescheduled': 'bg-purple-100 text-purple-800'
    };

    return (
      <span className={`px-3 py-1 rounded-full text-sm font-medium ${styles[status]}`}>
        {status.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')}
      </span>
    );
  };

  return (
    <div className="max-w-7xl mx-auto p-8">
      <h1 className="text-3xl font-bold mb-8">Shortlisted Applicants</h1>
      
      <div className="space-y-6">
        {applicants.map((applicant) => (
          <div key={applicant.id} className="bg-white rounded-lg shadow-md p-6">
            <div className="flex justify-between items-start">
              <div>
                <h3 className="text-xl font-semibold">{applicant.name}</h3>
                <p className="text-gray-600">{applicant.currentPosition}</p>
              </div>
              
              {!applicant.callStatus || applicant.callStatus === 'not_started' ? (
                <button
                  onClick={() => handleCallButton(applicant.id)}
                  disabled={isLoading === applicant.id}
                  className={`px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors ${
                    isLoading === applicant.id ? 'opacity-50 cursor-not-allowed' : ''
                  }`}
                >
                  {isLoading === applicant.id ? 'Initiating...' : 'Pre-Screen Call'}
                </button>
              ) : (
                getStatusBadge(applicant.callStatus)
              )}
            </div>

            {applicant.callStatus === 'conversation_ended' && (
              <div className="mt-4 bg-gray-50 p-4 rounded-lg">
                <div className="space-y-3">
                  <div>
                    <h4 className="font-medium text-lg mb-2">Call Summary</h4>
                    <p className="text-gray-700">{applicant.callSummary}</p>
                  </div>
                  <div className="flex items-center">
                    <span className="font-medium mr-2">Screening Score:</span>
                    <span className={`text-lg font-semibold ${
                      (applicant.screeningScore || 0) >= 80 ? 'text-green-600' : 
                      (applicant.screeningScore || 0) >= 60 ? 'text-yellow-600' : 
                      'text-red-600'
                    }`}>
                      {applicant.screeningScore}%
                    </span>
                  </div>
                </div>
              </div>
            )}

            {applicant.callStatus === 'rescheduled' && applicant.rescheduleDate && (
              <div className="mt-4 text-sm text-gray-600">
                Rescheduled for: {new Date(applicant.rescheduleDate).toLocaleString()}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
} 