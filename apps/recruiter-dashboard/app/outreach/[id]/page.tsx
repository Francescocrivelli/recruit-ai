'use client';

import { useState } from 'react';
import { FaLinkedin, FaEnvelope } from 'react-icons/fa';
import { generateOutreachMessage } from '../../../utils/outreachGenerator';
import { mockApplicants } from '../../../utils/mockData';

export default function OutreachPage({ params }: { params: { id: string } }) {
  const [selectedChannel, setSelectedChannel] = useState<'linkedin' | 'email' | null>(null);
  const [message, setMessage] = useState('');
  
  const applicant = mockApplicants.find(a => a.id === params.id);
  
  if (!applicant) return <div>Applicant not found</div>;

  const handleChannelSelect = (channel: 'linkedin' | 'email') => {
    setSelectedChannel(channel);
    const generatedMessage = generateOutreachMessage(applicant, channel);
    setMessage(generatedMessage);
  };

  const handleSendOutreach = async () => {
    // TODO: Implement actual sending logic
    console.log(`Sending ${selectedChannel} message:`, message);
    // Update applicant status
    // Redirect to shortlist page
  };

  return (
    <div className="max-w-4xl mx-auto p-8">
      <h1 className="text-2xl font-bold mb-8">Send Outreach to {applicant.name}</h1>
      
      <div className="grid grid-cols-2 gap-6 mb-8">
        <button
          onClick={() => handleChannelSelect('linkedin')}
          className={`p-6 rounded-lg border-2 flex flex-col items-center gap-4 ${
            selectedChannel === 'linkedin' ? 'border-blue-600 bg-blue-50' : 'border-gray-200'
          }`}
        >
          <FaLinkedin className="w-8 h-8 text-blue-600" />
          <span className="font-medium">LinkedIn Message</span>
        </button>

        <button
          onClick={() => handleChannelSelect('email')}
          className={`p-6 rounded-lg border-2 flex flex-col items-center gap-4 ${
            selectedChannel === 'email' ? 'border-blue-600 bg-blue-50' : 'border-gray-200'
          }`}
        >
          <FaEnvelope className="w-8 h-8 text-blue-600" />
          <span className="font-medium">Email</span>
        </button>
      </div>

      {selectedChannel && (
        <div className="space-y-4">
          <h2 className="text-xl font-semibold">Generated Message</h2>
          <textarea
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            className="w-full h-64 p-4 rounded-lg border border-gray-300"
          />
          <button
            onClick={handleSendOutreach}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Send Message
          </button>
        </div>
      )}
    </div>
  );
} 