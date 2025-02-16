'use client';

import { useState } from 'react';
import { FaLinkedin, FaEnvelope } from 'react-icons/fa';
import { generateOutreachMessages } from '../../../utils/outreachGenerator';
import { mockApplicants } from '../../../utils/mockData';

export default function OutreachPage({ params }: { params: { id: string } }) {
  const [selectedPlatform, setSelectedPlatform] = useState<'linkedin' | 'email' | null>(null);
  const [message, setMessage] = useState('');

  // Find the applicant using the ID from params
  const applicant = mockApplicants.find(a => a.id === params.id);

  if (!applicant) {
    return <div>Applicant not found</div>;
  }

  const handlePlatformSelect = (platform: 'linkedin' | 'email') => {
    setSelectedPlatform(platform);
    const messages = generateOutreachMessages(applicant);
    setMessage(messages[platform]);
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      <h1 className="text-2xl font-bold mb-6">Send Outreach to {applicant.name}</h1>
      
      <div className="flex gap-4 mb-8">
        <button
          onClick={() => handlePlatformSelect('linkedin')}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg ${
            selectedPlatform === 'linkedin' 
              ? 'bg-blue-600 text-white' 
              : 'bg-gray-100 hover:bg-gray-200'
          }`}
        >
          <FaLinkedin className="text-xl" />
          LinkedIn
        </button>
        
        <button
          onClick={() => handlePlatformSelect('email')}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg ${
            selectedPlatform === 'email' 
              ? 'bg-blue-600 text-white' 
              : 'bg-gray-100 hover:bg-gray-200'
          }`}
        >
          <FaEnvelope className="text-xl" />
          Email
        </button>
      </div>

      {selectedPlatform && (
        <div>
          <h2 className="text-lg font-semibold mb-4">
            {selectedPlatform === 'linkedin' ? 'LinkedIn Message' : 'Email Message'}
          </h2>
          <textarea
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            className="w-full h-64 p-4 border rounded-lg"
            placeholder="Your message here..."
          />
          <button
            className="mt-4 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Send {selectedPlatform === 'linkedin' ? 'LinkedIn Message' : 'Email'}
          </button>
        </div>
      )}
    </div>
  );
} 