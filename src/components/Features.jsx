const features = [
  { icon: "fa-bell", title: "Instant Alerts", desc: "Get notified immediately via WhatsApp or email when human presence is detected in your monitored area." },
  { icon: "fa-brain", title: "Smart AI Detection", desc: "Our advanced algorithms distinguish humans from pets, shadows, and other false triggers with 98% accuracy." },
  { icon: "fa-history", title: "24/7 Monitoring", desc: "Works day and night with low-light optimization to protect your property around the clock." },
];

export default function Features() {
  return (
    <section id="features" className="py-16 px-4 md:px-8 bg-white">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-16">
          <h2 className="text-3xl font-bold mb-4">Advanced Security Features</h2>
          <p className="text-lg text-slate-600 max-w-2xl mx-auto">LucidSight combines cutting-edge AI with simple setup for comprehensive protection</p>
        </div>
        <div className="grid md:grid-cols-3 gap-8">
          {features.map((f) => (
            <div key={f.title} className="card p-8 rounded-xl">
              <div className="feature-icon text-5xl mb-6"><i className={`fas ${f.icon}`}></i></div>
              <h3 className="text-xl font-bold mb-3">{f.title}</h3>
              <p className="text-slate-600">{f.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
