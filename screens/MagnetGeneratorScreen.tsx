// Fix: Create a placeholder screen component to resolve compilation errors.
import React, { useState } from 'react';
import { Button, Card, Slider } from '../components/common';
import { ArrowLeftIcon } from '../components/icons';
import { GeneratedTrack, GenerationModel } from '../types';

interface GeneratorScreenProps {
  onBack: () => void;
  onGenerationComplete: (track: GeneratedTrack) => void;
}

const MagnetGeneratorScreen: React.FC<GeneratorScreenProps> = ({ onBack, onGenerationComplete }) => {
    const [prompt, setPrompt] = useState('Deep electronic ambient, медленно развивающиеся текстуры');
    const [temperature, setTemperature] = useState(3.0);
    const [maxCfg, setMaxCfg] = useState(10);
    const [isGenerating, setIsGenerating] = useState(false);
    const [error, setError] = useState<string | null>(null);
    
    const handleGenerate = async () => {
        setIsGenerating(true);
        setError(null);
        try {
            const response = await fetch('/api/generate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    model: GenerationModel.MAGNET,
                    prompt,
                    temperature,
                    max_cfg: maxCfg,
                }),
            });

            if (!response.ok) {
                const errData = await response.json().catch(() => ({ message: 'Ошибка генерации. Сервер не отвечает.' }));
                throw new Error(errData.message || 'Произошла неизвестная ошибка');
            }

            const result = await response.json();

            const newTrack: GeneratedTrack = {
                id: new Date().toISOString(),
                name: prompt.substring(0, 30) + '...',
                model: GenerationModel.MAGNET,
                audioUrl: result.audioUrl,
                duration: result.duration,
                createdAt: new Date(),
            };
            onGenerationComplete(newTrack);

        } catch (e: any) {
            setError(e.message);
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
      <h2 className="text-3xl font-bold mb-6 text-center">Генератор музыки (MAGNeT)</h2>
      <Card className="space-y-6">
          <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">Описание музыки</label>
              <textarea
                  value={prompt}
                  onChange={e => setPrompt(e.target.value)}
                  className="w-full bg-gray-700 border border-gray-600 rounded-md shadow-sm p-2 text-white focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                  rows={3}
                  placeholder="Deep electronic ambient..."
              />
              <p className="text-xs text-gray-500 mt-1">Подсказка: опишите жанр, инструменты, темп, настроение</p>
          </div>
          <Slider label="Temperature (Творческость)" value={temperature} min={2.0} max={4.0} step={0.1} onChange={e => setTemperature(+e.target.value)} hint="2.5=стабильно, 3.0=рекомендуется, 3.5=творчески" />
          <Slider label="Max CFG (Следование тексту)" value={maxCfg} min={5} max={20} step={1} onChange={e => setMaxCfg(+e.target.value)} hint="10=баланс, 15+=точнее, 8>=творчество" />
          
          <div className="mt-6 flex flex-col items-center">
            <Button onClick={handleGenerate} disabled={isGenerating}>
                {isGenerating ? 'Генерация...' : '🎵 Генерировать трек'}
            </Button>
            {isGenerating && <p className="mt-2 text-sm text-gray-400">Это может занять некоторое время...</p>}
            {error && <p className="mt-4 text-red-400 text-center">{error}</p>}
          </div>
      </Card>
    </div>
  );
};

export default MagnetGeneratorScreen;