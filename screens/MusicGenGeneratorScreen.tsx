const API_URL = 'http://localhost:8000';

// Fix: Create a placeholder screen component to resolve compilation errors.
import React, { useState } from 'react';
import { Button, Card, Slider } from '../components/common';
import { ArrowLeftIcon } from '../components/icons';
import { GeneratedTrack, GenerationModel, MusicGenParams } from '../types';
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
      return 'The generation took too long (over 2 minutes). Please try with shorter duration or try again.';
    case 'network_error':
      return 'Cannot reach the server. Please check your internet connection and try again.';
    case 'http_error':
      return detail || 'The server encountered an error. Please try again in a moment.';
    default:
      return detail || 'An unexpected error occurred. Please try again.';
  }
}

const MusicGenGeneratorScreen: React.FC<GeneratorScreenProps> = ({ onBack, onGenerationComplete }) => {
    const [params, setParams] = useState<MusicGenParams>({
        prompt: 'lo-fi hip hop with piano and rain sounds, chill vibes, relaxing background music',
        duration: 30,
        guidance_scale: 3.0,
        temperature: 1.0,
        top_k: 250,
        top_p: 0.9,
    });
    const [isGenerating, setIsGenerating] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const handleGenerate = async () => {
        setIsGenerating(true);
        setError(null);
        
        try {
            console.log('Generating music with MusicGen...', params);

            const response = await fetch(`${API_URL}/api/generate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    model: 'musicgen',
                    ...params,
                }),
            });

            console.log('Response status:', response.status);

            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`API error ${response.status}: ${errorText}`);
            }

            const data = await response.json();
            console.log('Generated track:', data);

            const newTrack: GeneratedTrack = {
                id: data.track_id || new Date().toISOString(),
                name: params.prompt.substring(0, 30) + '...',
                model: GenerationModel.MUSICGEN,
                audioUrl: `${API_URL}${data.audio_url}`,
                duration: data.duration || params.duration,
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

    const updateParam = <K extends keyof MusicGenParams>(key: K, value: MusicGenParams[K]) => {
        setParams(prev => ({ ...prev, [key]: value }));
    };

    const getGenerationTime = (duration: number) => {
        return Math.ceil(duration * 0.7); // Approximate: ~0.7 seconds per second of audio on CPU
    };

    return (
    <div className="max-w-4xl mx-auto animate-fade-in">
      <Button variant="secondary" onClick={onBack} className="mb-4" disabled={isGenerating}>
        <ArrowLeftIcon />
        Назад к выбору модели
      </Button>
      <h2 className="text-3xl font-bold mb-6 text-center">MusicGen - Генератор инструментальной музыки 🎵</h2>
      <p className="text-center text-gray-400 mb-6">Модель: facebook/musicgen-small (300MB) | Режим: CPU</p>
      
      <Card className="space-y-6">
          <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">Описание музыки (на английском)</label>
              <textarea
                  value={params.prompt}
                  onChange={e => updateParam('prompt', e.target.value)}
                  className="w-full h-32 bg-gray-700 border border-gray-600 rounded-md shadow-sm p-3 text-white focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 font-mono text-sm"
                  placeholder="lo-fi hip hop with piano and rain sounds..."
                  disabled={isGenerating}
              />
              <p className="text-xs text-gray-500 mt-1">Опишите музыку, которую хотите сгенерировать. Используйте английский язык для лучших результатов.</p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <Slider 
                  label="Длительность" 
                  value={params.duration} 
                  min={5} 
                  max={60} 
                  step={5} 
                  onChange={e => updateParam('duration', +e.target.value)} 
                  hint={`${getGenerationTime(params.duration)} сек генерации`}
              />
              <Slider 
                  label="Guidance Scale" 
                  value={params.guidance_scale} 
                  min={1.0} 
                  max={15.0} 
                  step={0.5} 
                  onChange={e => updateParam('guidance_scale', +e.target.value)} 
                  hint="Выше = ближе к описанию"
              />
              <Slider 
                  label="Temperature" 
                  value={params.temperature} 
                  min={0.1} 
                  max={2.0} 
                  step={0.1} 
                  onChange={e => updateParam('temperature', +e.target.value)} 
                  hint="Выше = разнообразнее"
              />
              <Slider 
                  label="Top-K" 
                  value={params.top_k} 
                  min={50} 
                  max={500} 
                  step={50} 
                  onChange={e => updateParam('top_k', +e.target.value)} 
                  hint="Количество вариантов для выбора"
              />
              <Slider 
                  label="Top-P" 
                  value={params.top_p} 
                  min={0.0} 
                  max={1.0} 
                  step={0.05} 
                  onChange={e => updateParam('top_p', +e.target.value)} 
                  hint="0.9 = стандартное значение"
              />
          </div>

          <div className="bg-indigo-900/30 border border-indigo-500/50 rounded-md p-4">
              <h4 className="font-semibold text-indigo-300 mb-2">ℹ️ Информация о MusicGen</h4>
              <ul className="text-sm text-gray-300 space-y-1">
                  <li>✅ Генерирует инструментальную музыку</li>
                  <li>❌ НЕ генерирует вокал</li>
                  <li>📦 Модель: facebook/musicgen-small (300MB)</li>
                  <li>⏱️ Скорость: ~{getGenerationTime(params.duration)} секунд на CPU для {params.duration}с музыки</li>
                  <li>💡 Для вокала используйте Bark</li>
              </ul>
          </div>

          <div className="mt-6 flex flex-col items-center">
            <Button onClick={handleGenerate} disabled={isGenerating || !params.prompt.trim()}>
                {isGenerating ? `Генерация... (~${getGenerationTime(params.duration)} сек)` : '🎬 Генерировать музыку'}
            </Button>
            {isGenerating && (
                <div className="mt-4 text-center">
                    <p className="text-sm text-indigo-400">⏳ Идёт генерация музыки...</p>
                    <p className="text-xs text-gray-400 mt-2">На CPU это займёт примерно {getGenerationTime(params.duration)} секунд. Пожалуйста, подождите.</p>
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

export default MusicGenGeneratorScreen;