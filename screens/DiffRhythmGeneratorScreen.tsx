const API_URL = 'http://localhost:8000';

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
            // ИСПРАВЛЕНО: Прямой вызов API вместо apiClient
            console.log('Generating music...', { lyrics, genre, mood, gender });

            const response = await fetch(`${API_URL}/api/generate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    prompt: lyrics,
                    duration: 30,
                    // Опционально: можно добавить genre, mood, gender если backend поддерживает
                }),
            });

            console.log('Response status:', response.status);

            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`API error ${response.status}: ${errorText}`);
            }

            const data = await response.json();
            console.log('Generated track:', data);

            // ИСПРАВЛЕНО: Используем правильный формат ответа от backend
            const newTrack: GeneratedTrack = {
                id: data.track_id || new Date().toISOString(),
                name: lyrics.substring(0, 30).split('\n')[0] + '...',
                model: GenerationModel.DIFFRHYTHM,
                audioUrl: `${API_URL}${data.audio_url}`, // ИСПРАВЛЕНО: добавлен полный URL
                duration: data.duration || 0,
                createdAt: new Date(),
            };
            
            console.log('Track created:', newTrack);
            onGenerationComplete(newTrack);

        } catch (e: any) {
            const errorMessage = e?.message || 'An unexpected error occurred. Please try again.';
            setError(errorMessage);
            console.error('Generation error:', e);
            alert(`Ошибка генерации: ${errorMessage}`);
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
                  disabled={isGenerating}
              />
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                  <label className="block text-sm font-medium text-gray-300">Жанр</label>
                  <select 
                      value={genre} 
                      onChange={e => setGenre(e.target.value)} 
                      className="mt-1 block w-full bg-gray-700 border border-gray-600 rounded-md shadow-sm py-2 px-3 text-white focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                      disabled={isGenerating}
                  >
                      <option>Pop</option><option>Rock</option><option>Rap</option><option>Electronic</option><option>Jazz</option>
                  </select>
              </div>
              <div>
                  <label className="block text-sm font-medium text-gray-300">Настроение</label>
                  <select 
                      value={mood} 
                      onChange={e => setMood(e.target.value)} 
                      className="mt-1 block w-full bg-gray-700 border border-gray-600 rounded-md shadow-sm py-2 px-3 text-white focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                      disabled={isGenerating}
                  >
                      <option>Happy</option><option>Sad</option><option>Energetic</option><option>Calm</option><option>Romantic</option>
                  </select>
              </div>
              <div>
                  <label className="block text-sm font-medium text-gray-300">Пол вокалиста</label>
                  <select 
                      value={gender} 
                      onChange={e => setGender(e.target.value)} 
                      className="mt-1 block w-full bg-gray-700 border border-gray-600 rounded-md shadow-sm py-2 px-3 text-white focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                      disabled={isGenerating}
                  >
                      <option>Male</option><option>Female</option>
                  </select>
              </div>
          </div>

          <div className="mt-6 flex flex-col items-center">
            <Button onClick={handleGenerate} disabled={isGenerating}>
                {isGenerating ? 'Генерация... (может занять до 10 минут)' : '🎬 Генерировать песню'}
            </Button>
            {isGenerating && (
                <div className="mt-4 text-center">
                    <p className="text-sm text-indigo-400">⏳ Идёт генерация музыки...</p>
                    <p className="text-xs text-gray-400 mt-2">На CPU это может занять 5-10 минут. Пожалуйста, подождите.</p>
                </div>
            )}
            {error && (
                <div className="mt-4 p-4 bg-red-900/20 border border-red-500 rounded-md">
                    <p className="text-red-400 text-center">{error}</p>
                </div>
            )}
          </div>
      </Card>
    </div>
  );
};

export default DiffRhythmGeneratorScreen;