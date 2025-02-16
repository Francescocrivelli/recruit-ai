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
    matchScore: number;
    education: string[];
    experience: string[];
    publications: string[];
    projects: string[];
    awards: string[];
    personal_info?: any[];
    relevantChunks?: { content: string; score: number; section: string; subquery_index: number }[];
  };
}

export function ApplicantCard({ applicant }: ApplicantProps) {
  const [outreachSent, setOutreachSent] = useState(false);
  const [expandedChunks, setExpandedChunks] = useState<number[]>([]);
  const [isCallLoading, setIsCallLoading] = useState(false);
  const [callStatus, setCallStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle');

  const formatChunkContent = (content: string) => {
    return content.replace(
      /(Title|Authors|Journal\/Publisher|Year|Summary|Snippet|Description|Company|Location|Position|Role|Duration|Technologies|Skills|Project|Impact|Result):/g,
      '<strong>$1:</strong>'
    );
  };

  const toggleChunk = (index: number) => {
    setExpandedChunks(prev => 
      prev.includes(index) 
        ? prev.filter(i => i !== index)
        : [...prev, index]
    );
  };

  const handlePreScreenCall = async () => {
    setIsCallLoading(true);
    setCallStatus('loading');
    
    try {
      const response = await fetch('https://calltool3-684089940295.us-west2.run.app/create-call', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          userPhone: "+16179559106",
          instruction: `You are an AI interviewer, your name is Bryan conducting a pre-screening call for a computer scientist candidate. Your goal is to understand the candidate's technical projects, hands-on experience, and cultural fit with our company. Begin with a friendly welcome and ask the candidate to share a little about themselves. Naturally guide the conversation by asking about their recent impactful projects (including challenges faced, solutions implemented, and key learnings), their technical background and areas of expertise, and how they approach problem-solving and teamwork. Additionally, explore what they value in a workplace culture and encourage them to ask any questions about the role or the company. Keep the tone conversational, supportive, and professional, ensuring a natural flow of dialogue.`
        }),
      });

      if (!response.ok) {
        throw new Error('Call initiation failed');
      }

      setCallStatus('success');
    } catch (error) {
      console.error('Pre-screen call failed:', error);
      setCallStatus('error');
    } finally {
      setIsCallLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      {/* Header with name and score */}
      <div className="flex justify-between items-start mb-6">
        <div>
          <h2 className="text-2xl font-bold">{applicant.name}</h2>
          <p className="text-gray-600">Match Score: {Math.abs(applicant.matchScore).toFixed(1)}%</p>
        </div>
      </div>

      {/* Relevant Chunks Section */}
      <div className="mb-6">
        <h3 className="font-semibold text-gray-700 mb-2">Relevant Matches</h3>
        <div className="space-y-4">
          {applicant.relevantChunks?.map((chunk, index) => {
            const isExpanded = expandedChunks.includes(index);
            const formattedContent = formatChunkContent(chunk.content);
            const shouldTruncate = chunk.content.length > 300;

            return (
              <div key={index} className="bg-gray-50 p-4 rounded-lg">
                <div className="flex justify-between items-start">
                  <p className="font-medium text-gray-700">
                    Subquery {chunk.subquery_index} best chunk (score: {chunk.score.toFixed(3)}, section: {chunk.section})
                  </p>
                  {shouldTruncate && (
                    <button
                      onClick={() => toggleChunk(index)}
                      className="text-blue-600 hover:text-blue-700 text-sm font-medium"
                    >
                      {isExpanded ? 'Show Less' : 'Show More'}
                    </button>
                  )}
                </div>
                <div 
                  className={`mt-2 text-sm text-gray-600 whitespace-pre-wrap ${
                    !isExpanded && shouldTruncate ? 'line-clamp-3' : ''
                  }`}
                  dangerouslySetInnerHTML={{ 
                    __html: formattedContent
                  }}
                />
              </div>
            );
          })}
        </div>
      </div>

      {/* Education Section */}
      {applicant.education?.length > 0 && (
        <div className="mb-6">
          <h3 className="font-semibold text-gray-700 mb-2">Education</h3>
          <div className="space-y-2">
            {applicant.education.map((edu, index) => (
              <div key={index} className="text-sm text-gray-600">
                {edu}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Experience Section */}
      {applicant.experience?.length > 0 && (
        <div className="mb-6">
          <h3 className="font-semibold text-gray-700 mb-2">Experience</h3>
          <div className="space-y-2">
            {applicant.experience.map((exp, index) => (
              <div key={index} className="text-sm text-gray-600">
                {exp}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Publications Section */}
      {applicant.publications?.length > 0 && (
        <div className="mb-6">
          <h3 className="font-semibold text-gray-700 mb-2">Publications</h3>
          <div className="space-y-2">
            {applicant.publications.map((pub, index) => (
              <div key={index} className="text-sm text-gray-600">
                {pub}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Projects Section */}
      {applicant.projects?.length > 0 && (
        <div className="mb-6">
          <h3 className="font-semibold text-gray-700 mb-2">Projects</h3>
          <div className="space-y-2">
            {applicant.projects.map((project, index) => (
              <div key={index} className="text-sm text-gray-600">
                {project}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Awards Section */}
      {applicant.awards?.length > 0 && (
        <div className="mb-6">
          <h3 className="font-semibold text-gray-700 mb-2">Awards</h3>
          <div className="space-y-2">
            {applicant.awards.map((award, index) => (
              <div key={index} className="text-sm text-gray-600">
                {award}
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="flex gap-4 mt-4">
        <button
          onClick={() => setOutreachSent(true)}
          className={`flex-1 px-4 py-2 rounded-lg transition-colors ${
            outreachSent 
              ? 'bg-green-600 hover:bg-green-700' 
              : 'bg-blue-600 hover:bg-blue-700'
          } text-white`}
          disabled={outreachSent}
        >
          {outreachSent ? 'Sent!' : 'Send Outreach'}
        </button>

        <button
          onClick={handlePreScreenCall}
          disabled={isCallLoading || callStatus === 'success'}
          className={`flex-1 px-4 py-2 rounded-lg transition-colors ${
            callStatus === 'success'
              ? 'bg-green-600'
              : callStatus === 'error'
              ? 'bg-red-600 hover:bg-red-700'
              : 'bg-purple-600 hover:bg-purple-700'
          } text-white disabled:opacity-50 flex items-center justify-center gap-2`}
        >
          {isCallLoading ? (
            <>
              <span className="animate-spin">⌛</span>
              Initiating Call...
            </>
          ) : callStatus === 'success' ? (
            'Call Initiated!'
          ) : callStatus === 'error' ? (
            'Call Failed - Retry'
          ) : (
            'Pre-Screen Call'
          )}
        </button>
      </div>

      {callStatus === 'error' && (
        <p className="mt-2 text-sm text-red-600">
          Failed to initiate call. Please try again or contact support.
        </p>
      )}
    </div>
  );
}

