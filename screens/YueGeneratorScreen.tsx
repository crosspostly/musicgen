// Fix: Create a placeholder screen component to resolve compilation errors.
import React, { useState } from 'react';
import { Button, Card } from '../components/common';
import { ArrowLeftIcon } from '../components/icons';
import { GeneratedTrack, GenerationModel } from '../types';

interface GeneratorScreenProps {
  onBack: () => void;
  onGenerationComplete: (track: GeneratedTrack) => void;
}

const YueGeneratorScreen: React.FC<GeneratorScreenProps> = ({ onBack, onGenerationComplete }) => {
    const [lyrics, setLyrics] = useState('Verse 1:\nТвои слова как шёпот ветра\nНесут волшебство в ночах');
    const [genre, setGenre] = useState('Rock');
    const [mood, setMood] = useState('Melancholic');
    const [gender, setGender] = useState('Male');
    const [instruments, setInstruments] = useState(['Drums', 'Guitar', 'Bass']);
    const [isGenerating, setIsGenerating] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const handleInstrumentToggle = (instrument: string) => {
        setInstruments(prev => 
            prev.includes(instrument) 
                ? prev.filter(i => i !== instrument) 
                : [...prev, instrument]
        );
    };
    
    const handleGenerate = async () => {
        setIsGenerating(true);
        setError(null);
        try {
            const response = await fetch('/api/generate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    model: GenerationModel.YUE,
                    lyrics,
                    genre,
                    mood,
                    gender,
                    instruments,
                }),
            });

            if (!response.ok) {
                const errData = await response.json().catch(() => ({ message: 'Ошибка генерации. Сервер не отвечает.' }));
                throw new Error(errData.message || 'Произошла неизвестная ошибка');
            }

            const result = await response.json();

            const newTrack: GeneratedTrack = {
                id: new Date().toISOString(),
                name: lyrics.substring(0, 30).split('\n')[0] + '...',
                model: GenerationModel.YUE,
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

    const allInstruments = ['Drums', 'Guitar', 'Bass', 'Piano', 'Synth', 'Violin'];

    return (
    <div className="max-w-4xl mx-auto animate-fade-in">
      <Button variant="secondary" onClick={onBack} className="mb-4" disabled={isGenerating}>
        <ArrowLeftIcon />
        Назад к выбору модели
      </Button>
      <h2 className="text-3xl font-bold mb-6 text-center">Генератор песен (YuE)</h2>
      <Card className="space-y-6">
          <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">Лирика / Текст песни</label>
              <textarea
                  value={lyrics}
                  onChange={e => setLyrics(e.target.value)}
                  className="w-full h-32 bg-gray-700 border border-gray-600 rounded-md shadow-sm p-3 text-white focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 font-mono text-sm"
                  placeholder="Verse 1: ..."
              />
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
               <div>
                  <label className="block text-sm font-medium text-gray-300">Жанр</label>
                  <select value={genre} onChange={e => setGenre(e.target.value)} className="mt-1 block w-full bg-gray-700 border border-gray-600 rounded-md shadow-sm py-2 px-3 text-white focus:outline-none focus:ring-indigo-500 focus:border-indigo-500">
                      <option>Rock</option><option>Metal</option><option>Pop</option><option>Electronic</option><option>K-pop</option>
                  </select>
              </div>
              <div>
                  <label className="block text-sm font-medium text-gray-300">Настроение</label>
                  <select value={mood} onChange={e => setMood(e.target.value)} className="mt-1 block w-full bg-gray-700 border border-gray-600 rounded-md shadow-sm py-2 px-3 text-white focus:outline-none focus:ring-indigo-500 focus:border-indigo-500">
                      <option>Energetic</option><option>Aggressive</option><option>Melancholic</option><option>Calm</option><option>Happy</option>
                  </select>
              </div>
              <div>
                  <label className="block text-sm font-medium text-gray-300">Пол вокалиста</label>
                  <select value={gender} onChange={e => setGender(e.target.value)} className="mt-1 block w-full bg-gray-700 border border-gray-600 rounded-md shadow-sm py-2 px-3 text-white focus:outline-none focus:ring-indigo-500 focus:border-indigo-500">
                      <option>Male</option><option>Female</option>
                  </select>
              </div>
          </div>
          <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">Инструменты</label>
              <div className="flex flex-wrap gap-2">
                  {allInstruments.map(inst => (
                      <Button key={inst} variant={instruments.includes(inst) ? 'primary' : 'secondary'} onClick={() => handleInstrumentToggle(inst)}>{inst}</Button>
                  ))}
              </div>
          </div>
          <div className="mt-6 flex flex-col items-center">
            <Button onClick={handleGenerate} disabled={isGenerating}>
                {isGenerating ? 'Генерация...' : '🎬 Генерировать полную песню'}
            </Button>
            {isGenerating && <p className="mt-2 text-sm text-gray-400">Это может занять некоторое время... (~30-40 сек)</p>}
            {error && <p className="mt-4 text-red-400 text-center">{error}</p>}
          </div>
      </Card>
    </div>
  );
};

export default YueGeneratorScreen;