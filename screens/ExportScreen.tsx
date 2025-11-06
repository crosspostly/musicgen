import React, { useState } from 'react';
import { Button, Card, Slider, Checkbox, ProgressBar } from '../components/common';
import { MetadataEditorModal } from '../components/MetadataEditorModal';
import { ArrowLeftIcon, PlayIcon, PauseIcon } from '../components/icons';
import { GeneratedTrack, LoopJobStatus } from '../types';
import { loopService, LoopCreationOptions } from '../services/loopService';

interface ExportScreenProps {
  track: GeneratedTrack;
  onDone: () => void;
}

interface LoopJobState {
  id: string;
  status: LoopJobStatus;
  progress: number;
  error?: string;
}

const ExportScreen: React.FC<ExportScreenProps> = ({ track, onDone }) => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [showMetadataEditor, setShowMetadataEditor] = useState(false);
  const [editedTrack, setEditedTrack] = useState<GeneratedTrack>(track);

  // Loop creation form state
  const [loopDuration, setLoopDuration] = useState(3600); // 1 hour in seconds
  const [loopFadeInOut, setLoopFadeInOut] = useState(true);
  const [loopFormat, setLoopFormat] = useState<'mp3' | 'wav'>('mp3');
  const [isCreatingLoop, setIsCreatingLoop] = useState(false);
  const [loopError, setLoopError] = useState<string | null>(null);

  const [loopJobs, setLoopJobs] = useState<LoopJobState[]>([]);
  const [completedLoops, setCompletedLoops] = useState<any[]>([]);

  const minLoopDuration = 60; // 1 minute
  const maxLoopDuration = 36000; // 10 hours

  const handleTogglePlayback = () => {
    setIsPlaying(!isPlaying);
  };

  const formatDuration = (seconds: number): string => loopService.formatDuration(seconds);

  const formatFileSize = (bytes: number): string => loopService.formatFileSize(bytes);

  const getStatusLabel = (status: LoopJobStatus): string => {
    const labels: Record<LoopJobStatus, string> = {
      [LoopJobStatus.PENDING]: 'Pending',
      [LoopJobStatus.ANALYZING]: 'Analyzing',
      [LoopJobStatus.RENDERING]: 'Rendering',
      [LoopJobStatus.EXPORTING]: 'Exporting',
      [LoopJobStatus.COMPLETED]: 'Completed',
      [LoopJobStatus.FAILED]: 'Failed',
    };
    return labels[status];
  };

  const handleCreateLoop = async () => {
    if (loopDuration < minLoopDuration || loopDuration > maxLoopDuration) {
      setLoopError(`Duration must be between ${formatDuration(minLoopDuration)} and ${formatDuration(maxLoopDuration)}`);
      return;
    }

    setIsCreatingLoop(true);
    setLoopError(null);

    try {
      const options: LoopCreationOptions = {
        trackId: editedTrack.id,
        duration: loopDuration,
        fadeInOut: loopFadeInOut,
        format: loopFormat,
      };

      const loopJob = await loopService.createLoopJob(options);
      const jobState: LoopJobState = {
        id: loopJob.id,
        status: loopJob.status,
        progress: loopJob.progress,
      };

      setLoopJobs((prev) => [...prev, jobState]);

      // Start polling for job status
      loopService.pollLoopJobStatus(
        loopJob.id,
        (updatedJob) => {
          setLoopJobs((prev) =>
            prev.map((job) =>
              job.id === loopJob.id
                ? {
                    id: updatedJob.id!,
                    status: updatedJob.status!,
                    progress: updatedJob.progress || 0,
                    error: updatedJob.error,
                  }
                : job
            )
          );
        },
        (completedJob) => {
          // Loop completed
          if (completedJob.resultUrl) {
            setCompletedLoops((prev) => [
              ...prev,
              {
                id: completedJob.id,
                format: loopFormat,
                duration: loopDuration,
                fileUrl: completedJob.resultUrl,
                filePath: completedJob.resultPath,
              },
            ]);
          }
        },
        (error) => {
          setLoopError(error.message);
        }
      );
    } catch (error) {
      setLoopError(error instanceof Error ? error.message : 'Failed to create loop');
    } finally {
      setIsCreatingLoop(false);
    }
  };

  const handleRetryLoop = () => {
    setLoopError(null);
    handleCreateLoop();
  };

  const handleClearLoop = (jobId: string) => {
    setLoopJobs((prev) => prev.filter((job) => job.id !== jobId));
  };

  const handleDownload = (url: string, filename: string) => {
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  };

  const handleMetadataSave = (updatedTrack: GeneratedTrack) => {
    setEditedTrack(updatedTrack);
    track = updatedTrack;
  };

  const getExportFilename = (format: 'mp3' | 'wav', isLoop: boolean, loopDuration?: number): string => {
    const artist = editedTrack.metadata?.artist || 'Unknown';
    const name = editedTrack.name || 'Track';
    const ext = format === 'mp3' ? 'mp3' : 'wav';

    if (isLoop && loopDuration) {
      return `${artist} - ${name} (Loop ${formatDuration(loopDuration)}).${ext}`;
    }
    return `${artist} - ${name}.${ext}`;
  };

  return (
    <div className="max-w-4xl mx-auto animate-fade-in">
      <Button variant="secondary" onClick={onDone} className="mb-4">
        <ArrowLeftIcon className="w-4 h-4" />
        Back to Model Selection
      </Button>

      <h2 className="text-3xl font-bold mb-6 text-center">Export Track</h2>

      {/* Track Details Section */}
      <Card className="mb-6">
        <div className="space-y-4">
          <div className="flex justify-between items-start">
            <div>
              <h3 className="text-2xl font-semibold text-white">{editedTrack.name}</h3>
              <p className="text-gray-400">by {editedTrack.metadata?.artist || 'Unknown Artist'}</p>
              <p className="text-gray-500 text-sm">Generated with {editedTrack.model}</p>
            </div>
            <Button variant="secondary" onClick={() => setShowMetadataEditor(true)}>
              Edit Metadata
            </Button>
          </div>

          {/* Audio Player */}
          <div className="bg-gray-900 rounded-lg p-4 flex items-center space-x-4">
            <button
              onClick={handleTogglePlayback}
              className="flex items-center justify-center w-10 h-10 bg-indigo-600 hover:bg-indigo-500 rounded-full transition-colors focus:ring-2 focus:ring-indigo-500"
              aria-label={isPlaying ? 'Pause' : 'Play'}
            >
              {isPlaying ? <PauseIcon className="w-5 h-5" /> : <PlayIcon className="w-5 h-5" />}
            </button>
            <div className="flex-1">
              <div className="h-1 bg-gray-700 rounded-full"></div>
              <p className="text-xs text-gray-400 mt-1">{formatDuration(editedTrack.duration)}</p>
            </div>
          </div>

          <div className="text-sm text-gray-400 border-t border-gray-700 pt-4">
            <p>Album: {editedTrack.metadata?.album || 'Not specified'}</p>
            <p>Genre: {editedTrack.metadata?.genre || 'Not specified'}</p>
          </div>
        </div>
      </Card>

      {/* Download Original Track */}
      <Card className="mb-6">
        <h3 className="text-lg font-semibold mb-4 text-white">Download Original Track</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {['mp3', 'wav'].map((format) => (
            <div key={format} className="bg-gray-900 rounded-lg p-4">
              <div className="flex justify-between items-start mb-3">
                <div>
                  <p className="font-semibold text-white uppercase">{format}</p>
                  <p className="text-sm text-gray-400">{formatDuration(editedTrack.duration)}</p>
                </div>
              </div>
              <Button
                onClick={() =>
                  handleDownload(
                    editedTrack.audioUrl,
                    getExportFilename(format as 'mp3' | 'wav', false)
                  )
                }
                className="w-full"
                disabled={!editedTrack.audioUrl}
              >
                Download {format.toUpperCase()}
              </Button>
            </div>
          ))}
        </div>
      </Card>

      {/* Create Seamless Loop Section */}
      <Card className="mb-6">
        <h3 className="text-lg font-semibold mb-4 text-white">Create Seamless Loop</h3>

        <div className="space-y-6">
          {/* Duration Slider */}
          <Slider
            label="Loop Duration"
            value={loopDuration}
            min={minLoopDuration}
            max={maxLoopDuration}
            step={60}
            onChange={(e) => setLoopDuration(Number(e.target.value))}
            unit=""
            valueLabel={formatDuration(loopDuration)}
            hint={`Range: ${formatDuration(minLoopDuration)} to ${formatDuration(maxLoopDuration)}`}
          />

          {/* Fade Toggle */}
          <div>
            <Checkbox
              label="Enable Fade In/Out (smooth transitions)"
              checked={loopFadeInOut}
              onChange={(e) => setLoopFadeInOut(e.target.checked)}
            />
            <p className="text-xs text-gray-500 mt-1">
              Applies fade-in at the start and fade-out at the end for seamless looping
            </p>
          </div>

          {/* Format Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">Export Format</label>
            <div className="grid grid-cols-2 gap-3">
              {['mp3', 'wav'].map((fmt) => (
                <button
                  key={fmt}
                  onClick={() => setLoopFormat(fmt as 'mp3' | 'wav')}
                  className={`py-2 px-3 rounded-md font-medium transition-colors ${
                    loopFormat === fmt
                      ? 'bg-indigo-600 text-white'
                      : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                  }`}
                  aria-pressed={loopFormat === fmt}
                >
                  {fmt.toUpperCase()}
                </button>
              ))}
            </div>
          </div>

          {/* Error Message */}
          {loopError && (
            <div className="bg-red-900 border border-red-700 rounded-lg p-3">
              <p className="text-red-200 text-sm">{loopError}</p>
              <div className="flex space-x-2 mt-2">
                <Button
                  variant="danger"
                  onClick={handleRetryLoop}
                  className="text-xs py-1 px-2"
                >
                  Retry
                </Button>
              </div>
            </div>
          )}

          {/* Submit Button */}
          <Button
            onClick={handleCreateLoop}
            disabled={isCreatingLoop}
            className="w-full"
          >
            {isCreatingLoop ? 'Creating Loop...' : '🔄 Create Loop'}
          </Button>
        </div>
      </Card>

      {/* Loop Jobs Progress */}
      {loopJobs.length > 0 && (
        <Card className="mb-6">
          <h3 className="text-lg font-semibold mb-4 text-white">Loop Creation Progress</h3>
          <div className="space-y-4">
            {loopJobs.map((job) => (
              <div key={job.id} className="bg-gray-900 rounded-lg p-4">
                <div className="flex justify-between items-start mb-2">
                  <div>
                    <p className="font-medium text-white">{getStatusLabel(job.status)}</p>
                    <p className="text-sm text-gray-400">{job.progress}%</p>
                  </div>
                  {job.status !== LoopJobStatus.COMPLETED && job.status !== LoopJobStatus.FAILED && (
                    <Button
                      variant="secondary"
                      onClick={() => handleClearLoop(job.id)}
                      className="text-xs py-1 px-2"
                    >
                      Clear
                    </Button>
                  )}
                </div>
                <ProgressBar progress={job.progress} className="mb-2" />
                {job.error && <p className="text-red-400 text-sm mt-1">{job.error}</p>}
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Completed Loops */}
      {completedLoops.length > 0 && (
        <Card className="mb-6">
          <h3 className="text-lg font-semibold mb-4 text-white">Available Loop Files</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {completedLoops.map((loop) => (
              <div key={loop.id} className="bg-gray-900 rounded-lg p-4">
                <div className="mb-3">
                  <p className="font-semibold text-white">
                    {loop.format.toUpperCase()} Loop - {formatDuration(loop.duration)}
                  </p>
                  {loop.filePath && (
                    <p className="text-xs text-gray-500 mt-1 truncate">
                      Saved to: {loop.filePath}
                    </p>
                  )}
                </div>
                <Button
                  onClick={() =>
                    handleDownload(loop.fileUrl, getExportFilename(loop.format, true, loop.duration))
                  }
                  className="w-full"
                >
                  Download Loop
                </Button>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* File Storage Info */}
      <Card className="text-center text-gray-400 text-sm">
        <p>📁 Files are saved to your local storage directory</p>
        <p className="text-xs mt-1">Location depends on your system and app configuration</p>
      </Card>

      {/* Metadata Editor Modal */}
      {showMetadataEditor && (
        <MetadataEditorModal
          track={editedTrack}
          onSave={handleMetadataSave}
          onClose={() => setShowMetadataEditor(false)}
        />
      )}
    </div>
  );
};

export default ExportScreen;
