// Fix: Create the main App component to handle state and screen rendering.
import React, { useState } from 'react';
import { Screen, GenerationModel, GeneratedTrack } from './types';
import ModelSelectionScreen from './screens/ModelSelectionScreen';
import MusicGenGeneratorScreen from './screens/MusicGenGeneratorScreen';
import BarkGeneratorScreen from './screens/BarkGeneratorScreen';
import MetadataEditorScreen from './screens/MetadataEditorScreen';
import ExportScreen from './screens/ExportScreen';
import FreestyleScreen from './screens/FreestyleScreen';
import { GithubIcon } from './components/icons';

const App: React.FC = () => {
  const [currentScreen, setCurrentScreen] = useState<Screen>(Screen.MODEL_SELECTION);
  const [selectedModel, setSelectedModel] = useState<GenerationModel | null>(null);
  const [generatedTrack, setGeneratedTrack] = useState<GeneratedTrack | null>(null);

  const handleSelectModel = (model: GenerationModel) => {
    setSelectedModel(model);
    switch (model) {
      case GenerationModel.MUSICGEN:
        setCurrentScreen(Screen.MUSICGEN_GENERATOR);
        break;
      case GenerationModel.BARK:
        setCurrentScreen(Screen.BARK_GENERATOR);
        break;
    }
  };
  
  const handleNavigate = (screen: Screen) => {
      setCurrentScreen(screen);
  };
  
  const handleBackToSelection = () => {
      setCurrentScreen(Screen.MODEL_SELECTION);
      setSelectedModel(null);
      setGeneratedTrack(null);
  };
  
  const handleGenerationComplete = (track: GeneratedTrack) => {
      setGeneratedTrack(track);
      setCurrentScreen(Screen.METADATA_EDITOR);
  };
  
  const handleMetadataComplete = (track: GeneratedTrack) => {
      setGeneratedTrack(track);
      setCurrentScreen(Screen.EXPORT);
  };

  const renderScreen = () => {
      switch (currentScreen) {
        case Screen.MODEL_SELECTION:
          return <ModelSelectionScreen onSelectModel={handleSelectModel} onNavigate={handleNavigate} />;
        case Screen.FREESTYLE:
            return <FreestyleScreen onBack={handleBackToSelection} />;
        case Screen.MUSICGEN_GENERATOR:
          return <MusicGenGeneratorScreen onBack={handleBackToSelection} onGenerationComplete={handleGenerationComplete} />;
        case Screen.BARK_GENERATOR:
          return <BarkGeneratorScreen onBack={handleBackToSelection} onGenerationComplete={handleGenerationComplete} />;
        case Screen.METADATA_EDITOR:
          if (!generatedTrack) return <ModelSelectionScreen onSelectModel={handleSelectModel} onNavigate={handleNavigate} />; // Fallback
          return <MetadataEditorScreen track={generatedTrack} onBack={() => handleSelectModel(generatedTrack.model)} onComplete={handleMetadataComplete} />;
        case Screen.EXPORT:
          if (!generatedTrack) return <ModelSelectionScreen onSelectModel={handleSelectModel} onNavigate={handleNavigate} />; // Fallback
          return <ExportScreen track={generatedTrack} onDone={handleBackToSelection} />;
        default:
          return <ModelSelectionScreen onSelectModel={handleSelectModel} onNavigate={handleNavigate} />;
      }
    };

  return (
    <div className="bg-gray-900 text-white min-h-screen font-sans">
      <header className="py-4 border-b border-gray-800">
        <div className="container mx-auto px-4 flex justify-between items-center">
            <h1 className="text-2xl font-bold text-indigo-400">MeloGen AI</h1>
            <a href="https://github.com/example/melogen-ai" target="_blank" rel="noopener noreferrer" className="text-gray-400 hover:text-white transition-colors">
                <GithubIcon className="w-6 h-6" />
            </a>
        </div>
      </header>
      <main className="container mx-auto px-4 py-8 md:py-12">
        {renderScreen()}
      </main>
      <footer className="text-center py-6 text-gray-500 text-sm border-t border-gray-800 mt-12">
        <p>Crafted with AI & Passion for Music</p>
      </footer>
    </div>
  );
};

export default App;
