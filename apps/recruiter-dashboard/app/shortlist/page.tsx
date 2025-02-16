'use client';

import { useState } from 'react';
import { shortlistedApplicants } from '../../utils/mockData';

type CallStatus = 'not_started' | 'picked_up' | 'in_progress' | 'conversation_ended' | 'hung_up' | 'rescheduled';

export default function ShortlistPage() {
  const [applicants, setApplicants] = useState(shortlistedApplicants);

  const handleCallButton = async (applicantId: string) => {
    try {
      // TODO: Replace with actual API call
      console.log('Initiating call for applicant:', applicantId);
      
      setApplicants(current =>
        current.map(a =>
          a.id === applicantId
            ? { ...a, callStatus: 'in_progress' as CallStatus }
            : a
        )
      );
    } catch (error) {
      console.error('Error initiating call:', error);
    }
  };

  const getStatusDisplay = (status: CallStatus) => {
    const statusStyles = {
      'picked_up': 'bg-blue-100 text-blue-800',
      'in_progress': 'bg-yellow-100 text-yellow-800',
      'conversation_ended': 'bg-green-100 text-green-800',
      'hung_up': 'bg-red-100 text-red-800',
      'rescheduled': 'bg-purple-100 text-purple-800',
      'not_started': 'bg-gray-100 text-gray-800'
    };

    return (
      <span className={`px-3 py-1 rounded-full text-sm font-medium ${statusStyles[status]}`}>
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
              <div className="space-y-4">
                <div>
                  <h3 className="text-xl font-semibold">{applicant.name}</h3>
                  <p className="text-gray-600">{applicant.currentPosition}</p>
                </div>

                <div className="flex items-center gap-4">
                  {getStatusDisplay(applicant.callStatus)}
                  
                  {applicant.callStatus === 'not_started' && (
                    <button
                      onClick={() => handleCallButton(applicant.id)}
                      className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                    >
                      Initiate Call
                    </button>
                  )}
                </div>

                {applicant.callStatus === 'conversation_ended' && (
                  <div className="mt-4 space-y-2">
                    <div className="bg-gray-50 p-4 rounded-lg">
                      <h4 className="font-medium text-lg mb-2">Call Summary</h4>
                      <p className="text-gray-700">{applicant.callSummary}</p>
                      <div className="mt-4">
                        <span className="font-medium">Screening Score: </span>
                        <span className={`text-lg ${
                          applicant.screeningScore >= 80 ? 'text-green-600' : 
                          applicant.screeningScore >= 60 ? 'text-yellow-600' : 
                          'text-red-600'
                        }`}>
                          {applicant.screeningScore}%
                        </span>
                      </div>
                    </div>
                  </div>
                )}

                {applicant.callStatus === 'rescheduled' && (
                  <div className="text-sm text-gray-600">
                    Rescheduled for: {new Date(applicant.rescheduleDate).toLocaleString()}
                  </div>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
} 