import { useRef, useState } from "react";

const startSoundUrl = "https://www.soundjay.com/buttons/sounds/button-3.mp3";

export default function Detection({ notify }) {
  const [method, setMethod] = useState("");
  const [contact, setContact] = useState("");
  const [active, setActive] = useState(false);
  const startSoundRef = useRef(null);
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const streamRef = useRef(null);
  const intervalRef = useRef(null);

  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: true,
        audio: false,
      });

      streamRef.current = stream;

      if (videoRef.current) {
        videoRef.current.srcObject = stream;
      }

      return true;
    } catch (error) {
      console.error("Camera access failed:", error);

      notify("Please allow camera access.", "error");

      return false;
    }
  };

  const sendFrame = () => {
    const video = videoRef.current;
    const canvas = canvasRef.current;

    if (!video || !canvas) return;
    if (video.readyState < 2) return;

    canvas.width = 640;
    canvas.height = 480;

    const context = canvas.getContext("2d");
    context.drawImage(video, 0, 0, 640, 480);

    canvas.toBlob(
      async (blob) => {
        if (!blob) return;

        const formData = new FormData();
        formData.append("frame", blob, "frame.jpg");

        try {
          const res = await fetch("/process_frame", {
            method: "POST",
            body: formData,
          });

          const data = await res.json().catch(() => null);

          if (!res.ok) {
            if (res.status === 400 && data?.error === "Detection is not active") {
              stopCameraAndFrames();
              setActive(false);
              notify("Detection is inactive on server. Please start detection again.", "error");
            }
            return;
          }

          if (data?.detected) {
            console.log("Human detected in current frame");
          }
        } catch (error) {
          console.error("Frame upload failed:", error);
        }
      },
      "image/jpeg",
      0.7
    );
  };

  const stopCameraAndFrames = () => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }

    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
    }

    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const formData = new FormData();
    formData.append("method", method);
    formData.append("contact", contact);

    try {
      const res = await fetch("/start_detection", { method: "POST", body: formData });
      const data = await res.json();
      if (res.ok && data.status) {
        setActive(true);

        const cameraStarted = await startCamera();

        if (!cameraStarted) {
          await fetch("/stop_detection", { method: "POST" });
          setActive(false);
          return;
        }

        intervalRef.current = setInterval(sendFrame, 500);

        startSoundRef.current?.play().catch(() => {});
        notify("Detection started successfully!", "success");
      } else {
        notify(data.error || "Failed to start detection. Please try again.", "error");
      }
    } catch {
      notify("Network error. Please check your connection.", "error");
    }
  };

  const handleStop = async () => {
    try {
      const res = await fetch("/stop_detection", { method: "POST" });
      const data = await res.json();
      if (res.ok && data.status) {
        stopCameraAndFrames();
        setActive(false);
        notify("Detection stopped successfully!", "success");
      } else {
        notify(data.error || "Failed to stop detection.", "error");
      }
    } catch {
      notify("Network error. Please check your connection.", "error");
    }
  };

  return (
    <section id="detection" className="py-16 px-4 md:px-8 bg-white">
      <div className="max-w-3xl mx-auto card p-8 rounded-xl">
        <div className="text-center mb-10">
          <h2 className="text-3xl font-bold mb-3">Start Human Detection</h2>
          <p className="text-lg text-slate-600">Configure your monitoring settings below</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-sm font-medium mb-2 text-slate-700">Alert Method</label>
            <div className="relative">
              <select
                required
                value={method}
                onChange={(e) => setMethod(e.target.value)}
                className="input-field w-full p-3 rounded-lg appearance-none"
              >
                <option value="">Select notification method</option>
                <option value="Email">Email Notification</option>
                <option value="Telegram">Telegram Bot</option>
              </select>
              <i className="fas fa-chevron-down absolute right-3 top-3.5 text-slate-400 pointer-events-none"></i>
            </div>
          </div>

          {method === "Email" && (
            <div>
              <label className="block text-sm font-medium mb-2 text-slate-700">Email Address</label>
              <input
                type="email"
                required
                value={contact}
                onChange={(e) => setContact(e.target.value)}
                placeholder="you@example.com"
                className="input-field w-full p-3 rounded-lg"
              />
            </div>
          )}

          {method === "Telegram" && (
            <div>
              <label className="block text-sm font-medium mb-2 text-slate-700">
                Telegram Chat ID
              </label>
              <input
                type="text"
                required
                inputMode="numeric"
                value={contact}
                onChange={(e) => setContact(e.target.value.trim())}
                placeholder="Example: 123456789"
                className="input-field w-full p-3 rounded-lg"
              />
              <p className="mt-2 text-sm text-slate-600">
                Open the shared bot in Telegram, tap Start, then enter your own chat ID.
                Alerts from this session will be sent only to that chat.
              </p>
            </div>
          )}

          <div className="pt-4">
            <video
              ref={videoRef}
              autoPlay
              playsInline
              muted
              className={`w-full rounded-lg mb-6 ${active ? "block" : "hidden"}`}
            />

            <canvas ref={canvasRef} className="hidden" />

            <div className="flex items-center justify-between bg-slate-100 rounded-lg px-4 py-3 mb-6">
              <div className="flex items-center">
                <span className={`status-indicator ${active ? "status-active" : "status-inactive"}`}></span>
                <span className="font-medium text-slate-700">
                  {active ? "Detection Active" : "Detection Inactive"}
                </span>
              </div>
            </div>

            <div className="flex flex-col sm:flex-row gap-4">
              <button
                type="submit"
                className="btn-primary flex-1 py-3 px-6 rounded-lg font-semibold text-white flex items-center justify-center"
              >
                <i className="fas fa-play mr-2"></i> Start Detection
              </button>
              <button
                type="button"
                onClick={handleStop}
                disabled={!active}
                className={`flex-1 py-3 px-6 rounded-lg font-semibold flex items-center justify-center ${
                  active
                    ? "bg-red-500 text-white hover:bg-red-600"
                    : "bg-slate-200 text-slate-600 opacity-70 cursor-not-allowed"
                }`}
              >
                <i className="fas fa-stop mr-2"></i> Stop
              </button>
            </div>
          </div>
        </form>

        <audio ref={startSoundRef} src={startSoundUrl}></audio>
      </div>
    </section>
  );
}
