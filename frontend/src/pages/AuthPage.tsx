import { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { Card, CardContent, CardHeader, CardTitle, Button, Input } from '../components/ui';
import api from '../lib/api';
import { useNavigate } from 'react-router-dom';
import { Microscope } from 'lucide-react';

export default function AuthPage() {
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [error, setError] = useState('');
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    try {
      if (isLogin) {
        const { data } = await api.post('/auth/login', { email, password });
        login(data.access_token);
      } else {
        await api.post('/auth/register', { email, password, full_name: fullName });
        const { data } = await api.post('/auth/login', { email, password });
        login(data.access_token);
      }
      navigate('/dashboard');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'An error occurred');
    }
  };

  return (
    <div className="flex min-h-screen">
      {/* Left side branding */}
      <div className="hidden lg:flex w-1/2 bg-primary items-center justify-center p-12 text-primary-foreground">
        <div className="max-w-lg space-y-6">
          <div className="inline-flex items-center justify-center p-3 bg-white/10 rounded-2xl mb-4">
            <Microscope className="w-10 h-10" />
          </div>
          <h1 className="text-4xl font-bold tracking-tight">Research Copilot</h1>
          <p className="text-lg text-primary-foreground/80 leading-relaxed">
            Your AI-powered research assistant. Ingest papers, chat with your library, and generate autonomous deep literature reviews.
          </p>
        </div>
      </div>
      
      {/* Right side form */}
      <div className="flex-1 flex items-center justify-center bg-background p-8">
        <Card className="w-full max-w-md border-0 shadow-none lg:shadow-xl lg:border lg:rounded-2xl">
          <CardHeader className="space-y-2 text-center lg:text-left">
            <CardTitle className="text-3xl font-bold">{isLogin ? 'Welcome back' : 'Create an account'}</CardTitle>
            <p className="text-muted-foreground text-sm">
              {isLogin ? 'Enter your credentials to access your library' : 'Get started with Research Copilot'}
            </p>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              {!isLogin && (
                <div className="space-y-1">
                  <label className="text-sm font-medium">Full Name</label>
                  <Input placeholder="John Doe" value={fullName} onChange={e => setFullName(e.target.value)} />
                </div>
              )}
              <div className="space-y-1">
                <label className="text-sm font-medium">Email</label>
                <Input type="email" placeholder="name@example.com" value={email} onChange={e => setEmail(e.target.value)} required />
              </div>
              <div className="space-y-1">
                <label className="text-sm font-medium">Password</label>
                <Input type="password" placeholder="••••••••" value={password} onChange={e => setPassword(e.target.value)} required />
              </div>
              {error && <p className="text-destructive text-sm font-medium bg-destructive/10 p-3 rounded-md">{error}</p>}
              <Button type="submit" className="w-full h-12 text-base mt-2">{isLogin ? 'Sign In' : 'Sign Up'}</Button>
            </form>
            <div className="mt-6 text-center">
              <button onClick={() => setIsLogin(!isLogin)} className="text-sm text-muted-foreground hover:text-primary transition-colors">
                {isLogin ? "Don't have an account? Sign up" : 'Already have an account? Sign in'}
              </button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
