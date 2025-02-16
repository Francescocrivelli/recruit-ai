'use client';

import { useState, useEffect } from 'react';
import { ApplicantCard } from '../../../../packages/ui/src/ApplicantCard/ApplicantCard';
import { ShortlistedApplicant } from '../../utils/types';

export default function ShortlistedPage() {
  const [shortlistedApplicants, setShortlistedApplicants] = useState<ShortlistedApplicant[]>([]);
  const [callInProgress, setCallInProgress] = useState<string | null>(null);

  const handlePreScreenCall = async (applicantId: string) => {
    setCallInProgress(applicantId);
    
    try {
      console.log('Initiating pre-screen call...');
      
      const response = await fetch('https://calltool3-684089940295.us-west2.run.app/create-call', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify({
          userPhone: "+16179559106",
          instruction: `You are an AI interviewer, your name is Bryan conducting a pre-screening call for a computer scientist candidate. Your goal is to understand the candidate's technical projects, hands-on experience, and cultural fit with our company. Begin with a friendly welcome and ask the candidate to share a little about themselves. Naturally guide the conversation by asking about their recent impactful projects (including challenges faced, solutions implemented, and key learnings), their technical background and areas of expertise, and how they approach problem-solving and teamwork. Additionally, explore what they value in a workplace culture and encourage them to ask any questions about the role or the company. Keep the tone conversational, supportive, and professional, ensuring a natural flow of dialogue.`
        }),
      });

      console.log('API Response Status:', response.status);
      
      const responseData = await response.json();
      console.log('API Response:', responseData);

      if (!response.ok) {
        throw new Error(`Call failed: ${responseData.message || response.statusText}`);
      }

      // Update applicant status
      setShortlistedApplicants(prev => 
        prev.map(app => 
          app.id === applicantId 
            ? { ...app, callStatus: 'in_progress' }
            : app
        )
      );

      // Show success message
      alert('Call initiated successfully!');

    } catch (error) {
      console.error('Failed to initiate call:', error);
      alert('Failed to initiate call. Please try again.');
    } finally {
      setCallInProgress(null);
    }
  };

  // Add this useEffect to log state changes
  useEffect(() => {
    console.log('Shortlisted applicants:', shortlistedApplicants);
  }, [shortlistedApplicants]);

  return (
    <div className="max-w-7xl mx-auto p-8">
      <h1 className="text-4xl font-bold mb-8">Shortlisted Candidates</h1>
      
      <div className="space-y-6">
        {shortlistedApplicants.map((applicant) => (
          <div key={applicant.id} className="flex items-start gap-4 bg-white rounded-lg shadow-md p-6">
            <div className="flex-grow">
              <h2 className="text-2xl font-bold">{applicant.name}</h2>
              <p className="text-gray-600">Match Score: {applicant.matchScore.toFixed(1)}%</p>
              
              {/* Call Status */}
              {applicant.callStatus && (
                <div className="mt-2">
                  <span className="text-sm font-medium text-gray-700">
                    Call Status: {applicant.callStatus.replace('_', ' ')}
                  </span>
                </div>
              )}
            </div>

            {/* Pre-Screen Call Button */}
            <button
              onClick={() => handlePreScreenCall(applicant.id)}
              disabled={callInProgress === applicant.id || applicant.callStatus === 'conversation_ended'}
              className={`px-4 py-2 rounded-lg transition-colors ${
                applicant.callStatus === 'conversation_ended'
                  ? 'bg-green-600'
                  : callInProgress === applicant.id
                  ? 'bg-yellow-500'
                  : 'bg-blue-600 hover:bg-blue-700'
              } text-white disabled:opacity-50 min-w-[150px] text-center`}
            >
              {callInProgress === applicant.id ? (
                <>
                  <span className="animate-spin inline-block mr-2">⌛</span>
                  Calling...
                </>
              ) : applicant.callStatus === 'conversation_ended' ? (
                'Call Completed'
              ) : (
                'Pre-Screen Call'
              )}
            </button>
          </div>
        ))}
      </div>
    </div>
  );
} 