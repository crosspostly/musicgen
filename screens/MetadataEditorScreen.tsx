// Fix: Create a placeholder screen component to resolve compilation errors.
import React, { useState } from 'react';
import { Button, Card } from '../components/common';
import { GeneratedTrack } from '../types';

interface MetadataEditorScreenProps {
  track: GeneratedTrack;
  onBack: () => void;
  onComplete: (track: GeneratedTrack) => void;
}

const MetadataEditorScreen: React.FC<MetadataEditorScreenProps> = ({ track, onBack, onComplete }) => {
  const [editedTrack, setEditedTrack] = useState<GeneratedTrack>(track);

  const handleComplete = () => {
    // In a real app, you would save the metadata
    onComplete(editedTrack);
  };
  
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
      const { name, value } = e.target;
      setEditedTrack(prev => ({
          ...prev,
          metadata: {
              ...prev.metadata,
              [name]: value,
          }
      }));
  };

  return (
    <div className="max-w-2xl mx-auto animate-fade-in">
      <h2 className="text-3xl font-bold mb-6 text-center">Edit Metadata</h2>
      <Card className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-300">Track Name</label>
              <input type="text" value={editedTrack.name} onChange={e => setEditedTrack({...editedTrack, name: e.target.value})} className="mt-1 block w-full bg-gray-700 border border-gray-600 rounded-md shadow-sm py-2 px-3 text-white focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-300">Artist</label>
              <input type="text" name="artist" value={editedTrack.metadata?.artist || ''} onChange={handleInputChange} className="mt-1 block w-full bg-gray-700 border border-gray-600 rounded-md shadow-sm py-2 px-3 text-white focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-300">Album</label>
              <input type="text" name="album" value={editedTrack.metadata?.album || ''} onChange={handleInputChange} className="mt-1 block w-full bg-gray-700 border border-gray-600 rounded-md shadow-sm py-2 px-3 text-white focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm" />
            </div>
          <div className="flex justify-between items-center pt-4">
            <Button variant="secondary" onClick={onBack}>Back</Button>
            <Button onClick={handleComplete}>Save and Export</Button>
          </div>
      </Card>
    </div>
  );
};

export default MetadataEditorScreen;
