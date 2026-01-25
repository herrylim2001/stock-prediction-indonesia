'use client';

import { useState, useRef, useEffect } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { useRouter } from 'next/navigation';
import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { Card, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { api } from '@/lib/api';
import { formatCurrency, formatDuration } from '@/lib/utils';
import {
  Radio,
  Camera,
  Mic,
  Settings,
  FlipHorizontal,
  Eye,
  Gift,
  Clock,
  DollarSign,
  X,
  CheckCircle,
  AlertCircle,
} from 'lucide-react';

export default function HostLivePage() {
  const router = useRouter();
  const videoRef = useRef<HTMLVideoElement>(null);
  const [stream, setStream] = useState<MediaStream | null>(null);
  const [sessionTitle, setSessionTitle] = useState('');
  const [category, setCategory] = useState('');
  const [isLive, setIsLive] = useState(false);
  const [activeSessionId, setActiveSessionId] = useState<string | null>(null);
  const [duration, setDuration] = useState(0);
  const [cameraReady, setCameraReady] = useState(false);
  const [micReady, setMicReady] = useState(false);

  // Check for active session
  const { data: activeSession } = useQuery({
    queryKey: ['active-session'],
    queryFn: () => api.getActiveSession(),
    retry: false,
  });

  // Start session mutation
  const startMutation = useMutation({
    mutationFn: (data: { title: string; category?: string }) => api.startSession(data),
    onSuccess: (response) => {
      setActiveSessionId(response.session.id);
      setIsLive(true);
    },
  });

  // End session mutation
  const endMutation = useMutation({
    mutationFn: (id: string) => api.endSession(id),
    onSuccess: () => {
      setIsLive(false);
      setActiveSessionId(null);
      router.push('/host');
    },
  });

  // Initialize camera
  useEffect(() => {
    const initCamera = async () => {
      try {
        const mediaStream = await navigator.mediaDevices.getUserMedia({
          video: { width: 1280, height: 720 },
          audio: true,
        });
        setStream(mediaStream);
        if (videoRef.current) {
          videoRef.current.srcObject = mediaStream;
        }
        setCameraReady(true);
        setMicReady(true);
      } catch (err) {
        console.error('Failed to access camera:', err);
      }
    };
    initCamera();

    return () => {
      stream?.getTracks().forEach((track) => track.stop());
    };
  }, []);

  // Check for existing active session
  useEffect(() => {
    if (activeSession?.session) {
      setActiveSessionId(activeSession.session.id);
      setIsLive(true);
      setSessionTitle(activeSession.session.title);
    }
  }, [activeSession]);

  // Duration timer
  useEffect(() => {
    if (!isLive) return;
    const interval = setInterval(() => {
      setDuration((d) => d + 1);
    }, 1000);
    return () => clearInterval(interval);
  }, [isLive]);

  const handleStartLive = () => {
    if (!sessionTitle.trim()) {
      alert('Please enter a session title');
      return;
    }
    startMutation.mutate({ title: sessionTitle, category });
  };

  const handleEndLive = () => {
    if (activeSessionId && confirm('Are you sure you want to end this session?')) {
      endMutation.mutate(activeSessionId);
    }
  };

  // Mock live stats (in production, these would come from websocket)
  const liveStats = {
    viewers: 1234,
    earnings: 156.5,
    gifts: 45,
  };

  return (
    <DashboardLayout requiredRole="host">
      <div className="max-w-6xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">
              {isLive ? 'You are LIVE' : 'Go Live'}
            </h1>
            <p className="text-gray-500">
              {isLive ? 'Your stream is now broadcasting' : 'Set up your stream and go live'}
            </p>
          </div>
          {isLive && (
            <div className="flex items-center space-x-2">
              <span className="flex items-center px-3 py-1.5 bg-red-100 text-red-700 rounded-full animate-pulse">
                <Radio className="w-4 h-4 mr-2" />
                LIVE
              </span>
            </div>
          )}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Video Preview */}
          <div className="lg:col-span-2">
            <Card>
              <CardContent className="p-0">
                <div className="relative aspect-video bg-black rounded-t-xl overflow-hidden">
                  <video
                    ref={videoRef}
                    autoPlay
                    muted
                    playsInline
                    className="w-full h-full object-cover"
                  />

                  {/* Live overlay */}
                  {isLive && (
                    <div className="absolute top-4 left-4 right-4 flex items-center justify-between">
                      <div className="flex items-center space-x-3">
                        <span className="px-2 py-1 bg-red-600 text-white text-sm font-medium rounded">
                          LIVE
                        </span>
                        <span className="px-2 py-1 bg-black/50 text-white text-sm rounded flex items-center">
                          <Clock className="w-4 h-4 mr-1" />
                          {formatDuration(duration)}
                        </span>
                      </div>
                      <span className="px-2 py-1 bg-black/50 text-white text-sm rounded flex items-center">
                        <Eye className="w-4 h-4 mr-1" />
                        {liveStats.viewers.toLocaleString()}
                      </span>
                    </div>
                  )}

                  {/* Gift notification area */}
                  {isLive && (
                    <div className="absolute bottom-4 left-4 right-4">
                      <div className="bg-gradient-to-r from-yellow-400 to-orange-500 text-white px-4 py-2 rounded-lg animate-slide-up">
                        <Gift className="w-4 h-4 inline mr-2" />
                        <span className="font-medium">@viewer123</span> sent 5x Rose
                      </div>
                    </div>
                  )}
                </div>

                {/* Controls */}
                <div className="p-4 flex items-center justify-between border-t border-gray-200">
                  <div className="flex items-center space-x-2">
                    <Button variant="ghost" size="sm">
                      <Camera className="w-5 h-5" />
                    </Button>
                    <Button variant="ghost" size="sm">
                      <Mic className="w-5 h-5" />
                    </Button>
                    <Button variant="ghost" size="sm">
                      <FlipHorizontal className="w-5 h-5" />
                    </Button>
                    <Button variant="ghost" size="sm">
                      <Settings className="w-5 h-5" />
                    </Button>
                  </div>

                  {isLive ? (
                    <Button
                      variant="danger"
                      onClick={handleEndLive}
                      loading={endMutation.isPending}
                    >
                      End Stream
                    </Button>
                  ) : (
                    <Button
                      onClick={handleStartLive}
                      loading={startMutation.isPending}
                      disabled={!cameraReady || !sessionTitle.trim()}
                    >
                      <Radio className="w-4 h-4 mr-2" />
                      Start Live
                    </Button>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Session Setup / Stats */}
            <Card>
              <CardContent className="p-6 space-y-4">
                {!isLive ? (
                  <>
                    <h3 className="font-semibold text-gray-900">Session Setup</h3>
                    <Input
                      label="Session Title"
                      value={sessionTitle}
                      onChange={(e) => setSessionTitle(e.target.value)}
                      placeholder="What's your stream about?"
                    />
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Category
                      </label>
                      <select
                        value={category}
                        onChange={(e) => setCategory(e.target.value)}
                        className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm"
                      >
                        <option value="">Select category</option>
                        <option value="gaming">Gaming</option>
                        <option value="music">Music</option>
                        <option value="talk">Talk Show</option>
                        <option value="lifestyle">Lifestyle</option>
                        <option value="other">Other</option>
                      </select>
                    </div>
                  </>
                ) : (
                  <>
                    <h3 className="font-semibold text-gray-900">Live Stats</h3>
                    <div className="space-y-3">
                      <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                        <span className="flex items-center text-gray-600">
                          <Eye className="w-4 h-4 mr-2" />
                          Viewers
                        </span>
                        <span className="font-semibold">{liveStats.viewers.toLocaleString()}</span>
                      </div>
                      <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                        <span className="flex items-center text-gray-600">
                          <Gift className="w-4 h-4 mr-2" />
                          Gifts
                        </span>
                        <span className="font-semibold">{liveStats.gifts}</span>
                      </div>
                      <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                        <span className="flex items-center text-green-700">
                          <DollarSign className="w-4 h-4 mr-2" />
                          Earnings
                        </span>
                        <span className="font-semibold text-green-700">
                          {formatCurrency(liveStats.earnings)}
                        </span>
                      </div>
                    </div>
                  </>
                )}
              </CardContent>
            </Card>

            {/* Equipment Check */}
            <Card>
              <CardContent className="p-6">
                <h3 className="font-semibold text-gray-900 mb-4">Equipment Check</h3>
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="flex items-center text-gray-600">
                      <Camera className="w-4 h-4 mr-2" />
                      Camera
                    </span>
                    {cameraReady ? (
                      <span className="flex items-center text-green-600">
                        <CheckCircle className="w-4 h-4 mr-1" />
                        Ready
                      </span>
                    ) : (
                      <span className="flex items-center text-yellow-600">
                        <AlertCircle className="w-4 h-4 mr-1" />
                        Connecting...
                      </span>
                    )}
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="flex items-center text-gray-600">
                      <Mic className="w-4 h-4 mr-2" />
                      Microphone
                    </span>
                    {micReady ? (
                      <span className="flex items-center text-green-600">
                        <CheckCircle className="w-4 h-4 mr-1" />
                        Ready
                      </span>
                    ) : (
                      <span className="flex items-center text-yellow-600">
                        <AlertCircle className="w-4 h-4 mr-1" />
                        Connecting...
                      </span>
                    )}
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="flex items-center text-gray-600">
                      <Radio className="w-4 h-4 mr-2" />
                      Connection
                    </span>
                    <span className="flex items-center text-green-600">
                      <CheckCircle className="w-4 h-4 mr-1" />
                      Good
                    </span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}
