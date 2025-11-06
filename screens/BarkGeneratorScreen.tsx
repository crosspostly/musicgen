// Fix: Create a placeholder screen component to resolve compilation errors.
import React, { useState } from 'react';
import { Button, Card, Slider } from '../components/common';
import { ArrowLeftIcon } from '../components/icons';
import { GeneratedTrack, GenerationModel } from '../types';

interface GeneratorScreenProps {
  onBack: () => void;
  onGenerationComplete: (track: GeneratedTrack) => void;
}

const BarkGeneratorScreen: React.FC<GeneratorScreenProps> = ({ onBack, onGenerationComplete }) => {
    const [text, setText] = useState('[MAN] Привет, это моя новая песня!\n[WOMAN] [laughter] Хаха, мне нравится!\n[MAN SINGING] ♪ Я пою, но это не совсем настоящее пение ♪');
    const [voicePreset, setVoicePreset] = useState('v2/en_speaker_9');
    const [temperature, setTemperature] = useState(0.75);
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
                    model: GenerationModel.BARK,
                    text,
                    voice_preset: voicePreset,
                    temperature,
                }),
            });

            if (!response.ok) {
                const errData = await response.json().catch(() => ({ message: 'Ошибка генерации. Сервер не отвечает.' }));
                throw new Error(errData.message || 'Произошла неизвестная ошибка');
            }

            const result = await response.json();

            const newTrack: GeneratedTrack = {
                id: new Date().toISOString(),
                name: 'Bark Effect: ' + text.substring(0, 20) + '...',
                model: GenerationModel.BARK,
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
      <h2 className="text-3xl font-bold mb-6 text-center">Генератор голоса и речи (Bark)</h2>
      <Card className="space-y-6">
          <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">Текст (речь, пение или смешанное)</label>
              <textarea
                  value={text}
                  onChange={e => setText(e.target.value)}
                  className="w-full h-32 bg-gray-700 border border-gray-600 rounded-md shadow-sm p-3 text-white focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 font-mono text-sm"
                  placeholder="[MAN] Привет..."
              />
              <p className="text-xs text-gray-500 mt-1">Используйте теги: [laughter], [SINGING], [MAN], [WOMAN] и т.д.</p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                  <label className="block text-sm font-medium text-gray-300">Голосовой пресет</label>
                  <select value={voicePreset} onChange={e => setVoicePreset(e.target.value)} className="mt-1 block w-full bg-gray-700 border border-gray-600 rounded-md shadow-sm py-2 px-3 text-white focus:outline-none focus:ring-indigo-500 focus:border-indigo-500">
                      <option value="v2/en_speaker_9">Мужской глубокий</option>
                      <option value="v2/en_speaker_3">Мужской нейтральный</option>
                      <option value="v2/en_speaker_6">Женский нейтральный</option>
                      <option value="v2/en_speaker_0">Женский высокий</option>
                  </select>
              </div>
              <Slider label="Temperature" value={temperature} min={0} max={1.5} step={0.05} onChange={e => setTemperature(+e.target.value)} hint="Выше = вариативнее, Ниже = стабильнее"/>
          </div>

          <div className="mt-6 flex flex-col items-center">
            <Button onClick={handleGenerate} disabled={isGenerating}>
                {isGenerating ? 'Генерация...' : '🎙️ Генерировать голос'}
            </Button>
            {isGenerating && <p className="mt-2 text-sm text-gray-400">Ожидаем ответ от сервера...</p>}
            {error && <p className="mt-4 text-red-400 text-center">{error}</p>}
          </div>
      </Card>
    </div>
  );
};

export default BarkGeneratorScreen;