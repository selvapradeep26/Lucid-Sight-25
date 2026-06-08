const steps = [
  { n: 1, title: "Connect Your Camera", desc: "Use your existing webcam or connect a mobile device as a camera source." },
  { n: 2, title: "Configure Alerts", desc: "Choose how you want to receive notifications and provide your contact details." },
  { n: 3, title: "Activate Protection", desc: "Start detection and relax knowing your space is being monitored." },
];

export default function HowItWorks() {
  return (
    <section id="how-it-works" className="py-16 px-4 md:px-8 bg-slate-50">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-16">
          <h2 className="text-3xl font-bold mb-4">How LucidSight Works</h2>
          <p className="text-lg text-slate-600 max-w-2xl mx-auto">Simple setup, powerful protection in just a few steps</p>
        </div>

        <div className="grid md:grid-cols-3 gap-8 mb-12">
          {steps.map((s) => (
            <div key={s.n} className="text-center">
              <div className="bg-indigo-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl font-bold text-indigo-600">{s.n}</span>
              </div>
              <h3 className="text-xl font-bold mb-2">{s.title}</h3>
              <p className="text-slate-600">{s.desc}</p>
            </div>
          ))}
        </div>

        <div className="bg-white rounded-xl overflow-hidden shadow-lg max-w-4xl mx-auto p-6">
          <div className="flex items-center mb-4">
            <i className="fas fa-mobile-alt text-2xl text-indigo-600 mr-3"></i>
            <h3 className="text-xl font-bold">Using CamoStudio with LucidSight</h3>
          </div>
          <div className="camo-studio-guide p-5 rounded-lg mb-6">
            <h4 className="font-bold mb-3 text-indigo-700">Step-by-Step Setup Guide:</h4>
            <ol className="list-decimal list-inside space-y-3 text-slate-700">
              <li>Download and install CamoStudio on your mobile device from the App Store or Google Play</li>
              <li>Launch CamoStudio and follow the in-app setup instructions</li>
              <li>Connect your mobile device to the same network as your computer</li>
              <li>On your computer, open LucidSight and select "Mobile Camera"</li>
            </ol>
          </div>
        </div>
      </div>
    </section>
  );
}
