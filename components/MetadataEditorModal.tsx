import React, { useState } from 'react';
import { Button, Card } from './common';
import { GeneratedTrack } from '../types';

interface MetadataEditorModalProps {
  track: GeneratedTrack;
  onSave: (track: GeneratedTrack) => void;
  onClose: () => void;
}

export const MetadataEditorModal: React.FC<MetadataEditorModalProps> = ({
  track,
  onSave,
  onClose,
}) => {
  const [editedTrack, setEditedTrack] = useState<GeneratedTrack>(track);

  const handleMetadataChange = (field: 'artist' | 'album' | 'genre', value: string) => {
    setEditedTrack((prev) => ({
      ...prev,
      metadata: {
        ...prev.metadata,
        [field]: value,
      },
    }));
  };

  const handleNameChange = (value: string) => {
    setEditedTrack((prev) => ({
      ...prev,
      name: value,
    }));
  };

  const handleSave = () => {
    onSave(editedTrack);
    onClose();
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <Card className="max-w-md w-full space-y-4">
        <h3 className="text-xl font-bold text-white">Edit Track Metadata</h3>

        <div>
          <label className="block text-sm font-medium text-gray-300 mb-1">Track Name</label>
          <input
            type="text"
            value={editedTrack.name}
            onChange={(e) => handleNameChange(e.target.value)}
            className="w-full bg-gray-700 border border-gray-600 rounded-md shadow-sm py-2 px-3 text-white focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
            aria-label="Track name"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-300 mb-1">Artist</label>
          <input
            type="text"
            value={editedTrack.metadata?.artist || ''}
            onChange={(e) => handleMetadataChange('artist', e.target.value)}
            className="w-full bg-gray-700 border border-gray-600 rounded-md shadow-sm py-2 px-3 text-white focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
            aria-label="Artist name"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-300 mb-1">Album</label>
          <input
            type="text"
            value={editedTrack.metadata?.album || ''}
            onChange={(e) => handleMetadataChange('album', e.target.value)}
            className="w-full bg-gray-700 border border-gray-600 rounded-md shadow-sm py-2 px-3 text-white focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
            aria-label="Album name"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-300 mb-1">Genre</label>
          <input
            type="text"
            value={editedTrack.metadata?.genre || ''}
            onChange={(e) => handleMetadataChange('genre', e.target.value)}
            className="w-full bg-gray-700 border border-gray-600 rounded-md shadow-sm py-2 px-3 text-white focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
            aria-label="Genre"
          />
        </div>

        <div className="flex justify-end space-x-3 pt-2">
          <Button variant="secondary" onClick={onClose}>
            Cancel
          </Button>
          <Button onClick={handleSave}>Save</Button>
        </div>
      </Card>
    </div>
  );
};
