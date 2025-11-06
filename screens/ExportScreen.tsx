// Fix: Create a placeholder screen component to resolve compilation errors.
import React from 'react';
import { Button, Card } from '../components/common';
import { GeneratedTrack } from '../types';

interface ExportScreenProps {
  track: GeneratedTrack;
  onDone: () => void;
}

const ExportScreen: React.FC<ExportScreenProps> = ({ track, onDone }) => {
  return (
    <div className="max-w-2xl mx-auto animate-fade-in">
      <h2 className="text-3xl font-bold mb-6 text-center">Export Track</h2>
      <Card>
        <div className="text-center space-y-4">
          <h3 className="text-xl font-semibold text-white">{track.name}</h3>
          <p className="text-gray-400">by {track.metadata?.artist || 'Unknown Artist'}</p>
          <p className="text-gray-500 text-sm">Generated with {track.model}</p>
          
          <div className="pt-4 space-x-4">
            <Button>Download WAV</Button>
            <Button>Download MP3</Button>
          </div>
        </div>
        
        <div className="mt-8 text-center">
            <Button variant="secondary" onClick={onDone}>Generate Another Track</Button>
        </div>
      </Card>
    </div>
  );
};

export default ExportScreen;
