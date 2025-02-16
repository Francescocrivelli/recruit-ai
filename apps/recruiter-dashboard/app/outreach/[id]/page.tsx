'use client';

import { useState } from 'react';
import { FaLinkedin, FaEnvelope } from 'react-icons/fa';
import { generateOutreachMessages } from '../../../utils/outreachGenerator';
import { mockApplicants } from '../../../utils/mockData';

export default function OutreachPage({ params }: { params: { id: string } }) {
  const [selectedChannel, setSelectedChannel] = useState<'linkedin' | 'email'>('linkedin');
  const [editedMessage, setEditedMessage] = useState<string>('');
  const [isSending, setIsSending] = useState(false);
  
  const applicant = mockApplicants.find(a => a.id === params.id);
  if (!applicant) return <div>Applicant not found</div>;

  const messages = generateOutreachMessages(applicant);

  // Initialize edited message when channel changes
  const handleChannelSelect = (channel: 'linkedin' | 'email') => {
    setSelectedChannel(channel);
    setEditedMessage(messages[channel]);
  };

  const handleSendMessage = async () => {
    setIsSending(true);
    try {
      // TODO: Replace with actual API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      console.log(`Sending ${selectedChannel} message:`, editedMessage);
      
      // Show success message
      alert('Message sent successfully!');
    } catch (error) {
      console.error('Error sending message:', error);
      alert('Failed to send message. Please try again.');
    } finally {
      setIsSending(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-8">
      <h1 className="text-3xl font-bold mb-8">Send Outreach</h1>
      
      <div className="flex gap-4 mb-6">
        <button
          onClick={() => handleChannelSelect('linkedin')}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg ${
            selectedChannel === 'linkedin' 
              ? 'bg-blue-600 text-white' 
              : 'bg-gray-100 text-gray-700'
          }`}
        >
          <FaLinkedin /> LinkedIn
        </button>
        <button
          onClick={() => handleChannelSelect('email')}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg ${
            selectedChannel === 'email' 
              ? 'bg-blue-600 text-white' 
              : 'bg-gray-100 text-gray-700'
          }`}
        >
          <FaEnvelope /> Email
        </button>
      </div>

      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-xl font-semibold mb-4">Message Preview</h2>
        <textarea
          value={editedMessage || messages[selectedChannel]}
          onChange={(e) => setEditedMessage(e.target.value)}
          className="w-full h-64 p-4 rounded-lg border border-gray-200 font-mono bg-gray-50 resize-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
        <div className="mt-4 flex justify-end">
          <button
            onClick={handleSendMessage}
            disabled={isSending}
            className={`px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors ${
              isSending ? 'opacity-50 cursor-not-allowed' : ''
            }`}
          >
            {isSending ? 'Sending...' : 'Send Message'}
          </button>
        </div>
      </div>
    </div>
  );
} 