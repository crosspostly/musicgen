// Fix: Create a placeholder screen component to resolve compilation errors.
import React, { useState } from 'react';
import { Button, Card, Slider } from '../components/common';
import { ArrowLeftIcon } from '../components/icons';
import { GeneratedTrack, GenerationModel } from '../types';

interface GeneratorScreenProps {
  onBack: () => void;
  onGenerationComplete: (track: GeneratedTrack) => void;
}

const LyriaGeneratorScreen: React.FC<GeneratorScreenProps> = ({ onBack, onGenerationComplete }) => {
    const [prompt, setPrompt] = useState('Lo-fi hip hop beat с мягким пианино и джазовыми аккордами');
    const [bpm, setBpm] = useState(80);
    const [brightness, setBrightness] = useState(0.6);
    const [density, setDensity] = useState(0.7);
    const [isGenerating, setIsGenerating] = useState(false);
    const [error, setError] = useState<string | null>(null);
    
    const handleGenerate = async () => {
        setIsGenerating(true);
        setError(null);
        try {
            // This is now a real API call to a backend endpoint.
            // The backend would handle the actual generation with the Lyria model.
            const response = await fetch('/api/generate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    model: GenerationModel.LYRIA,
                    prompt,
                    bpm,
                    brightness,
                    density,
                    duration: 30, // Example duration
                }),
            });

            if (!response.ok) {
                // In a real app, the backend would return a more specific error.
                // For demonstration, we assume a JSON error response.
                const errData = await response.json().catch(() => ({ message: 'Ошибка генерации. Сервер не отвечает.' }));
                throw new Error(errData.message || 'Произошла неизвестная ошибка');
            }

            const result = await response.json(); // Expects { audioUrl: string, duration: number }

            const newTrack: GeneratedTrack = {
                id: new Date().toISOString(),
                name: prompt.substring(0, 30) + '...', // Generate a temporary name
                model: GenerationModel.LYRIA,
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
      <h2 className="text-3xl font-bold mb-6 text-center">Генератор музыки (Lyria)</h2>
      <Card className="space-y-6">
          <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">Описание музыки</label>
              <textarea
                  value={prompt}
                  onChange={e => setPrompt(e.target.value)}
                  className="w-full bg-gray-700 border border-gray-600 rounded-md shadow-sm p-2 text-white focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                  rows={3}
                  placeholder="Lo-fi hip hop beat..."
              />
              <p className="text-xs text-gray-500 mt-1">Подсказка: минимум 10 слов, 5-500 символов</p>
          </div>
          
          <Slider label="BPM (Tempo)" value={bpm} min={60} max={200} step={1} onChange={e => setBpm(+e.target.value)} hint="Темп музыки. Рок=120-140, Lo-fi=70-90, Techno=120-140" unit="BPM"/>
          <Slider label="Brightness (Яркость)" value={brightness} min={0} max={1} step={0.05} onChange={e => setBrightness(+e.target.value)} hint="Яркость звучания. 0.1=темное/драмматичное, 0.9=яркое/энергичное" valueLabel={brightness < 0.5 ? 'Темное' : 'Яркое'}/>
          <Slider label="Density (Плотность нот)" value={density} min={0} max={1} step={0.05} onChange={e => setDensity(+e.target.value)} hint="Количество нот. 0.1=минимально, 0.9=максимально плотно" valueLabel={density < 0.5 ? 'Редкие' : 'Много'}/>

          <div className="mt-6 flex flex-col items-center">
            <Button onClick={handleGenerate} disabled={isGenerating}>
                {isGenerating ? 'Генерация...' : '🎵 Начать генерацию'}
            </Button>
            {error && <p className="mt-4 text-red-400 text-center">{error}</p>}
          </div>
      </Card>
    </div>
  );
};

export default LyriaGeneratorScreen;