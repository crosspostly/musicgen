// Fix: Create a placeholder screen component to resolve compilation errors.
import React, { useState } from 'react';
import { Button, Card, Slider } from '../components/common';
import { ArrowLeftIcon } from '../components/icons';
import { GeneratedTrack, GenerationModel, BarkParams } from '../types';

interface GeneratorScreenProps {
  onBack: () => void;
  onGenerationComplete: (track: GeneratedTrack) => void;
}

const BarkGeneratorScreen: React.FC<GeneratorScreenProps> = ({ onBack, onGenerationComplete }) => {
    const [params, setParams] = useState<BarkParams>({
        text: '[MAN] Привет, это моя новая песня!\n[WOMAN] [laughter] Хаха, мне нравится!\n[MAN SINGING] ♪ Я пою, но это не совсем настоящее пение ♪',
        voice_preset: 'v2/ru_speaker_0',
        language: 'ru',
        text_temp: 0.7,
        waveform_temp: 0.7,
    });
    const [isGenerating, setIsGenerating] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const handleGenerate = async () => {
        setIsGenerating(true);
        setError(null);
        try {
            const response = await fetch('http://localhost:8000/api/bark', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(params),
            });

            if (!response.ok) {
                const errData = await response.json().catch(() => ({ message: 'Ошибка генерации. Сервер не отвечает.' }));
                throw new Error(errData.message || 'Произошла неизвестная ошибка');
            }

            const result = await response.json();

            const newTrack: GeneratedTrack = {
                id: result.track_id || new Date().toISOString(),
                name: 'Bark: ' + params.text.substring(0, 20) + '...',
                model: GenerationModel.BARK,
                audioUrl: `http://localhost:8000${result.audio_url}`,
                duration: result.duration || 15,
                createdAt: new Date(),
            };
            onGenerationComplete(newTrack);
        } catch (e: any) {
            setError(e.message);
        } finally {
            setIsGenerating(false);
        }
    };

    const updateParam = <K extends keyof BarkParams>(key: K, value: BarkParams[K]) => {
        setParams(prev => ({ ...prev, [key]: value }));
    };

    const voicePresets = [
        { value: 'v2/ru_speaker_0', label: 'Русский женский 0' },
        { value: 'v2/ru_speaker_1', label: 'Русский женский 1' },
        { value: 'v2/ru_speaker_2', label: 'Русский женский 2' },
        { value: 'v2/ru_speaker_3', label: 'Русский женский 3' },
        { value: 'v2/ru_speaker_4', label: 'Русский мужской 0' },
        { value: 'v2/ru_speaker_5', label: 'Русский мужской 1' },
        { value: 'v2/ru_speaker_6', label: 'Русский мужской 2' },
        { value: 'v2/ru_speaker_7', label: 'Русский мужской 3' },
        { value: 'v2/en_speaker_0', label: 'English Female 0' },
        { value: 'v2/en_speaker_1', label: 'English Female 1' },
        { value: 'v2/en_speaker_2', label: 'English Female 2' },
        { value: 'v2/en_speaker_3', label: 'English Male 0' },
        { value: 'v2/en_speaker_4', label: 'English Male 1' },
        { value: 'v2/en_speaker_5', label: 'English Male 2' },
        { value: 'v2/en_speaker_6', label: 'English Male 3' },
        { value: 'v2/en_speaker_7', label: 'English Male 4' },
        { value: 'v2/en_speaker_8', label: 'English Male 5' },
        { value: 'v2/en_speaker_9', label: 'English Male 6' },
    ];

    const languages = [
        { value: 'ru', label: 'Русский' },
        { value: 'en', label: 'English' },
        { value: 'de', label: 'Deutsch' },
        { value: 'es', label: 'Español' },
        { value: 'fr', label: 'Français' },
        { value: 'it', label: 'Italiano' },
        { value: 'pt', label: 'Português' },
        { value: 'pl', label: 'Polski' },
        { value: 'nl', label: 'Nederlands' },
        { value: 'tr', label: 'Türkçe' },
    ];

    return (
    <div className="max-w-4xl mx-auto animate-fade-in">
      <Button variant="secondary" onClick={onBack} className="mb-4" disabled={isGenerating}>
        <ArrowLeftIcon />
        Назад к выбору модели
      </Button>
      <h2 className="text-3xl font-bold mb-6 text-center">Bark - Генератор голоса и речи 🎤</h2>
      <p className="text-center text-gray-400 mb-6">Модель: suno/bark (1.2GB) | Режим: CPU/GPU</p>
      
      <Card className="space-y-6">
          <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">Текст для озвучки</label>
              <textarea
                  value={params.text}
                  onChange={e => updateParam('text', e.target.value)}
                  className="w-full h-32 bg-gray-700 border border-gray-600 rounded-md shadow-sm p-3 text-white focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 font-mono text-sm"
                  placeholder="[MAN] Привет..."
                  maxLength={200}
                  disabled={isGenerating}
              />
              <p className="text-xs text-gray-500 mt-1">
                {params.text.length}/200 символов. Используйте теги: [laughter], [SINGING], [MAN], [WOMAN] и т.д.
              </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                  <label className="block text-sm font-medium text-gray-300">Голос (Voice Preset)</label>
                  <select 
                      value={params.voice_preset} 
                      onChange={e => updateParam('voice_preset', e.target.value)} 
                      className="mt-1 block w-full bg-gray-700 border border-gray-600 rounded-md shadow-sm py-2 px-3 text-white focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                      disabled={isGenerating}
                  >
                      <optgroup label="Русские голоса">
                          {voicePresets.filter(v => v.value.startsWith('v2/ru')).map(voice => (
                              <option key={voice.value} value={voice.value}>{voice.label}</option>
                          ))}
                      </optgroup>
                      <optgroup label="English voices">
                          {voicePresets.filter(v => v.value.startsWith('v2/en')).map(voice => (
                              <option key={voice.value} value={voice.value}>{voice.label}</option>
                          ))}
                      </optgroup>
                  </select>
              </div>
              <div>
                  <label className="block text-sm font-medium text-gray-300">Язык</label>
                  <select 
                      value={params.language} 
                      onChange={e => updateParam('language', e.target.value)} 
                      className="mt-1 block w-full bg-gray-700 border border-gray-600 rounded-md shadow-sm py-2 px-3 text-white focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                      disabled={isGenerating}
                  >
                      {languages.map(lang => (
                          <option key={lang.value} value={lang.value}>{lang.label}</option>
                      ))}
                  </select>
              </div>
              <Slider 
                  label="Text Temperature" 
                  value={params.text_temp} 
                  min={0.1} 
                  max={2.0} 
                  step={0.1} 
                  onChange={e => updateParam('text_temp', +e.target.value)} 
                  hint="Контролирует случайность в тексте"
              />
              <Slider 
                  label="Waveform Temperature" 
                  value={params.waveform_temp} 
                  min={0.1} 
                  max={2.0} 
                  step={0.1} 
                  onChange={e => updateParam('waveform_temp', +e.target.value)} 
                  hint="Контролирует случайность в аудио"
              />
          </div>

          <div className="bg-indigo-900/30 border border-indigo-500/50 rounded-md p-4">
              <h4 className="font-semibold text-indigo-300 mb-2">ℹ️ Информация о Bark</h4>
              <ul className="text-sm text-gray-300 space-y-1">
                  <li>📦 Модель: suno/bark (1.2GB)</li>
                  <li>🌍 Поддержка русского языка и 100+ голосов</li>
                  <li>⏱️ Скорость: ~30 секунд на сегмент</li>
                  <li>🎭 Особенности: смех, пение, шепот, эмоции</li>
                  <li>⚠️ Требуется установка backend для работы</li>
              </ul>
          </div>

          <div className="mt-6 flex flex-col items-center">
            <Button onClick={handleGenerate} disabled={isGenerating || !params.text.trim()}>
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