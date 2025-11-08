// Fix: Create a placeholder screen component to resolve compilation errors.
import React, { useState } from 'react';
import { Button, Card } from '../components/common';
import { ArrowLeftIcon } from '../components/icons';
import { GeneratedTrack, GenerationModel } from '../types';
import { apiClient, type ErrorType } from '../services/api';

interface GeneratorScreenProps {
  onBack: () => void;
  onGenerationComplete: (track: GeneratedTrack) => void;
}

/**
 * Map error types to user-friendly messages
 */
function getErrorMessage(errorType: ErrorType, detail?: string): string {
  switch (errorType) {
    case 'timeout':
      return 'The generation took too long (over 2 minutes). Please try with shorter lyrics or try again.';
    case 'network_error':
      return 'Cannot reach the server. Please check your internet connection and try again.';
    case 'http_error':
      return detail || 'The server encountered an error. Please try again in a moment.';
    default:
      return detail || 'An unexpected error occurred. Please try again.';
  }
}

const DiffRhythmGeneratorScreen: React.FC<GeneratorScreenProps> = ({ onBack, onGenerationComplete }) => {
    const [lyrics, setLyrics] = useState('Verse 1:\nПо городским улицам гуляю\nМечты и звёзды вспоминаю\n\nChorus:\nЭто песня моей жизни\nНаписана в сердце навеки');
    const [genre, setGenre] = useState('Pop');
    const [mood, setMood] = useState('Happy');
    const [gender, setGender] = useState('Male');
    const [isGenerating, setIsGenerating] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const handleGenerate = async () => {
        setIsGenerating(true);
        setError(null);
        try {
            const result = await apiClient.post('/api/generate', {
                model: GenerationModel.DIFFRHYTHM,
                prompt: lyrics,
                genre,
                mood,
                gender,
            });

            if (result.error) {
                const errorMessage = getErrorMessage(result.error.type, result.error.detail);
                setError(errorMessage);
                return;
            }

            if (!result.data) {
                setError('No response from server. Please try again.');
                return;
            }

            const data = result.data as { audioUrl?: string; duration?: number };
            const newTrack: GeneratedTrack = {
                id: new Date().toISOString(),
                name: lyrics.substring(0, 30).split('\n')[0] + '...',
                model: GenerationModel.DIFFRHYTHM,
                audioUrl: data.audioUrl || '',
                duration: data.duration || 0,
                createdAt: new Date(),
            };
            onGenerationComplete(newTrack);

        } catch (e: any) {
            setError('An unexpected error occurred. Please try again.');
            console.error('Unexpected error in generation:', e);
        } finally {
            setIsGenerating(false);
        }
    };

    return (
    <div className="max-w-4xl mx-auto animate-fade-in">
      <Button variant="secondary" onClick={onBack} className="mb-4" disabled={isGenerating}>
        <ArrowLeftIcon />
        Назад к выбору модели
      </Button>
      <h2 className="text-3xl font-bold mb-6 text-center">Генератор песен (DiffRhythm) ⭐</h2>
      <Card className="space-y-6">
          <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">Лирика / Текст песни</label>
              <textarea
                  value={lyrics}
                  onChange={e => setLyrics(e.target.value)}
                  className="w-full h-48 bg-gray-700 border border-gray-600 rounded-md shadow-sm p-3 text-white focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 font-mono text-sm"
                  placeholder="Verse 1: ..."
              />
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                  <label className="block text-sm font-medium text-gray-300">Жанр</label>
                  <select value={genre} onChange={e => setGenre(e.target.value)} className="mt-1 block w-full bg-gray-700 border border-gray-600 rounded-md shadow-sm py-2 px-3 text-white focus:outline-none focus:ring-indigo-500 focus:border-indigo-500">
                      <option>Pop</option><option>Rock</option><option>Rap</option><option>Electronic</option><option>Jazz</option>
                  </select>
              </div>
              <div>
                  <label className="block text-sm font-medium text-gray-300">Настроение</label>
                  <select value={mood} onChange={e => setMood(e.target.value)} className="mt-1 block w-full bg-gray-700 border border-gray-600 rounded-md shadow-sm py-2 px-3 text-white focus:outline-none focus:ring-indigo-500 focus:border-indigo-500">
                      <option>Happy</option><option>Sad</option><option>Energetic</option><option>Calm</option><option>Romantic</option>
                  </select>
              </div>
              <div>
                  <label className="block text-sm font-medium text-gray-300">Пол вокалиста</label>
                  <select value={gender} onChange={e => setGender(e.target.value)} className="mt-1 block w-full bg-gray-700 border border-gray-600 rounded-md shadow-sm py-2 px-3 text-white focus:outline-none focus:ring-indigo-500 focus:border-indigo-500">
                      <option>Male</option><option>Female</option>
                  </select>
              </div>
          </div>

          <div className="mt-6 flex flex-col items-center">
            <Button onClick={handleGenerate} disabled={isGenerating}>
                {isGenerating ? 'Генерация...' : '🎬 Генерировать песню'}
            </Button>
            {isGenerating && <p className="mt-2 text-sm text-indigo-400">Ожидаем ответ от сервера... (до 120 сек)</p>}
            {error && <p className="mt-4 text-red-400 text-center">{error}</p>}
          </div>
      </Card>
    </div>
  );
};

export default DiffRhythmGeneratorScreen;