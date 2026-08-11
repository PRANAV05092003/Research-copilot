import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle, Button, Input } from '../components/ui';
import { useAuth } from '../context/AuthContext';
import { Settings, User as UserIcon, Shield } from 'lucide-react';

export default function SettingsPage() {
  const { user } = useAuth();
  const [name, setName] = useState(user?.full_name || '');
  const [email, setEmail] = useState(user?.email || '');

  return (
    <div className="p-8 space-y-6 max-w-4xl mx-auto">
      <div className="flex items-center space-x-3 mb-6">
        <Settings className="w-8 h-8 text-primary" />
        <h1 className="text-3xl font-bold">Settings</h1>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="col-span-1 md:col-span-1 space-y-2">
          <Button variant="ghost" className="w-full justify-start font-medium bg-muted">
            <UserIcon className="mr-2 w-4 h-4" /> Profile
          </Button>
          <Button variant="ghost" className="w-full justify-start font-medium text-muted-foreground hover:bg-muted/50">
            <Shield className="mr-2 w-4 h-4" /> Security
          </Button>
        </div>
        
        <div className="col-span-1 md:col-span-2 space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Profile Details</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-1">
                <label className="text-sm font-medium">Full Name</label>
                <Input value={name} onChange={e => setName(e.target.value)} />
              </div>
              <div className="space-y-1">
                <label className="text-sm font-medium">Email</label>
                <Input value={email} onChange={e => setEmail(e.target.value)} disabled />
              </div>
              <Button>Save Changes</Button>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
