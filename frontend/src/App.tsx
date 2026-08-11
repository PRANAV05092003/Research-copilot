import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import Layout from './components/Layout';
import AuthPage from './pages/AuthPage';
import Dashboard from './pages/Dashboard';
import SearchPage from './pages/SearchPage';
import ChatPage from './pages/ChatPage';
import ResearchPage from './pages/ResearchPage';
import LibraryPage from './pages/LibraryPage';
import ComparePage from './pages/ComparePage';
import GapAnalysisPage from './pages/GapAnalysisPage';
import SettingsPage from './pages/SettingsPage';

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<AuthPage />} />
          <Route path="/" element={<Layout />}>
            <Route index element={<Navigate to="/dashboard" replace />} />
            <Route path="dashboard" element={<Dashboard />} />
            <Route path="library" element={<LibraryPage />} />
            <Route path="search" element={<SearchPage />} />
            <Route path="chat" element={<ChatPage />} />
            <Route path="research" element={<ResearchPage />} />
            <Route path="compare" element={<ComparePage />} />
            <Route path="gap-analysis" element={<GapAnalysisPage />} />
            <Route path="settings" element={<SettingsPage />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
