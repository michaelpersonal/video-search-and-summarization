import React, { useRef, useState, useCallback } from 'react';
import './CameraCapture.css';

interface CameraCaptureProps {
  onImageCapture: (file: File) => void;
  onError: (error: string) => void;
}

const CameraCapture: React.FC<CameraCaptureProps> = ({ onImageCapture, onError }) => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [isStreaming, setIsStreaming] = useState(false);
  const [isCapturing, setIsCapturing] = useState(false);
  const [isVideoReady, setIsVideoReady] = useState(false);
  const [stream, setStream] = useState<MediaStream | null>(null);

  const startCamera = useCallback(async () => {
    console.log('🔍 Starting camera...');
    console.log('📍 Current URL:', window.location.href);
    console.log('🔒 Secure context:', window.isSecureContext);
    console.log('📱 MediaDevices available:', !!navigator.mediaDevices);
    console.log('🎥 Video ref exists:', !!videoRef.current);

    try {
      console.log('🎥 Requesting camera permissions...');
      // Try with simple constraints first, fallback to basic if fails
      let mediaStream;
      try {
        // Try with ideal resolution first
        mediaStream = await navigator.mediaDevices.getUserMedia({
          video: {
            width: { ideal: 1920 },
            height: { ideal: 1080 }
          }
        });
      } catch (err) {
        console.log('⚠️ Constrained camera failed, trying basic camera access...');
        console.log('⚠️ Error:', err);
        // Fallback to simplest possible constraints (works with any camera)
        mediaStream = await navigator.mediaDevices.getUserMedia({
          video: true
        });
      }

      console.log('✅ Camera stream obtained:', mediaStream);
      setStream(mediaStream);
      
      if (videoRef.current) {
        videoRef.current.srcObject = mediaStream;
        setIsStreaming(true);
        setIsVideoReady(false);
        console.log('🎬 Video element updated, streaming should start');
        
        // Wait for video to be ready
        videoRef.current.addEventListener('loadeddata', () => {
          console.log('✅ Video data loaded and ready');
          setIsVideoReady(true);
        }, { once: true });
      } else {
        console.error('❌ Video ref is still null');
        // Stop the stream since we can't use it
        mediaStream.getTracks().forEach(track => track.stop());
        onError('Video element not ready. Please try again.');
      }
    } catch (error: any) {
      console.error('❌ Error accessing camera:', error);
      console.error('❌ Error name:', error.name);
      console.error('❌ Error message:', error.message);
      
      let errorMessage = 'Unable to access camera. Please check permissions.';
      
      if (error.name === 'NotAllowedError') {
        errorMessage = 'Camera permission denied. Please allow camera access in your browser settings.';
      } else if (error.name === 'NotFoundError') {
        errorMessage = 'No camera found on this device.';
      } else if (error.name === 'NotSupportedError') {
        errorMessage = 'Camera not supported in this browser.';
      } else if (error.name === 'NotReadableError') {
        errorMessage = 'Camera is already in use by another application.';
      }
      
      onError(errorMessage);
    }
  }, [onError]);

  const stopCamera = useCallback(() => {
    if (stream) {
      stream.getTracks().forEach(track => track.stop());
      setStream(null);
    }
    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }
    setIsStreaming(false);
    setIsVideoReady(false);
  }, [stream]);

  const takePhoto = useCallback(() => {
    if (!videoRef.current || !canvasRef.current || isCapturing || !stream) return;

    setIsCapturing(true);
    console.log('📸 Taking photo...');
    
    const video = videoRef.current;
    const canvas = canvasRef.current;
    const context = canvas.getContext('2d');

    if (context) {
      // Wait for video to be ready
      if (video.readyState < 2) { // HAVE_CURRENT_DATA
        console.log('⏳ Video not ready, waiting...');
        video.addEventListener('loadeddata', () => {
          takePhoto();
        }, { once: true });
        setIsCapturing(false);
        return;
      }

      // Get actual video dimensions
      const videoWidth = video.videoWidth;
      const videoHeight = video.videoHeight;
      
      console.log(`📐 Video dimensions: ${videoWidth}x${videoHeight}`);
      
      if (videoWidth === 0 || videoHeight === 0) {
        console.error('❌ Video dimensions are zero');
        setIsCapturing(false);
        onError('Video not ready. Please try again.');
        return;
      }

      // Set canvas size to match video
      canvas.width = videoWidth;
      canvas.height = videoHeight;

      // Draw video frame to canvas
      context.drawImage(video, 0, 0, canvas.width, canvas.height);

      // Convert canvas to blob with higher quality
      canvas.toBlob((blob) => {
        if (blob) {
          console.log(`📦 Blob size: ${blob.size} bytes`);
          console.log(`📐 Canvas dimensions: ${canvas.width}x${canvas.height}`);
          console.log(`🎥 Video dimensions: ${videoWidth}x${videoHeight}`);
          
          // Create a temporary URL to inspect the image
          const url = URL.createObjectURL(blob);
          console.log(`🔗 Temporary image URL: ${url}`);
          
          const file = new File([blob], `capture_${Date.now()}.jpg`, {
            type: 'image/jpeg'
          });
          console.log('✅ Photo captured, processing...');
          console.log('📁 File details:', {
            name: file.name,
            size: file.size,
            type: file.type,
            lastModified: file.lastModified
          });
          
          onImageCapture(file);
          
          // Stop camera after taking photo
          stopCamera();
        } else {
          console.error('❌ Failed to create blob');
          onError('Failed to capture photo. Please try again.');
        }
        setIsCapturing(false);
      }, 'image/jpeg', 0.95); // Increased quality to 95%
    } else {
      setIsCapturing(false);
      onError('Failed to capture photo. Please try again.');
    }
  }, [onImageCapture, onError, isCapturing, stream, stopCamera]);

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file && file.type.startsWith('image/')) {
      console.log('📁 File upload selected:', {
        name: file.name,
        size: file.size,
        type: file.type,
        lastModified: file.lastModified
      });
      onImageCapture(file);
    } else {
      onError('Please select a valid image file.');
    }
  };

  return (
    <div className="camera-capture">
      <div className="camera-container">
        {!isStreaming ? (
          <div className="camera-placeholder">
            <div className="camera-icon">📷</div>
            <p>Camera not active</p>
            <button 
              onClick={startCamera}
              className="btn btn-primary"
            >
              Start Camera
            </button>
          </div>
        ) : (
          <div className="video-container">
            <div className="camera-controls">
              <button
                onClick={takePhoto}
                disabled={isCapturing || !isVideoReady}
                className="btn btn-capture"
              >
                {isCapturing ? '📸 Taking Photo...' : 
                 !isVideoReady ? '⏳ Loading Camera...' : '📸 Take Photo'}
              </button>
              <button
                onClick={stopCamera}
                className="btn btn-secondary"
              >
                Cancel
              </button>
            </div>
            <p className="camera-instruction">
              {!isVideoReady ? 'Camera is loading...' : 'Position your object in the camera view and click "Take Photo"'}
            </p>
          </div>
        )}
        
        {/* Always render video element but hide when not streaming */}
        <video
          ref={videoRef}
          autoPlay
          playsInline
          muted
          className="camera-video"
          style={{ 
            display: isStreaming ? 'block' : 'none',
            width: '100%',
            maxWidth: '100%',
            borderRadius: '8px'
          }}
        />
        <canvas
          ref={canvasRef}
          style={{ display: 'none' }}
        />
      </div>

      <div className="upload-section">
        <p>Or upload an image:</p>
        <input
          type="file"
          accept="image/*"
          onChange={handleFileUpload}
          className="file-input"
        />
      </div>
    </div>
  );
};

export default CameraCapture; 